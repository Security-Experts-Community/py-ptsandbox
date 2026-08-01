You can get information about the **B**ehavioral **A**nalysis **queue**.

By default, this returns all currently running jobs.

```py title="Code example" hl_lines="9-10"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    baqueue = await sandbox.ui.get_baqueue_tasks()
    for task in baqueue.tasks:
        print(task.object_name, task.state)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._tasks.TasksMixin.get_baqueue_tasks
