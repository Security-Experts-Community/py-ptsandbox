You can manage sources using the API.

!!! note "Note"

    This API is not yet stable and may change in the future.

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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.get_entry_points_types

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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.get_entry_points

### Create a new source

!!! warning "Warning"

    Creating a new source requires special configuration. Not all parameters may be suitable for each source type.

    Study the documentation, or inspect the required parameters using browser dev tools.

```py title="Code example" hl_lines="17-28"
import asyncio

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import (
    EntryPointSettings,
    EntryPointToken,
    EntryPointType,
    SandboxCreateEntryPointRequest,
)


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    await sandbox.ui.create_entry_point(
        SandboxCreateEntryPointRequest(
            name="test-source",
            type=EntryPointType.SCAN_API,
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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.create_entry_point

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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.get_entry_point

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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.delete_entry_point

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

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.get_entry_point_tasks

### Download logs from the source

```py title="Code example" hl_lines="12-14"
import asyncio

import aiofiles

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

1. Log sizes can reach several gigabytes. The response is an async iterator to avoid loading everything into memory.

::: ptsandbox.sandbox.ui._entry_points.EntryPointsMixin.get_entry_point_logs
