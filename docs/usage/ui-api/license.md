## Get information about license

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    license = await sandbox.ui.get_license()
    print(license)

asyncio.run(main())
```

!!! tip "Check if the license has expired or not"

    ```py
    import asyncio
    from datetime import datetime, timezone

    from ptsandbox import Sandbox
    from ptsandbox.models import SandboxKey


    async def main():
        key = SandboxKey(...)
        sandbox = Sandbox(key)

        await sandbox.ui.authorize()

        response = await sandbox.ui.get_license()
        if datetime.now(tz=timezone.utc) > response.data.license.expiration_time:
            print("License expired")
        else:
            print(f"License ok, expires in: {response.data.license.expiration_time}")


    asyncio.run(main())
    ```

??? quote "Response model in `ptsandbox/models/ui/license.py`"

    ```py
    class SandboxLicenseResponse(BaseModel):
        """
        License status and details
        """

        class Data(BaseModel):
            class UpdateStatus(BaseModel):
                """
                Information about the last attempt to update the license
                """

                error: LicenseUpdateError
                """
                Error if the status is FAILED
                """

                last_check_status: Literal["SUCCESS", "FAILED"] = Field(alias="lastCheckStatus")

                last_check_time: AwareDatetime = Field(alias="lastCheckTime")

                last_success_check_time: AwareDatetime = Field(alias="lastSuccessCheckTime")

                license_update_time: AwareDatetime = Field(alias="licenseUpdateTime")
                """
                When the license itself was updated, not when it was checked
                """

                product: Literal["Sandbox", "MultiScanner"]
                """
                Product type
                """

            class License(BaseModel):
                class NodesLimit(BaseModel):
                    multiscanner: int = Field(alias="multiScanner")
                    sandbox_high_performance: int = Field(alias="sandboxHighPerformance")
                    sandbox_low_performance: int = Field(alias="sandboxLowPerformance")

                class Performance(BaseModel):
                    """
                    Bandwidth by traffic type
                    """

                    type: LicensePerformanceType
                    limit: int

                class Sandbox(BaseModel):
                    enabled: bool
                    """
                    Is behavioral analysis allowed?
                    """

                    images: list[str]
                    """
                    Images that can be used in behavioral analysis
                    """

                class Telemetry(BaseModel):
                    enabled: bool
                    """
                    Is telemetry enabled
                    """

                entry_points: list[LicenseEntryPoint] = Field(alias="entryPoints")
                """
                Allowed entrypoints
                """

                expiration_time: AwareDatetime = Field(alias="expirationTime")
                """
                License expiration date
                """

                external_av_engines: list[LicenseAvEngine] = Field(alias="externalAvEngines")
                """
                Allowed external engines
                """

                files_per_hour: int = Field(alias="filesPerHour")
                """
                Throughput capacity
                """

                grace_period: int = Field(alias="gracePeriod")
                """
                The number of grace period days in seconds
                """

                perpetual: bool
                """
                Is the license permanent
                """

                internal_av_engines: list[LicenseAvEngine] = Field(alias="internalAvEngines")
                """
                Allowed internal engines
                """

                is_entry_points_blocking_mode: bool = Field(alias="isEntryPointsBlockingMode")
                """
                Is blocking mode allowed?
                """

                license_version: int = Field(default=2, alias="licenseVersion")
                """
                License version
                """

                nodes_limit: NodesLimit = Field(alias="nodesLimit")
                """
                Maximum number of nodes by type
                """

                number: int
                """
                License number issued
                """

                performance: list[Performance] = []
                """
                Bandwidth by traffic type
                """

                sandbox: Sandbox

                telemetry: Telemetry

            state: LicenseStatus
            """
            License status - is there, is it expired
            """

            serial_number: str = Field(alias="serialNumber")
            """
            Serial number of the current license
            """

            update_status: UpdateStatus = Field(alias="updateStatus")

            license: License

        data: Data
    ```

## Update current license

```py title="Code example" hl_lines="12"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    update_result = await sandbox.ui.update_license()
    print(update_result)

asyncio.run(main())
```

??? quote "Response model in `ptsandbox/models/ui/license.py`"

    ```py
    class SandboxLicenseUpdateResponse(BaseModel):
        """
        License update attempt status
        """

        class Data(BaseModel):
            status: Literal["SUCCESS", "FAILED"]

            error: LicenseUpdateError

        data: Data
    ```
