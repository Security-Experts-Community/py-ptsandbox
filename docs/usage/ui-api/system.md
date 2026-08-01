You can get information about system components, including cluster status and component health.

## Status

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    status = await sandbox.ui.get_system_status()
    print(status)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_status

### Cluster status

```py title="Code example"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    cluster = await sandbox.ui.get_system_cluster_status()
    print(cluster)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_cluster_status

### Components status

```py title="Code example"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    components = await sandbox.ui.get_system_components_status()
    print(components)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_components_status

## Settings

### Get information

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    settings = await sandbox.ui.get_system_settings()
    print(settings)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_settings

### Update information

```py title="Code example" hl_lines="9-15"
import asyncio
from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import SandboxUpdateSystemSettingsRequest

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    await sandbox.ui.update_system_settings(
        SandboxUpdateSystemSettingsRequest(
            quarantine=SandboxUpdateSystemSettingsRequest.Quarantine(
                retention_period=30000,
            )
        )
    )

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.update_system_settings

## Version

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    version = await sandbox.ui.get_system_version()
    print(version)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_version

## System Logs

```py title="Code example" hl_lines="9-11"
import aiofiles
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    async with aiofiles.open("logs.zip", "wb") as fd:
        async for chunk in sandbox.ui.get_system_logs(): # (1)!
            await fd.write(chunk)

asyncio.run(main())
```

1. :warning: Without parameters, all logs will be downloaded. This can be several gigabytes.

::: ptsandbox.sandbox.ui._system.SystemMixin.get_system_logs

## License

License management methods are documented on the [License](license.md) page.
