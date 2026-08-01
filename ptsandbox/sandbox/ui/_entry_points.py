from collections.abc import AsyncIterator
from typing import Any

from ptsandbox.models import (
    SandboxCreateEntryPointRequest,
    SandboxEntryPointResponse,
    SandboxEntryPointsResponse,
    SandboxEntryPointsTypesResponse,
    SandboxUITasksResponse,
)
from ptsandbox.sandbox.base import BaseSandboxClient
from ptsandbox.sandbox.ui._token import token_required


class EntryPointsMixin(BaseSandboxClient):
    @token_required
    async def get_entry_points_types(self) -> SandboxEntryPointsTypesResponse:
        """
        Get a list of possible sources to check with their parameters

        Returns:
            List of possible sources

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/entry-points-types",
            response_model=SandboxEntryPointsTypesResponse,
        )

    @token_required
    async def get_entry_points(self) -> SandboxEntryPointsResponse:
        """
        Get a list of added sources for analysis

        Returns:
            EntryPoints model

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/entry-points",
            response_model=SandboxEntryPointsResponse,
        )

    @token_required
    async def create_entry_point(self, parameters: SandboxCreateEntryPointRequest) -> None:
        """
        Add a new analysis source

        Args:
            parameters:
                Parameters for request

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        async with self.http_client.post(
            f"{self.key.ui_url}/entry-points",
            json=parameters.dict(),
        ):
            pass

    @token_required
    async def get_entry_point(self, entry_point_id: str) -> SandboxEntryPointResponse:
        """
        Get information about the analysis source

        Args:
            entry_point_id:
                ID of entry point

        Returns:
            EntryPoint model

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/entry-points/{entry_point_id}",
            response_model=SandboxEntryPointResponse,
        )

    @token_required
    async def delete_entry_point(self, entry_point_id: str) -> None:
        """
        Delete the analysis source

        Args:
            entry_point_id:
                ID of entry point

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        async with self.http_client.delete(
            f"{self.key.ui_url}/entry-points/{entry_point_id}",
        ):
            pass

    @token_required
    async def get_entry_point_tasks(
        self,
        entry_point_id: str,
        query: str = "",
        limit: int = 20,
        offset: int = 0,
        utc_offset_seconds: int = 0,
        next_cursor: str | None = None,
    ) -> SandboxUITasksResponse:
        """
        Listing tasks from the source

        Args:
            entry_point_id:
                ID of entry point
            query:
                Filtering using the query language. For the syntax, see the user documentation.

                ```
                age < 30d AND (task.correlated.state != UNKNOWN ) ORDER BY start desc
                ```
            limit:
                Limit on the number of records to be returned
            offset:
                The offset of the returned records. If the next Cursor is specified, the offset from the cursor is
            utc_offset_seconds:
                The offset of the user's time from UTC, which will be used for the time in QL queries

        Returns:
            Information about requested tasks

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        data: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "utcOffsetSeconds": utc_offset_seconds,
        }

        if next_cursor is not None:
            data["nextCursor"] = next_cursor

        return await self._request(
            "GET",
            f"{self.key.ui_url}/entry-points/{entry_point_id}/tasks",
            response_model=SandboxUITasksResponse,
            params=data,
        )

    @token_required
    async def get_entry_point_logs(self, entry_point_id: str) -> AsyncIterator[bytes]:
        """
        Download logs of a specific source

        Args:
            entry_point_id:
                ID of entry point

        Returns:
            Archive with logs

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        async with self.http_client.get(
            f"{self.key.ui_url}/entry-points/{entry_point_id}/logs",
        ) as response:
            async for chunk in self._iter_chunks(response):
                yield chunk
