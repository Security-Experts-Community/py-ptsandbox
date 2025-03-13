![Image](./docs/assets/logo_with_text.svg)

<p align="center">
    <em>Async API connector for PT Sandbox instances</em>
</p>

---

**Documentation**: <a href="https://security-experts-community.github.io/py-ptsandbox/">https://security-experts-community.github.io/py-ptsandbox/</a>

**Source Code**: <a href="https://github.com/Security-Experts-Community/py-ptsandbox">https://github.com/Security-Experts-Community/py-ptsandbox</a>

---

## Installation

You can use the following command to install the package:

PyPI:

```sh
python3 -m pip install ptsandbox
```

uv:

```
uv add ptsandbox
```

Nix:

```
TBA
```

<p align="middle">
    <img width="50%" src="./docs/assets/pic_right.svg">
</p>

## Usage

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
