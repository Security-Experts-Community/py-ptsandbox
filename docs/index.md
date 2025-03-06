# Overview

**py-ptsandbox** - is an asynchronous python library for [PT Sandbox](https://global.ptsecurity.com/products/sandbox) instances.

## Highlights

- Completely asynchronous
- Fully typed

## Installation

### PyPI

```sh
pip install ptsandbox
```

### Nix

**TBA**

### uv

```sh
uv add ptsandbox
```

## Examples

```py
import asyncio
from ptsandbox import SandboxKey, Sandbox

async def main() -> None:
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10", # or "sandbox.example.com"
    )
    sandbox = Sandbox(key=key)

    print(await sandbox.api.get_images())


if __name__ == "__main__":
    asyncio.run(main())
```
