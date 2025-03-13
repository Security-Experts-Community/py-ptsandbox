## Check API Status

```py title="Code example" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    status = await sandbox.check_health()
    print(status)
```

??? quote "Response model in `ptsandbox/models/api/maintenance.py`"

    ```py
    class CheckHealthResponse(BaseResponse):
        """
        Healthcheck results
        """

        class Data(BaseModel):
            status: str
            """
            Health status
            """

        data: Data
    ```

## Get product version

```py title="Code example" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    version = await sandbox.get_version()
    print(version)
```

??? quote "Response model in `ptsandbox/models/api/maintenance.py`"

    ```py
    class GetVersionResponse(BaseResponse):
        """
        Get information about product
        """

        class Data(BaseModel):
            version: str
            """
            Product version, for example '5.11.0.12345'
            """

            edition: str
            """
            Filled in for test builds or certification builds.
            """

        data: Data
    ```
