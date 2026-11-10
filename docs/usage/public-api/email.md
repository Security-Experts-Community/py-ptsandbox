# Extract email headers

Upload an email and get its headers.

```py title="Code example"
import asyncio
from pathlib import Path
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    async with Sandbox(key=SandboxKey(...)) as sandbox:
        with open("./email-headers", "wb") as fd:
            async for chunk in sandbox.get_email_headers(Path("./email.bin")):
                await asyncio.to_thread(fd.write, chunk)
```

::: ptsandbox.sandbox.sandbox.Sandbox.get_email_headers

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.get_email_headers
