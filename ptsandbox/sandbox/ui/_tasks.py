from collections.abc import AsyncIterator
from typing import Any, Literal
from uuid import UUID

from ptsandbox.models import (
    SandboxBaqueueTasksResponse,
    SandboxTasksFilterValuesResponse,
    SandboxTasksResponse,
    SandboxTasksSummaryResponse,
)
from ptsandbox.sandbox.base import BaseSandboxClient
from ptsandbox.sandbox.ui._token import token_required


class TasksMixin(BaseSandboxClient):
    @token_required
    async def get_tasks(
        self,
        query: str = "",
        limit: int = 20,
        offset: int = 0,
        utc_offset_seconds: int = 0,
        next_cursor: str | None = None,
    ) -> SandboxTasksResponse:
        """
        Get tasks listing

        Args:
            query:
                filtering using the query language. For the syntax, see the user documentation.

                ```
                age < 30d AND (task.correlated.state != UNKNOWN ) ORDER BY start desc
                ```
            limit: limit on the number of records to be returned
            offset: the offset of the returned records. If the next Cursor is specified, the offset from the cursor is
            utc_offset_seconds: the offset of the user's time from UTC, which will be used for the time in QL queries
            next_cursor: the value from the previous request

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
            f"{self.key.ui_url}/v2/tasks",
            response_model=SandboxTasksResponse,
            params=data,
        )

    @token_required
    async def get_tasks_csv(
        self,
        query: str = "",
        columns: (
            list[
                Literal[
                    "action",
                    "behavioralAnalysis",
                    "fromTo",
                    "priority",
                    "processedTime",
                    "quarantine",
                    "source",
                    "status",
                    "taskName",
                    "time",
                    "verdict",
                    "verdictTime",
                ]
            ]
            | None
        ) = None,
        utc_offset_seconds: int = 0,
    ) -> AsyncIterator[bytes]:
        """
        Export a tasks listing to CSV

        Args:
            query: filtering using the query language. For the syntax, see the user documentation.
            columns: the list of csv columns to be exported.
            utc_offset_seconds: the offset of the user's time from UTC, which will be used for the time in QL queries

        Returns:
            AsyncIterator with chunks of CSV file

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        if columns is None:
            columns = []

        data: dict[str, Any] = {
            "format": "CSV",  # only csv supported by now
            "query": query,
            "columns": ",".join(columns),
            "utcOffsetSeconds": utc_offset_seconds,
        }

        response = await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/export",
            params=data,
        )

        response.raise_for_status()

        async for chunk in self._iter_chunks(response):
            yield chunk

    @token_required
    async def get_tasks_filter_values(
        self,
        from_: str = "",
        to: str = "",
        scan_id: UUID | None = None,
    ) -> SandboxTasksFilterValuesResponse:
        """
        Get possible values for filters based on sources and validation results

        Args:
            from_: for which period possible values are being searched: minimum time
            to: for which period possible values are being searched: maximum time
            scan_id: filter by task ID

        Returns:
            Possible filter values

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        data: dict[str, Any] = {}
        if scan_id is not None:
            data["scanId"] = scan_id

        if from_:
            data["from"] = from_

        if to:
            data["to"] = to

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/filter-values",
            response_model=SandboxTasksFilterValuesResponse,
            params=data,
        )

    @token_required
    async def get_task_summary(self, scan_id: UUID) -> SandboxTasksSummaryResponse:
        """
        Get information about a specific task

        Args:
            scan_id: task id

        Returns:
            Full information about a specific task

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/{scan_id}/summary",
            response_model=SandboxTasksSummaryResponse,
        )

    @token_required
    async def get_baqueue_tasks(
        self,
        query: str = "age < 7d AND state IN (CREATED, STARTING, STARTED, DEDUPLICATION, READY, READY_WITH_ERROR) ORDER BY state DESC, priority.value DESC, ts.created",
        limit: int = 50,
        offset: int = 0,
        utc_offset_seconds: int = 0,
    ) -> SandboxBaqueueTasksResponse:
        """
        Listing of tasks in the Behavioral Analysis queue

        Args:
            query: QL search query (by default, all tasks that are currently running are requested)
            limit: limit on the number of records to be returned
            offset: offset of returned records
            utc_offset_seconds: the offset of the user's time from UTC, which will be used for the time in QL queries

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        data: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "query": query,
            "utcOffsetSeconds": utc_offset_seconds,
        }

        return await self._request(
            "GET",
            f"{self.key.ui_url}/baqueue/tasks",
            response_model=SandboxBaqueueTasksResponse,
            params=data,
        )
