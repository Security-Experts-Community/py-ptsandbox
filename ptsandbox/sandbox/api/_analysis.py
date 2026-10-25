from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, BinaryIO
from uuid import UUID

import aiohttp

from ptsandbox.models import (
    SandboxAdvancedScanTaskRequest,
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
    SandboxRescanTaskRequest,
    SandboxScanTaskRequest,
    SandboxScanURLTaskRequest,
)
from ptsandbox.models.api.analysis import SandboxTasksResponse
from ptsandbox.sandbox._payload import Payload
from ptsandbox.sandbox.base import BaseSandboxClient


class AnalysisMixin(BaseSandboxClient):
    def _analysis_timeout(self, analysis_duration: int, read_timeout: int) -> aiohttp.ClientTimeout:
        """Time to wait for a synchronous scan response: the analysis itself plus the sandbox overhead."""
        return self._timeout(
            sock_read=analysis_duration * 4 + (300 if analysis_duration < 80 else 120) + read_timeout,
        )

    async def create_scan(self, data: SandboxScanTaskRequest, read_timeout: int = 0) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        timeout = self._analysis_timeout(data.options.sandbox.analysis_duration, read_timeout)

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/createScanTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    async def create_advanced_scan(
        self,
        data: SandboxAdvancedScanTaskRequest,
        read_timeout: int = 0,
    ) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis using advanced API

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        timeout = self._analysis_timeout(data.sandbox.analysis_duration, read_timeout)

        return await self._request(
            "POST",
            f"{self.key.debug_url}/analysis/createBAScanTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    async def create_url_scan(self, data: SandboxScanURLTaskRequest, read_timeout: int = 0) -> SandboxBaseTaskResponse:
        """
        Send the URL to the sandbox

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        timeout = self._analysis_timeout(data.options.sandbox.analysis_duration, read_timeout)

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/createScanURLTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    async def check_task(self, data: SandboxCheckTaskRequest) -> SandboxCheckTaskResponse:
        """
        Checking the result of a scan running with the async_result flag

        Args:
            data: request parameters (scan_id, allow_preflight)

        Returns:
            Information about the analysis status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/checkTask",
            response_model=SandboxCheckTaskResponse,
            json=data.dict(),
            retry=True,
        )

    async def get_report(self, scan_id: UUID) -> SandboxBaseTaskResponse:
        """
        Getting the full task scan report

        Args:
            scan_id: ID of the task to get the report for

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/report",
            response_model=SandboxBaseTaskResponse,
            json={"scan_id": str(scan_id)},
            retry=True,
        )

    async def create_rescan(self, data: SandboxRescanTaskRequest, read_timeout: int = 300) -> SandboxBaseTaskResponse:
        """
        Run a retro scan to check for detects without running a behavioral analysis.

        Args:
            data: sandbox parameters in model
            read_timeout: response waiting time in seconds

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        # compute default timeout
        timeout = self._timeout(
            sock_read=(
                round(data.options.sandbox.analysis_duration * 1.5)
                if data.options.sandbox.analysis_duration > 70
                else 70
            )
            + read_timeout,
        )

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/createRetroTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    async def get_email_headers(self, data: str | Path | bytes | BinaryIO) -> AsyncIterator[bytes]:
        """
        Upload an email to receive headers

        Args:
            data: path to .eml file, its content or a binary stream

        Returns:
            The header file

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        async with self.http_client.post(
            f"{self.key.debug_url}/analysis/getHeaders",
            payload=Payload(data),
            retry=True,
        ) as response:
            async for chunk in self._iter_chunks(response):
                yield chunk

    async def get_tasks(self, data: dict[str, Any]) -> SandboxTasksResponse:
        """
        Get tasks listing

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/listTasks",
            response_model=SandboxTasksResponse,
            json=data,
            retry=True,
        )
