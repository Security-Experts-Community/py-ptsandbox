# Overview

<figure markdown="span">
    ![Logo](./assets/logo_with_text.svg){ width="700"}
    <figcaption>Async API connector for PT Sandbox instances</figcaption>
</figure>

## Highlights

- Fully typed
- Completely asynchronous
- Just a modern python

## Installation

=== "PyPi"

    ```sh
    pip install ptsandbox
    ```

=== "uv"

    ```sh
    uv add ptsandbox
    ```

=== "nix"

    ```
    TBA
    ```

## Examples

Getting a list of all installed images using the API:

```py
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main() -> None:
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)
    print(await sandbox.api.get_images())

asyncio.run(main())
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

    sandbox = Sandbox(key)
    # You must log in before using the UI API
    await sandbox.ui.authorize()

    print(await sandbox.ui.get_system_settings())

asyncio.run(main())
```
