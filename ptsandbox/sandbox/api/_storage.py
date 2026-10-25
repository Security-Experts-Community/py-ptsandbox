import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import BinaryIO

from ptsandbox.models import SandboxUploadScanFileResponse
from ptsandbox.sandbox._payload import Payload
from ptsandbox.sandbox.base import BaseSandboxClient


class StorageMixin(BaseSandboxClient):
    upload_semaphore: asyncio.Semaphore

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
        timeout = self._timeout(total=upload_timeout)

        url = f"{self.key.url}/storage/uploadScanFile"

        payload = Payload(file)

        async with self.upload_semaphore:
            # an upload only puts the file into temporary storage, so it's safe to resend
            return await self._request(
                "POST",
                url,
                response_model=SandboxUploadScanFileResponse,
                payload=payload,
                retry=True,
                timeout=timeout,
            )

    async def download_artifact(self, file_uri: str, read_timeout: int = 120) -> bytes:
        """
        Download file from the sandbox by hash

        Args:
            file_uri:
                Permanent file identifier in the ``sha256:<sha256_hex>`` format.

                This is not the same as the temporary ``file_uri`` returned by
                :meth:`upload_file` (``sfm:stream_v1...``), which is only valid
                for use with scan creation endpoints.
            read_timeout: response waiting time in seconds

        Returns:
            File data

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status (404 if the file is not found)
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        timeout = self._timeout(sock_read=read_timeout)

        async with self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            json={"file_uri": file_uri},
            retry=True,
            timeout=timeout,
        ) as response:
            return await response.read()

    async def download_artifact_stream(self, file_uri: str, read_timeout: int = 120) -> AsyncIterator[bytes]:
        """
        Download file from the sandbox by hash

        Args:
            file_uri:
                Permanent file identifier in the ``sha256:<sha256_hex>`` format.

                This is not the same as the temporary ``file_uri`` returned by
                :meth:`upload_file` (``sfm:stream_v1...``), which is only valid
                for use with scan creation endpoints.
            read_timeout: response waiting time in seconds

        Returns:
            streaming file data

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status (404 if the file is not found)
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        timeout = self._timeout(sock_read=read_timeout)

        async with self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            json={"file_uri": file_uri},
            retry=True,
            timeout=timeout,
        ) as response:
            async for chunk in self._iter_chunks(response):
                yield chunk
