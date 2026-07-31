## Get information about the license

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    license = await sandbox.ui.get_license()
    print(license)

asyncio.run(main())
```

!!! tip "Check if the license has expired or not"

    ```py
    import asyncio
    from datetime import datetime, timezone

    from ptsandbox import Sandbox
    from ptsandbox.models import SandboxKey


    async def main():
        key = SandboxKey(...)
        sandbox = Sandbox(key)

        await sandbox.ui.authorize()

        response = await sandbox.ui.get_license()
        if datetime.now(tz=timezone.utc) > response.data.license.expiration_time:
            print("License expired")
        else:
            print(f"License ok, expires in: {response.data.license.expiration_time}")


    asyncio.run(main())
    ```

::: ptsandbox.sandbox.ui._system.SystemMixin.get_license

## Update the current license

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    update_result = await sandbox.ui.update_license()
    print(update_result)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._system.SystemMixin.update_license
