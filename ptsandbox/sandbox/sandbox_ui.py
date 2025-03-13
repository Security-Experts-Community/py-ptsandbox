import asyncio
import datetime
import functools
import inspect
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from http import HTTPStatus
from typing import Any, Literal, ParamSpec, TypeVar, overload
from urllib.parse import urlparse
from uuid import UUID

import aiohttp
import aiohttp.client_exceptions
from aiohttp_socks import ProxyConnector
from loguru import logger

from ptsandbox.models import (
    SandboxArtifactsFilterValuesResponse,
    SandboxAVEnginesResponse,
    SandboxBaqueueTasksResponse,
    SandboxClusterStatusResponse,
    SandboxCreateTokenResponse,
    SandboxException,
    SandboxKey,
    SandboxScansResponse,
    SandboxSystemSettingsResponse,
    SandboxSystemStatusResponse,
    SandboxSystemVersionResponse,
    SandboxTasksFilterValuesResponse,
    SandboxTasksResponse,
    SandboxTasksSummaryResponse,
    SandboxTokensResponse,
    SandboxTreeResponse,
    SandboxUpdateSystemSettingsRequest,
    TokenPermissions,
)
from ptsandbox.models.ui.components import SandboxComponentsResponse
from ptsandbox.models.ui.license import (
    SandboxLicenseResponse,
    SandboxLicenseUpdateResponse,
)
from ptsandbox.utils.async_http_client import AsyncHTTPClient

P = ParamSpec("P")
R = TypeVar("R")


class SandboxUI:
    """
    Using raw queries to sandbox UI API
    """

    const_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",  # noqa
        "Content-Type": "application/json",
    }

    key: SandboxKey
    session: aiohttp.ClientSession
    default_timeout: aiohttp.ClientTimeout

    update_token_lock: asyncio.Lock
    last_updated_token: datetime.datetime | None

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: aiohttp.ClientTimeout,
        proxy: str | None = None,
        token_lifetime: datetime.timedelta = datetime.timedelta(minutes=8),
    ) -> None:
        self.key = key
        self.default_timeout = default_timeout
        self.token_lifetime = token_lifetime

        self.session = aiohttp.ClientSession(
            timeout=self.default_timeout,
            headers=self.const_headers,
            cookie_jar=aiohttp.CookieJar(unsafe=True),
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
        )

        self.is_authorized = False
        self.last_updated_token = None
        self.fingerprint = "".join(random.choice("0123456789abcdef") for _ in range(32))
        self.update_token_lock = asyncio.Lock()

        self.http_client = AsyncHTTPClient(self.session, logger=logger)

    @staticmethod
    @overload
    def _token_required(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...

    @staticmethod
    @overload
    def _token_required(func: Callable[P, AsyncIterator[bytes]]) -> Callable[P, AsyncIterator[bytes]]: ...

    @staticmethod
    def _token_required(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        An auxiliary method for verifying authorization
        """

        if inspect.isasyncgenfunction(func):

            @functools.wraps(func)
            # idk how to fix mypy complains about next line
            def wrapper_iter(self: "SandboxUI", *args: P.args, **kwargs: P.kwargs) -> Any:  # type: ignore
                async def inner() -> Any:
                    await self._ensure_token()
                    async for chunk in func(self, *args, **kwargs):
                        yield chunk

                return inner()

            return wrapper_iter
        else:

            @functools.wraps(func)
            # idk how to fix mypy complains about next line
            async def wrapper(self: "SandboxUI", *args: P.args, **kwargs: P.kwargs) -> Any:  # type: ignore
                await self._ensure_token()
                return await func(self, *args, **kwargs)

            return wrapper

    async def _ensure_token(self) -> None:
        if not self.is_authorized:
            raise SandboxException("Can't use the UI API without logging in first")

        async with self.update_token_lock:
            if not self.last_updated_token or (datetime.datetime.now() > self.last_updated_token + self.token_lifetime):
                await self._update_token()

    async def _update_token(self) -> None:
        response = await self.http_client.post(
            f"{self.key.ui_url}/auth/token",
            json={"fingerprint": self.fingerprint},
        )

        token = await response.json()

        try:
            self.session.headers["Authorization"] = "Bearer " + token["data"]["accessToken"]
        except ValueError as e:
            raise SandboxException("Can't get accessToken from response") from e

        self.last_updated_token = datetime.datetime.now()

    async def authorize(self) -> None:
        """
        Authorization in the UI using the passed parameters in the key
        """

        parameters = {"fingerprint": self.fingerprint}

        response = await self.http_client.get(f"{self.key.ui_url}/auth/authorize", params=parameters)
        try:
            location: str = (await response.json())["data"]["location"]
        except KeyError as e:
            raise SandboxException("Can't get location from authorization url") from e

        url = urlparse(location)

        assert self.key.ui is not None

        data: dict[str, str | bool | SandboxKey.UI.AuthType] = {
            "username": self.key.ui.login,
            "password": self.key.ui.password,
            "authType": self.key.ui.auth_type,
            "rememberLogin": True,
        }

        response = await self.http_client.post(f"{url.scheme}://{url.netloc}/ui/login", json=data)
        if response.status != HTTPStatus.OK:
            await self.close()
            response.raise_for_status()

        # get refresh token
        await self.http_client.get(location)

        self.is_authorized = True

        # get access token
        await self._update_token()

    async def close(self) -> None:
        """
        Close UI session
        """

        if not self.session.closed:
            await self.session.close()

    @_token_required
    async def get_system_status(self) -> SandboxSystemStatusResponse:
        """
        Get information about the system status

        For full information, look at the documentation of the `SandboxSystemStatusResponse` model.

        Returns:
            A model with information about the system
        """

        response = await self.http_client.get(f"{self.key.ui_url}/v2/system/status")

        response.raise_for_status()

        return SandboxSystemStatusResponse.model_validate(await response.json())

    @_token_required
    async def get_system_settings(self) -> SandboxSystemSettingsResponse:
        """
        Get information about the system settings

        Returns:
            A model with system settings
        """

        response = await self.http_client.get(f"{self.key.ui_url}/system/settings")

        response.raise_for_status()

        return SandboxSystemSettingsResponse.model_validate(await response.json())

    @_token_required
    async def update_system_settings(self, settings: SandboxUpdateSystemSettingsRequest) -> None:
        """
        Update system settings
        """

        response = await self.http_client.put(f"{self.key.ui_url}/system/settings", json=settings.dict())

        response.raise_for_status()

    @_token_required
    async def get_system_version(self) -> SandboxSystemVersionResponse:
        """
        Get the version of the installed product
        """

        response = await self.http_client.get(f"{self.key.ui_url}/system/version")

        response.raise_for_status()

        return SandboxSystemVersionResponse.model_validate(await response.json())

    @_token_required
    async def get_system_logs(
        self,
        since: int | None = None,
        components: list[str] | None = None,
    ) -> AsyncIterator[bytes]:
        """
        Download the archive with system logs

        Args:
            since: the time period for uploading logs in seconds
            components: component names in the format `{namespace}/{component}`, `{namespace}/{component}`, ... If the field is empty, all components will be downloaded

        Returns:
            Archive with logs
        """

        if components is None:
            components = []

        data: dict[str, Any] = {"components": ",".join(components)}
        if since is not None:
            data.update({"since": since})

        response = await self.http_client.get(f"{self.key.ui_url}/system/logs")

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    @_token_required
    async def get_system_cluster_status(self) -> SandboxClusterStatusResponse:
        """
        Get information about the cluster status
        """

        response = await self.http_client.get(f"{self.key.ui_url}/v2/system/status/cluster")

        response.raise_for_status()

        return SandboxClusterStatusResponse.model_validate(await response.json())

    @_token_required
    async def get_system_components_status(self) -> SandboxComponentsResponse:
        """
        Get information about the components status
        """

        response = await self.http_client.get(f"{self.key.ui_url}/v2/system/status/components")

        response.raise_for_status()

        return SandboxComponentsResponse.model_validate(await response.json())

    @_token_required
    async def get_license(self) -> SandboxLicenseResponse:
        """
        Get the license status and details
        """

        response = await self.http_client.get(f"{self.key.ui_url}/license")

        response.raise_for_status()

        return SandboxLicenseResponse.model_validate(await response.json())

    @_token_required
    async def update_license(self) -> SandboxLicenseUpdateResponse:
        """
        Updating the current license
        """

        response = await self.http_client.put(f"{self.key.ui_url}/license")

        response.raise_for_status()

        return SandboxLicenseUpdateResponse.model_validate(await response.json())

    @_token_required
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


        Returns:
            Information about requested tasks
        """

        data: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "utcOffsetSeconds": utc_offset_seconds,
        }

        if next_cursor is not None:
            data.update({"nextCursor": next_cursor})

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks", params=data)

        response.raise_for_status()

        return SandboxTasksResponse.model_validate(await response.json())

    @_token_required
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
        """

        if columns is None:
            columns = []

        data: dict[str, Any] = {
            "format": "CSV",  # only csv supported by now
            "query": query,
            "columns": ",".join(columns),
            "utcOffsetSeconds": utc_offset_seconds,
        }

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/export", params=data)

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    @_token_required
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
        """

        data: dict[str, Any] = {}
        if scan_id is not None:
            data.update({"scanId": scan_id})

        if from_:
            data.update({"from": from_})

        if to:
            data.update({"to": to})

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/filter-values", params=data)

        response.raise_for_status()

        return SandboxTasksFilterValuesResponse.model_validate(await response.json())

    @_token_required
    async def get_task_summary(self, scan_id: UUID) -> SandboxTasksSummaryResponse:
        """
        Get information about a specific task

        Args:
            scan_id: task id

        Returns:
            Full information about a specific task
        """

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/{scan_id}/summary")

        response.raise_for_status()

        return SandboxTasksSummaryResponse.model_validate(await response.json())

    @_token_required
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
        """

        if columns is None:
            columns = []

        data: dict[str, Any] = {
            "format": "CSV",  # only csv supported by now
            "query": query,
            "columns": ",".join(columns),
            "utcOffsetSeconds": utc_offset_seconds,
        }

        response = await self.http_client.get(f"{self.key.ui_url}/v2/artifacts/export", params=data)

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    @_token_required
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
        """

        data: dict[str, Any] = {}
        if scan_id is not None:
            data.update({"scanId": scan_id})

        if from_:
            data.update({"from": from_})

        if to:
            data.update({"to": to})

        response = await self.http_client.get(f"{self.key.ui_url}/v2/artifacts/filter-values", params=data)

        response.raise_for_status()

        return SandboxArtifactsFilterValuesResponse.model_validate(await response.json())

    @_token_required
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
        """

        data: dict[str, Any] = {"limit": limit, "offset": offset, "maxTreeLevel": max_tree_level, "sortMode": sort_mode}
        if parent_path is not None:
            data.update({"parentPath": ",".join(map(str, parent_path))})
        if filtered_by_ids is not None:
            data.update({"filteredByIds": ",".join(map(str, filtered_by_ids))})

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/{scan_id}/tree", params=data)

        response.raise_for_status()

        return SandboxTreeResponse.model_validate(await response.json())

    @_token_required
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
        """

        data: dict[str, Any] = {
            "query": query,
            "includeSandboxLogs": include_sandbox_logs,
            "skip_data_files": skip_data_files,
        }

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/{scan_id}/tree/download", params=data)

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    @_token_required
    async def get_task_artifact_scans(self, scan_id: UUID, node_id: int) -> SandboxScansResponse:
        """
        Getting scan results for a specific artifact

        Args:
            scan_id: ...
            node_id: ...

        Returns:
            The model with the scan results
        """

        response = await self.http_client.get(f"{self.key.ui_url}/v2/tasks/{scan_id}/artifacts/{node_id}/scans")

        response.raise_for_status()

        return SandboxScansResponse.model_validate(await response.json())

    @_token_required
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
        """

        data: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "query": query,
            "utcOffsetSeconds": utc_offset_seconds,
        }

        response = await self.http_client.get(f"{self.key.ui_url}/baqueue/tasks", params=data)

        response.raise_for_status()

        return SandboxBaqueueTasksResponse.model_validate(await response.json())

    @_token_required
    async def get_av_engines(self) -> SandboxAVEnginesResponse:
        """
        Get information about antivirus scanners

        Returns:
            A model with information about all antiviruses
        """

        response = await self.http_client.get(f"{self.key.ui_url}/av-engines")

        response.raise_for_status()

        return SandboxAVEnginesResponse.model_validate(await response.json())

    async def get_api_tokens(self) -> SandboxTokensResponse:
        """
        Get listing of current Public API tokens

        Returns:
            A model with information about all tokens
        """

        response = await self.http_client.get(f"{self.key.ui_url}/public-api/tokens")

        response.raise_for_status()

        return SandboxTokensResponse.model_validate(await response.json())

    async def create_api_token(
        self,
        name: str,
        permissions: list[TokenPermissions],
        comment: str = "",
    ) -> SandboxCreateTokenResponse:
        """
        Create a new Public API token

        Args:
            name: token name
            permissions: permissions for the token
            comment: additional information about the token

        Returns:
            A model with information about the created token
        """

        response = await self.http_client.post(
            f"{self.key.ui_url}/public-api/tokens",
            json={
                "name": name,
                "permissions": permissions,
                "comment": comment,
            },
        )

        response.raise_for_status()

        return SandboxCreateTokenResponse.model_validate(await response.json())

    async def delete_api_token(self, token_id: int) -> None:
        """
        Delete the Public API token

        Args:
            token_id: id of the PublicAPI token in the database
        """

        response = await self.http_client.delete(f"{self.key.ui_url}/public-api/tokens/{token_id}")

        response.raise_for_status()

    def __del__(self) -> None:
        if not self.session.closed:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
