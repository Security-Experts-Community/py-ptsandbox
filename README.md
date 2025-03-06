# py-ptsandbox

Async API connector for PT Sandbox instances.

## Installation

You can use the following command to install the package:

```sh
python3 -m pip install ptsandbox 
```

## Usage

An example of library usage:

```python
import asyncio
from ptsandbox import SandboxKey, Sandbox


async def main() -> None:
    key = SandboxKey(name="test-key-1", key="<TOKEN_FROM_SANDBOX>", host="10.10.10.10")
    sandbox = Sandbox(key=key)

    await sandbox.new_scan_v2(...)


if __name__ == "__main__":
    asyncio.run(main())
```
