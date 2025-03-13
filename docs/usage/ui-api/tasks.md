## Get all tasks

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    tasks = await sandbox.ui.get_tasks()
    print(tasks)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

## Export in csv

```py title="Code example" hl_lines="9-11"
import asyncio
import aiofiles
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    async with aiofiles.open("./tasks.csv", "wb") as fd:
        async for chunk in sandbox.ui.get_tasks_csv():
            await fd.write(chunk)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

## Get filter values

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    values = await sandbox.ui.get_tasks_filter_values()
    print(values)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

## Task

### Summary

```py title="Code example" hl_lines="9"
import asyncio
from uuid import UUID
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    summary = await sandbox.ui.get_task_summary(UUID("..."))
    print(summary)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

### Get a tree of artifacts for a specific task

```py title="Code example" hl_lines="9"
import asyncio
from uuid import UUID
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    summary = await sandbox.ui.get_task_tree(UUID("..."))
    print(summary)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

### Download all the artifacts of the task

```py title="Code example" hl_lines="10-12"
import asyncio
import aiofiles
from uuid import UUID
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    async with aiofiles.open("artifacts.zip", "wb") as fd:
        async for chunk in sandbox.ui.get_task_artifacts(UUID("...")):
            await fd.write(chunk)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```

### Get scan result for a specific artifact

```py title="Code example" hl_lines="11-12"
import asyncio
from uuid import UUID
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    scan_id = UUID("...")
    tree = await sandbox.ui.get_task_tree(scan_id)
    for children in tree.children:
        scan = await sandbox.ui.get_task_artifact_scans(scan_id, children.node_id)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```
