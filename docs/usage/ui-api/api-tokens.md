Manage API tokens in the sandbox.

## Get listing of current Public API tokens

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    tokens = await sandbox.ui.get_api_tokens()
    print(tokens)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._tokens.TokensMixin.get_api_tokens

## Create a new Public API token

```py title="Code example" hl_lines="3 9-16"
import asyncio
from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import TokenPermissions

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    token = await sandbox.ui.create_api_token(
        name="test-token",
        permissions=[
            TokenPermissions.SCAN_WITH_EXTENDED_SETTINGS,
            TokenPermissions.SCAN_WITH_PREDEFINED_SETTINGS,
        ],
        comment="test-comment",
    )
    print(token)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._tokens.TokensMixin.create_api_token

## Delete the Public API token

```py title="Code example" hl_lines="9"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    await sandbox.ui.delete_api_token(token_id=1337)

asyncio.run(main())
```

::: ptsandbox.sandbox.ui._tokens.TokensMixin.delete_api_token
