import asyncio
from collections.abc import AsyncIterator
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

import aiohttp
import attr
from aiohttp_socks import ProxyConnector
from loguru import logger

from ptsandbox.models import (
    CheckHealthResponse,
    GetVersionResponse,
    SandboxAdvancedScanTaskRequest,
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
    SandboxException,
    SandboxFileNotFoundException,
    SandboxGetImagesResponse,
    SandboxKey,
    SandboxRescanTaskRequest,
    SandboxScanTaskRequest,
    SandboxScanURLTaskRequest,
    SandboxUploadScanFileResponse,
)
from ptsandbox.utils.async_http_client import AsyncHTTPClient


class SandboxApi:
    """
    Using raw queries to sandbox API
    """

    key: SandboxKey
    session: aiohttp.ClientSession
    default_timeout: aiohttp.ClientTimeout
    upload_semaphore: asyncio.Semaphore

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: aiohttp.ClientTimeout,
        upload_semaphore_size: int | None = None,
        proxy: str | None = None,
    ) -> None:
        self.key = key
        self.default_timeout = default_timeout
        self.session = aiohttp.ClientSession(
            timeout=self.default_timeout,
            connector=(
                ProxyConnector.from_url(proxy, ssl=False)
                if proxy
                else aiohttp.TCPConnector(
                    ssl=False,
                    # i know this is strange, but aiodns => c-ares can't correctly resolve dns names
                    # https://github.com/c-ares/c-ares/issues/642
                    resolver=aiohttp.ThreadedResolver(),
                )
            ),
            headers={"X-Api-Key": key.key},
        )
        self.http_client = AsyncHTTPClient(self.session, logger=logger)

        self.upload_semaphore = asyncio.Semaphore(
            upload_semaphore_size if upload_semaphore_size else self.key.max_workers
        )

    async def _upload_bytes(self, file: BinaryIO) -> AsyncIterator[bytes]:
        while chunk := file.read(1024 * 1024):
            yield chunk

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
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        # update default timeout
        timeout = attr.evolve(self.default_timeout, total=upload_timeout)

        url = f"{self.key.url}/storage/uploadScanFile"

        async with self.upload_semaphore:
            match file:
                case str() | Path():
                    # we can't use aiofiles here, because aiohttp try use chunked encoding
                    # sandbox (or maybe aiohttp) can't correctly handle chunked encoding (i have no idea why, don't ask me)
                    # so we need this clunky code
                    with open(file, "rb") as fd:
                        response = await self.http_client.post(
                            url=url,
                            data=fd,
                            timeout=timeout,
                        )
                case bytes():
                    response = await self.http_client.post(
                        url=url,
                        data=file,
                        timeout=timeout,
                    )
                case BytesIO():
                    response = await self.http_client.post(
                        url=url,
                        data=self._upload_bytes(file),
                        timeout=timeout,
                    )
                case _:
                    raise SandboxException(f"Specified file type doesn't supported {type(file)}!")

        response.raise_for_status()

        return await SandboxUploadScanFileResponse.build(response)

    async def _download_artifact(self, file_uri: str, read_timeout: int) -> aiohttp.ClientResponse:
        timeout = attr.evolve(self.default_timeout, sock_read=read_timeout)

        response = await self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            json={"file_uri": file_uri},
            timeout=timeout,
        )

        return response

    async def download_artifact(self, file_uri: str, read_timeout: int = 120) -> bytes:
        """
        Download file from the sandbox by hash

        Args:
            file_uri: id of the file in the sandbox
            read_timeout: how long should I wait for the file to download?

        Returns:
            File data

        Raises:
            SandboxFileNotFoundException: if the requested file is not found on the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self._download_artifact(file_uri, read_timeout)
        if response.status == HTTPStatus.NOT_FOUND:
            raise SandboxFileNotFoundException(f"Requested file {file_uri} not found")

        response.raise_for_status()

        # idk how to fix mypy complains about next line
        return await response.read()  # type: ignore

    async def download_artifact_stream(self, file_uri: str, read_timeout: int = 120) -> AsyncIterator[bytes]:
        """
        Download file from the sandbox by hash

        Args:
            file_uri: id of the file in the sandbox
            read_timeout: how long should I wait for the file to download?

        Returns:
            streaming file data or throw exception SandboxFileNotFoundException

        Raises:
            SandboxFileNotFoundException: if the requested file is not found on the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self._download_artifact(file_uri, read_timeout)
        if response.status == HTTPStatus.NOT_FOUND:
            raise SandboxFileNotFoundException(f"Requested file {file_uri} not found")

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    async def create_scan(self, data: SandboxScanTaskRequest, read_timeout: int = 0) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        # compute default timeout
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

        response = await self.http_client.post(
            f"{self.key.url}/analysis/createScanTask",
            json=data.dict(),
            timeout=timeout,
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build(response)

    async def create_advanced_scan(
        self,
        data: SandboxAdvancedScanTaskRequest,
        read_timeout: int = 0,
    ) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis using advanced APi

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        # compute default timeout
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.sandbox.analysis_duration * 4
            + (300 if data.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

        response = await self.http_client.post(
            f"{self.key.debug_url}/analysis/createBAScanTask",
            json=data.dict(),
            timeout=timeout,
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build(response)

    async def creat_url_scan(self, data: SandboxScanURLTaskRequest, read_timeout: int = 0) -> SandboxBaseTaskResponse:
        """
        Send the url to the sandbox

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

        response = await self.http_client.post(
            f"{self.key.url}/analysis/createScanURLTask",
            json=data.dict(),
            timeout=timeout,
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build(response)

    async def check_task(self, data: SandboxCheckTaskRequest) -> SandboxCheckTaskResponse:
        """
        Checking the result of a scan running with the async_result flag

        Args:
            task_id: task id :)
            allow_preflight:
                If this flag is set, an intermediate result with the `is_preflight` attribute
                will be returned for scanning with multiple stages (for example, static + BA).

        Returns:
            Information about the analysis status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.post(
            f"{self.key.url}/analysis/checkTask",
            json=data.dict(),
        )

        response.raise_for_status()

        return await SandboxCheckTaskResponse.build(response)

    async def get_report(self, scan_id: UUID) -> SandboxBaseTaskResponse:
        """
        Getting the full task scan report

        Args:
            task_id: task id :)

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.post(
            f"{self.key.url}/analysis/report",
            json={"scan_id": str(scan_id)},
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build(response)

    async def create_rescan(self, data: SandboxRescanTaskRequest, read_timeout: int = 300) -> SandboxBaseTaskResponse:
        """
        Run a retro scan to check for detects without running a behavioral analysis.

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        # compute default timeout
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=(
                round(data.options.sandbox.analysis_duration * 1.5)
                if data.options.sandbox.analysis_duration > 70
                else 70
            )
            + read_timeout,
        )

        response = await self.http_client.post(
            f"{self.key.url}/analysis/createRetroTask",
            headers={"Content-Type": "application/json"},
            data=data.json(),
            timeout=timeout,
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build(response)

    async def get_email_headers(self, data: BinaryIO) -> AsyncIterator[bytes]:
        """
        Upload an email to receive headers

        Args:
            data: file data

        Returns:
            The header file

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.post(
            f"{self.key.debug_url}/analysis/getHeaders",
            data=self._upload_bytes(data),
        )

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    async def get_images(self) -> SandboxGetImagesResponse:
        """
        Get a list of available images in the sandbox

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.post(
            f"{self.key.url}/engines/sandbox/getImages",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

        return await SandboxGetImagesResponse.build(response)

    async def check_health(self) -> CheckHealthResponse:
        """
        Checking the API status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(url=f"{self.key.url}/maintenance/checkHealth")

        response.raise_for_status()

        return await CheckHealthResponse.build(response)

    async def get_version(self) -> GetVersionResponse:
        """
        Get information about product

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(url=f"{self.key.url}/maintenance/getVersion")

        response.raise_for_status()

        return await GetVersionResponse.build(response)

    def __del__(self) -> None:
        if not self.session.closed:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            if loop.is_running():
                loop.create_task(self.session.close())
            else:
                loop.run_until_complete(self.session.close())
