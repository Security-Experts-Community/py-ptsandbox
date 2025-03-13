You can manage api tokens that are in the sandbox.

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

??? quote "Response model in `ptsandbox/models/ui/tokens.py`"

    ```py
    class SandboxTokensResponse(BaseModel):
        """
        Listing of current Public API tokens
        """

        total: int
        """
        The number of tokens in the system
        """

        entries: list[Token] = []
        """
        List of tokens
        """
    ```

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

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    async def create_api_token(
        self,
        name: str,
        permissions: list[TokenPermissions],
        comment: str = "",
    ) -> SandboxCreateTokenResponse:
        """
        Create a new Public API token

        Args:
            name: token name
            permissions: permissions for the token
            comment: additional information about the token

        Returns:
            A model with information about the created token
        """

        response = await self.http_client.post(
            f"{self.key.ui_url}/public-api/tokens",
            json={
                "name": name,
                "permissions": permissions,
                "comment": comment,
            },
        )

        response.raise_for_status()

        return SandboxCreateTokenResponse.model_validate(await response.json())
    ```

??? quote "Response model in `ptsandbox/models/ui/tokens.py`"

    ```py
    class SandboxCreateTokenResponse(Token):
        token: str
        """
        The secret value of the token, which is shown only when creating a new PublicAPI token.
        """

        key: str
        """
        Hash of the secret value
        """
    ```

## Delete the Public API token

```py title="Code example" hl_lines="9"
import asyncio
from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import TokenPermissions

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    await sandbox.ui.delete_api_token(token_id=1337)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    async def delete_api_token(self, token_id: int) -> None:
        """
        Delete the Public API token

        Args:
            token_id: id of the PublicAPI token in the database
        """

        response = await self.http_client.delete(f"{self.key.ui_url}/public-api/tokens/{token_id}")

        response.raise_for_status()
    ```
