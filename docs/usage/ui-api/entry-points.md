You can manage sources using the API.

!!! note "Note"

    This is not a super stable API yet and may be improved in the future.

### Get a list of possible sources to check with their parameters

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    entry_points_types = await sandbox.ui.get_entry_points_types()
    print(entry_points_types)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_entry_points_types(self) -> SandboxEntryPointsTypesResponse:
        """
        Get a list of possible sources to check with their parameters

        Returns:
            List of possible sources

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(f"{self.key.ui_url}/entry-points-types")

        response.raise_for_status()

        return SandboxEntryPointsTypesResponse.model_validate(await response.json())
    ```

### Get a list of added sources for verification

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    entry_points = await sandbox.ui.get_entry_points()
    print(entry_points)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_entry_points(self) -> SandboxEntryPointsResponse:
        """
        Get a list of added sources for analysis

        Returns:
            EntryPoints model

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(f"{self.key.ui_url}/entry-points")

        response.raise_for_status()

        return SandboxEntryPointsResponse.model_validate(await response.json())
    ```

### Create a new source

!!! warning "Warning"

    Creating a new source requires special configuration. Not all parameters may be suitable for each source type.

    It is recommended to study the documentation, or find out the necessary parameters through the dev tools in the browser.

```py title="Code example" hl_lines="17-28"
import asyncio

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import (
    EntryPointSettings,
    EntryPointToken,
    EntryPointTypeUI,
    SandboxCreateEntryPointRequest,
)


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    await sandbox.ui.create_entry_point(
        SandboxCreateEntryPointRequest(
            name="test-source",
            type=EntryPointTypeUI.scan_api,
            settings=EntryPointSettings(
                token=EntryPointToken(
                    id=1337,
                    name="test-token",
                )
            ),
        )
    )

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def create_entry_point(self, parameters: SandboxCreateEntryPointRequest) -> None:
        """
        Add a new analysis source

        Args:
            parameters:
                Parameters for request

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.post(
            f"{self.key.ui_url}/entry-points",
            json=parameters.dict(),
        )

        response.raise_for_status()
    ```

### Get full information about a specific source

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    info = await sandbox.ui.get_entry_point("...")
    print(info)

asyncio.run(main())
```

!!! example "Get info about all sources on system"

    ```py hl_lines="13-15"
    import asyncio

    from ptsandbox import Sandbox
    from ptsandbox.models import SandboxKey


    async def main():
        sandbox = Sandbox(SandboxKey(...))

        await sandbox.ui.authorize()

        entry_points = await sandbox.ui.get_entry_points()
        for entry_point in entry_points.data:
            info = await sandbox.ui.get_entry_point(entry_point.id)
            print(info.data.name, info.data.enabled)

    asyncio.run(main())
    ```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_entry_point(self, entry_point_id: str) -> SandboxEntryPointResponse:
        """
        Get information about the analysis source

        Args:
            entry_point_id:
                Name of entry point

        Returns:
            EntryPoint model

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(f"{self.key.ui_url}/entry-points/{entry_point_id}")

        response.raise_for_status()

        return SandboxEntryPointResponse.model_validate(await response.json())
    ```

### Remove the source from the system

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    await sandbox.ui.delete_entry_point("...")

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def delete_entry_point(self, entry_point_id: str) -> None:
        """
        Delete the analysis source

        Args:
            entry_point_id:
                ID of entry point

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.delete(f"{self.key.ui_url}/entry-points/{entry_point_id}")

        response.raise_for_status()
    ```

### Get a list of tasks from a specific source

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    tasks = await sandbox.ui.get_entry_point_tasks("....")
    print(tasks.tasks)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_entry_point_tasks(
        self,
        entry_point_id: str,
        query: str = "",
        limit: int = 20,
        offset: int = 0,
        utc_offset_seconds: int = 0,
        next_cursor: str | None = None,
    ) -> SandboxTasksResponse:
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
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        data: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "utcOffsetSeconds": utc_offset_seconds,
        }

        if next_cursor is not None:
            data.update({"nextCursor": next_cursor})

        response = await self.http_client.get(f"{self.key.ui_url}/entry-points/{entry_point_id}/tasks", params=data)

        response.raise_for_status()

        return SandboxTasksResponse.model_validate(await response.json())
    ```

### Download logs from the source

```py title="Code example" hl_lines="12-14"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    async with aiofiles.open("./logs.zip", "wb") as fd:
        async for chunk in sandbox.ui.get_entry_point_logs("..."): # (1)!
            await fd.write(chunk)

asyncio.run(main())
```

1. Since the size of the logs can reach several gigabytes, the response is returned as an asynchronous iterator, so as not to store all the information in the application's memory.

??? quote "Source code `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_entry_point_logs(self, entry_point_id: str) -> AsyncIterator[bytes]:
        """
        Download logs of a specific source

        Args:
            entry_point_id:
                ID of entry point

        Returns:
            Archive with logs

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        response = await self.http_client.get(f"{self.key.ui_url}/entry-points/{entry_point_id}/logs")

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk
    ```
