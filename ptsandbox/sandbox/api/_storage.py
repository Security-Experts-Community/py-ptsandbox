import asyncio
from collections.abc import AsyncIterator, Generator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import attr

from ptsandbox.exceptions import SandboxException
from ptsandbox.models import SandboxUploadScanFileResponse
from ptsandbox.sandbox.base import BaseSandboxClient


class StorageMixin(BaseSandboxClient):
    upload_semaphore: asyncio.Semaphore

    async def _upload_bytes(self, file: BinaryIO) -> AsyncIterator[bytes]:
        while chunk := file.read(1024 * 1024):
            yield chunk

    @contextmanager
    def _file_payload(self, file: str | Path | bytes | BinaryIO) -> Generator[Any, None, None]:
        """
        Convert a file argument into a data payload suitable for aiohttp POST.

        For str/Path the file is opened and closed automatically; for bytes
        the raw bytes are yielded; for BytesIO/BinaryIO a chunked async
        generator is yielded.
        """
        match file:
            case str() | Path():
                # we can't use aiofiles here, because aiohttp try use chunked encoding
                # sandbox (or maybe aiohttp) can't correctly handle chunked encoding
                # so we need this clunky code
                with open(file, "rb") as fd:
                    yield fd
            case bytes():
                yield file
            case BytesIO():
                yield self._upload_bytes(file)
            case _:
                raise SandboxException(f"Specified file type doesn't supported {type(file)}!")

    async def upload_file(
        self,
        file: str | Path | bytes | BinaryIO,
        upload_timeout: float = 300,
    ) -> SandboxUploadScanFileResponse:
        """
        Uploads the file to the sandbox

        Args:
            file: a path in the form of a string, either a Path object or binary data
            upload_timeout: if a large enough file is being uploaded, increase timeout (in seconds).

        Returns:
            The link to the file in the temporary storage and the lifetime of this file are returned, or an exception is thrown.

        Raises:
            SandboxException: if incorrect arguments are passed (usually when ignoring type hints)
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        # update default timeout
        timeout = attr.evolve(self.default_timeout, total=upload_timeout)

        url = f"{self.key.url}/storage/uploadScanFile"

        async with self.upload_semaphore:
            with self._file_payload(file) as payload:
                return await self._request(
                    "POST",
                    url,
                    response_model=SandboxUploadScanFileResponse,
                    data=payload,
                    timeout=timeout,
                )

    async def download_artifact(self, file_uri: str, read_timeout: int = 120) -> bytes:
        """
        Download file from the sandbox by hash

        Args:
            file_uri: id of the file in the sandbox
            read_timeout: how long should I wait for the file to download?

        Returns:
            File data

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status (404 if the file is not found)
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        timeout = attr.evolve(self.default_timeout, sock_read=read_timeout)

        async with self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            json={"file_uri": file_uri},
            timeout=timeout,
        ) as response:
            return await response.read()  # type: ignore

    async def download_artifact_stream(self, file_uri: str, read_timeout: int = 120) -> AsyncIterator[bytes]:
        """
        Download file from the sandbox by hash

        Args:
            file_uri: id of the file in the sandbox
            read_timeout: how long should I wait for the file to download?

        Returns:
            streaming file data

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status (404 if the file is not found)
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        timeout = attr.evolve(self.default_timeout, sock_read=read_timeout)

        async with self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            json={"file_uri": file_uri},
            timeout=timeout,
        ) as response:
            async for chunk in self._iter_chunks(response):
                yield chunk
