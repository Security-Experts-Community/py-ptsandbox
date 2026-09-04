In some environments, you can't access the internet directly. You can use a proxy:

```py title="Code example" hl_lines="5-9"
from ptsandbox import Sandbox, SandboxKey


async def example() -> None:
    async with Sandbox(
        key=SandboxKey(...),
        proxy="socks5://10.10.10.30",
    ) as sandbox:
        await sandbox.api.get_health_status()
```

The library uses [aiohttp-socks](https://github.com/romis2012/aiohttp-socks). See its documentation for supported proxy types.
