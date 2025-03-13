You can get information about the **B**ehavioral **A**nalysis **queue**.

By default, all jobs that are currently running are requested.

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

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
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
    ```
