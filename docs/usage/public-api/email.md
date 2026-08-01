Upload an email and get its headers.

```py title="Code example" hl_lines="8"
import aiofiles
from pathlib import Path
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    async with aiofiles.open("./email-headers", "wb") as fd:
        async for chunk in sandbox.get_email_headers(Path("./email.bin")):
            await fd.write(chunk)
```

::: ptsandbox.sandbox.sandbox.Sandbox.get_email_headers

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.get_email_headers
