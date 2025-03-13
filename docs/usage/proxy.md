In some environments, it is not possible to access the internet directly, you can use the proxy for this:

```py title="Code example" hl_lines="6"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(
        key=SandboxKey(...),
        proxy="socks5://10.10.10.30"
    )
```

The library uses [aiohttp-socks](https://github.com/romis2012/aiohttp-socks), so you can view the supported proxy types in it.
