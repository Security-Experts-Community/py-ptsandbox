from pathlib import Path
from typing import BinaryIO
from uuid import UUID

import attr

from ptsandbox.models import (
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
)
from ptsandbox.models.api.scan import (
    SandboxScanWithSourceFileRequest,
    SandboxScanWithSourceURLRequest,
)
from ptsandbox.sandbox.base import BaseSandboxClient


class ScanMixin(BaseSandboxClient):
    async def source_check_file(
        self,
        file: str | Path | bytes | BinaryIO,
        data: SandboxScanWithSourceFileRequest,
        read_timeout: int = 240,
    ) -> SandboxBaseTaskResponse:
        """
        Send file to the sandbox with source settings

        Args:
            file:
                The file to be sent for analysis
            data:
                Request parameters in model
            read_timeout:
                Response waiting time in seconds

        Raises:
            SandboxException: if incorrect arguments are passed (usually when ignoring type hints)
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        timeout = attr.evolve(self.default_timeout, total=read_timeout)

        with self._file_payload(file) as payload:  # type: ignore[attr-defined]
            return await self._request(
                "POST",
                f"{self.key.url}/scan/checkFile",
                response_model=SandboxBaseTaskResponse,
                params=data.dict(),
                headers=data.get_headers(),
                data=payload,
                timeout=timeout,
            )

    async def source_check_url(
        self,
        data: SandboxScanWithSourceURLRequest,
        read_timeout: int = 240,
    ) -> SandboxBaseTaskResponse:
        """
        Send url to the sandbox with source settings

        Args:
            data:
                Request parameters in model
            read_timeout:
                Response waiting time in seconds

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        timeout = attr.evolve(self.default_timeout, total=read_timeout)

        return await self._request(
            "POST",
            f"{self.key.url}/scan/checkURL",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            headers=data.get_headers(),
            timeout=timeout,
        )

    async def source_get_status(self, data: SandboxCheckTaskRequest) -> SandboxCheckTaskResponse:
        """
        Check the status of a scan started via the source API (source_check_file / source_check_url).

        Returns only the status without the full report. For the full report, use ``source_get_report``.

        Args:
            data: request parameters (scan_id and allow_preflight)

        Returns:
            Information about the analysis status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/scan/getStatus",
            response_model=SandboxCheckTaskResponse,
            json=data.dict(),
        )

    async def source_get_report(self, scan_id: UUID) -> SandboxBaseTaskResponse:
        """
        Get the full scan report created using the source settings

        Args:
            task_id: task id :)

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/scan/getFullReport",
            response_model=SandboxBaseTaskResponse,
            json={"scan_id": str(scan_id)},
        )
