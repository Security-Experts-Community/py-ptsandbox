```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    engines = await sandbox.ui.get_av_engines()
    print(engines)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_av_engines(self) -> SandboxAVEnginesResponse:
        """
        Get information about antivirus scanners

        Returns:
            A model with information about all antiviruses
        """

        response = await self.http_client.get(f"{self.key.ui_url}/av-engines")

        response.raise_for_status()

        return SandboxAVEnginesResponse.model_validate(await response.json())
    ```
