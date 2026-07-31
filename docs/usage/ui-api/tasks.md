List tasks, export them to CSV, get task summaries, and browse artifact trees.

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

::: ptsandbox.sandbox.ui._tasks.TasksMixin.get_tasks

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

::: ptsandbox.sandbox.ui._tasks.TasksMixin.get_tasks_csv

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

::: ptsandbox.sandbox.ui._tasks.TasksMixin.get_tasks_filter_values

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

::: ptsandbox.sandbox.ui._tasks.TasksMixin.get_task_summary

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

::: ptsandbox.sandbox.ui._artifacts.ArtifactsMixin.get_task_tree

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

::: ptsandbox.sandbox.ui._artifacts.ArtifactsMixin.get_task_artifacts

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

::: ptsandbox.sandbox.ui._artifacts.ArtifactsMixin.get_task_artifact_scans
