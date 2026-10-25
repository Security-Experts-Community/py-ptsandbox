from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, Field

from ptsandbox.models import (
    LicenseAvEngine,
    LicenseEntryPoint,
    LicensePerformanceType,
    LicenseStatus,
    LicenseUpdateError,
)
from ptsandbox.models.core.base import BaseResponse, SandboxModel


class SandboxLicenseResponse(BaseResponse):
    """
    License status and details
    """

    class Data(SandboxModel):
        class UpdateStatus(SandboxModel):
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

        class License(SandboxModel):
            class NodesLimit(SandboxModel):
                multiscanner: int = Field(alias="multiScanner")
                sandbox_high_performance: int = Field(alias="sandboxHighPerformance")
                sandbox_low_performance: int = Field(alias="sandboxLowPerformance")

            class Performance(SandboxModel):
                """
                Bandwidth by traffic type
                """

                type: LicensePerformanceType
                limit: int

            class Sandbox(SandboxModel):
                enabled: bool
                """
                Is behavioral analysis allowed?
                """

                images: list[str]
                """
                Images that can be used in behavioral analysis
                """

            class Telemetry(SandboxModel):
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

            performance: list[Performance] = Field(default_factory=list[Performance])
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


class SandboxLicenseUpdateResponse(BaseResponse):
    """
    License update attempt status
    """

    class Data(SandboxModel):
        status: Literal["SUCCESS", "FAILED"]

        error: LicenseUpdateError

    data: Data
