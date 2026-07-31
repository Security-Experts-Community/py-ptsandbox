## Check API Status

```py title="Code example" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    status = await sandbox.api.get_health_status()
    print(status)
```

::: ptsandbox.sandbox.api._maintenance.MaintenanceMixin.get_health_status

## Get product version

```py title="Code example" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    version = await sandbox.api.get_version()
    print(version)
```

::: ptsandbox.sandbox.api._maintenance.MaintenanceMixin.get_version

## Lifecycle

The `Sandbox` class manages HTTP sessions for both the Public API and UI API. Always close the sessions when you're done, either explicitly or via the async context manager:

```py title="Code example"
from ptsandbox import Sandbox, SandboxKey

# Using the async context manager (recommended)
async with Sandbox(SandboxKey(...)) as sandbox:
    status = await sandbox.api.get_health_status()

# Or explicitly
sandbox = Sandbox(SandboxKey(...))
try:
    status = await sandbox.api.get_health_status()
finally:
    await sandbox.close()
```

::: ptsandbox.sandbox.sandbox.Sandbox.close
