from collections.abc import AsyncIterator
from typing import Any, BinaryIO
from uuid import UUID

import attr

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
from ptsandbox.sandbox.base import BaseSandboxClient


class AnalysisMixin(BaseSandboxClient):
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

        # compute default timeout
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

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
        Send the specified file to the sandbox for analysis using advanced APi

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
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.sandbox.analysis_duration * 4
            + (300 if data.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

        return await self._request(
            "POST",
            f"{self.key.debug_url}/analysis/createBAScanTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    async def creat_url_scan(self, data: SandboxScanURLTaskRequest, read_timeout: int = 0) -> SandboxBaseTaskResponse:
        """
        Send the url to the sandbox

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

        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + read_timeout,
        )

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/createScanURLTask",
            response_model=SandboxBaseTaskResponse,
            json=data.dict(),
            timeout=timeout,
        )

    create_url_scan = creat_url_scan

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
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/analysis/checkTask",
            response_model=SandboxCheckTaskResponse,
            json=data.dict(),
        )

    async def get_report(self, scan_id: UUID) -> SandboxBaseTaskResponse:
        """
        Getting the full task scan report

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
            f"{self.key.url}/analysis/report",
            response_model=SandboxBaseTaskResponse,
            json={"scan_id": str(scan_id)},
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
        timeout = attr.evolve(
            self.default_timeout,
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
            data=data.json(),
            timeout=timeout,
        )

    async def get_email_headers(self, data: BinaryIO) -> AsyncIterator[bytes]:
        """
        Upload an email to receive headers

        Args:
            data: file data

        Returns:
            The header file

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        payload = self._upload_bytes(data)  # type: ignore[attr-defined]

        response = await self._request(
            "POST",
            f"{self.key.debug_url}/analysis/getHeaders",
            data=payload,
        )

        response.raise_for_status()

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
        )
