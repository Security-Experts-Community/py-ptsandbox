## Get available tasks

!!! warning "Warning"

    So far, this method may not be available on all instances of the sandbox.
    It will appear in future releases.

This method is needed to get a list of tasks without using the UI API.

```py title="Example of getting the last 20 scans (default value)" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    result = await sandbox.get_tasks()
    for task in result.tasks:
        print(task.id, task.name)
```
