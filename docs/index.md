# Overview

<figure markdown="span">
    ![Logo](./assets/logo_with_text.svg){ width="700"}
    <figcaption>Async API connector for PT Sandbox instances</figcaption>
</figure>

## Highlights

- Fully typed
- Completely asynchronous
- Just a modern Python

## Installation

=== "PyPI"

    ```sh
    pip install ptsandbox
    ```

=== "uv"

    ```sh
    uv add ptsandbox
    ```

=== "nix"

    ```nix
    inputs.py-ptsandbox.url = "github:Security-Experts-Community/py-ptsandbox";
    ```

## Examples

`Sandbox` supports the async context manager protocol, so you don't need to manually close HTTP sessions:

```py
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main() -> None:
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    async with Sandbox(key) as sandbox:
        print(await sandbox.api.get_images())

asyncio.run(main())
```

!!! warning "Resource management"

    You are responsible for calling `close()` when you're done with the `Sandbox` instance. Failing to do so leaks HTTP connections and may exhaust the connection pool. The async context manager (`async with`) handles this automatically.

You can also use `Sandbox` without the context manager — just call `close()` when you're done:

```py
sandbox = Sandbox(key)
try:
    print(await sandbox.api.get_images())
finally:
    await sandbox.close()
```

Getting system settings using the UI API:

```py
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

    async with Sandbox(key) as sandbox:
        # You must log in before using the UI API
        await sandbox.ui.authorize()
        print(await sandbox.ui.get_system_settings())

asyncio.run(main())
```
