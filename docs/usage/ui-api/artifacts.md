Export artifacts data and get filter values for artifact queries.

## Export in csv

```py title="Code example" hl_lines="9-11"
import asyncio
import aiofiles
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    async with aiofiles.open("./tasks.csv", "wb") as fd:
        async for chunk in sandbox.ui.get_artifacts_csv():
            await fd.write(chunk)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._artifacts.ArtifactsMixin.get_artifacts_csv

## Get filter values

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    values = await sandbox.ui.get_artifacts_filter_values()
    print(values)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._artifacts.ArtifactsMixin.get_artifacts_filter_values
