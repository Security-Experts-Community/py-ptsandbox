## Get available tasks

!!! warning "Warning"

    This method may not be available on all sandbox instances. It will be available in future releases.

Use this method to list tasks without the UI API.

```py title="Example of getting the last 20 scans (default value)" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    result = await sandbox.get_tasks()
    for task in result.tasks:
        print(task.id, task.name)
```

::: ptsandbox.sandbox.sandbox.Sandbox.get_tasks

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.get_tasks
