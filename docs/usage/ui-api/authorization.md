Due to the specific API, not all useful functions are available directly through the `Public API`. Therefore, a connector to the UI API was written for this purpose.

```py title="Code example" hl_lines="16"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
        ui=SandboxKey.UI(
            login="login",
            password="password",
        ),
    )

    sandbox = Sandbox(key)
    await sandbox.ui.authorize() # (1)!

asyncio.run(main())
```

1. You must log in before using the API.

Sometimes it becomes necessary to use the UI API without access to the Public API.
To do this, you can initialize the key in this way:

```py title="Code example" hl_lines="7"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    key = SandboxKey(
        name="test-ui-1",
        key="", # (1)!
        host="10.10.10.10",
        ui=SandboxKey.UI(
            login="login",
            password="password",
        ),
    )

    sandbox = Sandbox(key)
    await sandbox.ui.authorize()
```

1. Just pass an empty `key` field
