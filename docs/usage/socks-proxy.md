In some environments, it is not possible to access the Internet directly, you can use the `socks5` proxy for this:

```python
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(
        key=SandboxKey(...),
        proxy="socks5://10.10.10.30"
    )
```
