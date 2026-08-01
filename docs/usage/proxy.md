In some environments, you can't access the internet directly. You can use a proxy:

```py title="Code example" hl_lines="6"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(
        key=SandboxKey(...),
        proxy="socks5://10.10.10.30"
    )
```

The library uses [aiohttp-socks](https://github.com/romis2012/aiohttp-socks). See its documentation for supported proxy types.
