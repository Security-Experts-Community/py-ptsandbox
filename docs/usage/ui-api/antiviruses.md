Get information about antivirus engines and distribution packs configured in the sandbox.

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    engines = await sandbox.ui.get_av_engines()
    print(engines)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_av_engines

### Get settings of a specific engine

```py title="Code example"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    engine = await sandbox.ui.get_av_engine("clamav")
    print(engine)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_av_engine

### Get distribution packs

```py title="Code example"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    packs = await sandbox.ui.get_av_distribution_packs()
    print(packs)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_av_distribution_packs
