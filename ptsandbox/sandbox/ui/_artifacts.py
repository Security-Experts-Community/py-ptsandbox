from collections.abc import AsyncIterator
from typing import Any, Literal
from uuid import UUID

import orjson

from ptsandbox.models import (
    SandboxArtifactsFilterValuesResponse,
    SandboxScansResponse,
    SandboxTreeResponse,
    StorageItem,
)
from ptsandbox.sandbox.base import BaseSandboxClient
from ptsandbox.sandbox.ui._token import token_required


class ArtifactsMixin(BaseSandboxClient):
    @token_required
    async def get_files(self, items: list[StorageItem]) -> AsyncIterator[bytes]:
        """
        Download file via UI API

        Args:
            items: the list of files to download

        Returns:
            ZIP archive with "infected" password

            Please note that if one of the hashes doesn't exist, and the others do,
            then the archive will be **only with existing hashes**.

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status (404 if none of the files are found)
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        # if passed just hash without filename, put hash as filename
        query: list[StorageItem] = [
            item if item.get("name") is not None else {"sha256": item["sha256"], "name": item["sha256"]}
            for item in items
        ]

        # idk, why json passed as GET param
        query_string = orjson.dumps(query).decode()

        response = await self._request(
            "GET",
            f"{self.key.ui_url}/storage/download",
            params={"items": query_string},
        )
        response.raise_for_status()

        async for chunk in self._iter_chunks(response):
            yield chunk

    @token_required
    async def get_artifacts_csv(
        self,
        query: str = "",
        columns: (
            list[
                Literal[
                    "behavioralAnalysis",
                    "bwListStatus",
                    "createProcess",
                    "detects.avast",
                    "detects.clamav",
                    "detects.drweb",
                    "detects.eset",
                    "detects.kaspersky",
                    "detects.nano",
                    "detects.ptesc",
                    "detects.ptav",
                    "detects.vba",
                    "detects.yara",
                    "detects.yara.test",
                    "emlBcc",
                    "emlCC",
                    "emlFrom",
                    "emlTo",
                    "fileExtensionTypeGroup",
                    "fileLabels",
                    "fileMd5",
                    "fileName",
                    "fileSha1",
                    "fileSha256",
                    "fileSize",
                    "fileType",
                    "fromTo",
                    "imageDuration",
                    "imageName",
                    "mimeType",
                    "nodeType",
                    "priority",
                    "receivedFrom",
                    "ruleEngineDetects",
                    "ruleEngineVerdict",
                    "sandboxBehavioral",
                    "sandboxBootkitmon",
                    "sandboxDetects",
                    "sandboxVerdict",
                    "smtpFrom",
                    "smtpTo",
                    "source",
                    "ssdeep",
                    "status",
                    "subject",
                    "taskId",
                    "time",
                    "verdict",
                    "verdict.avast",
                    "verdict.clamav",
                    "verdict.drweb",
                    "verdict.eset",
                    "verdict.kaspersky",
                    "verdict.nano",
                    "verdict.ptesc",
                    "verdict.ptav",
                    "verdict.vba",
                    "verdict.yara",
                    "verdict.yara.test",
                    "verdictPriority",
                    "verdictReason",
                ]
            ]
            | None
        ) = None,
        utc_offset_seconds: int = 0,
    ) -> AsyncIterator[bytes]:
        """
        Export an artifacts listing to CSV

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
            f"{self.key.ui_url}/v2/artifacts/export",
            params=data,
        )

        response.raise_for_status()

        async for chunk in self._iter_chunks(response):
            yield chunk

    @token_required
    async def get_artifacts_filter_values(
        self,
        from_: str = "",
        to: str = "",
        scan_id: UUID | None = None,
    ) -> SandboxArtifactsFilterValuesResponse:
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
            f"{self.key.ui_url}/v2/artifacts/filter-values",
            response_model=SandboxArtifactsFilterValuesResponse,
            params=data,
        )

    @token_required
    async def get_task_tree(
        self,
        scan_id: UUID,
        *,
        parent_path: list[int] | None = None,
        filtered_by_ids: list[int] | None = None,
        limit: int = 1000,
        offset: int = 0,
        max_tree_level: int = 3,
        sort_mode: Literal["DANGEROUS", "ALPHABETICAL"] = "DANGEROUS",
    ) -> SandboxTreeResponse:
        """
        Get a tree of artifacts for a specific task

        Args:
            scan_id: ...
            parent_path: the full path to the parent to start loading the tree from. For example: [0, 2, 10]
            filtered_by_ids: a list of IDs of specific nodes to be returned, for example: [0, 2, 10, 11]
            limit: limit on the number of records to be returned
            offset: the indentation from which the records are returned, used for pagination
            max_tree_level: the maximum depth (relative to the parent) to be returned
            sort_mode: the sorting method. First, the dangerous ones are 'DANGEROUS' or just alphabetically 'ALPHABETIC'

        Returns:
            The Artifact Tree

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        data: dict[str, Any] = {"limit": limit, "offset": offset, "maxTreeLevel": max_tree_level, "sortMode": sort_mode}
        if parent_path is not None:
            data["parentPath"] = ",".join(map(str, parent_path))
        if filtered_by_ids is not None:
            data["filteredByIds"] = ",".join(map(str, filtered_by_ids))

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/{scan_id}/tree",
            response_model=SandboxTreeResponse,
            params=data,
        )

    @token_required
    async def get_task_artifacts(
        self,
        scan_id: UUID,
        *,
        query: str = "",
        include_sandbox_logs: Literal["true", "false"] = "true",
        skip_data_files: Literal["true", "false"] = "false",
    ) -> AsyncIterator[bytes]:
        """
        Download all the artifacts of the task

        Args:
            scan_id: ...
            query: filtering using the query language. For the syntax, see the user documentation.
            include_sandbox_logs: whether to include BA logs as a result
            skip_data_files: whether to include data files in the result

        Returns:
            Sandbox returns an encrypted zip archive (password - infected), so we just export a set of bytes.
            If necessary, you can use pyzipper to unpack

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        data: dict[str, Any] = {
            "query": query,
            "includeSandboxLogs": include_sandbox_logs,
            "skipDataFiles": skip_data_files,
        }

        response = await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/{scan_id}/tree/download",
            params=data,
        )

        response.raise_for_status()

        async for chunk in self._iter_chunks(response):
            yield chunk

    @token_required
    async def get_task_artifact_scans(self, scan_id: UUID, node_id: int) -> SandboxScansResponse:
        """
        Getting scan results for a specific artifact

        Args:
            scan_id: ...
            node_id: ...

        Returns:
            The model with the scan results

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/tasks/{scan_id}/artifacts/{node_id}/scans",
            response_model=SandboxScansResponse,
        )
