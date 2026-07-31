from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ptsandbox.models.core.base import BaseResponse


class SandboxAVEnginesResponse(BaseResponse):
    class Data(BaseModel):
        class Engine(BaseModel):
            class Error(BaseModel):
                code: str
                message: str

            distribution_type: str = Field(alias="distributionType")
            """
            Distribution type
            """

            engine_update_time: int = Field(alias="engineUpdateTime")
            """
            The time of the last update of the antivirus engine
            """

            distribution_pack: str = Field(alias="distributionPack")

            distribution_version: str = Field(alias="distributionVersion")
            """
            Distribution version
            """

            is_installed: bool = Field(alias="isInstalled")
            """
            Antivirus is installed
            """

            engine_version: str = Field(alias="engineVersion")
            """
            Engine version
            """

            enabled: bool
            """
            Antivirus is enabled
            """

            errors: list[Error] = Field(default_factory=list[Error])
            """
            Antivirus errors
            """

            is_initializing: bool = Field(alias="isInitializing")
            """
            Antivirus initialization status
            """

            is_ready: bool = Field(alias="isReady")
            """
            The antivirus is ready to work
            """

            database_time: int = Field(alias="databaseTime")
            """
            The time of the last database update
            """

            license_expiration: int = Field(alias="licenseExpiration")
            """
            License validity period
            """

            maintenance_status: str | None = Field(default=None, alias="maintenanceStatus")

        engines_info: dict[str, Engine] = Field(default_factory=dict, alias="enginesInfo")
        """
        Mapping of engine code name to engine info.

        Known keys: kaspersky, bitdefender, symantec, eset, drweb, clamav, avast, avira.
        New engines may appear in future API versions without library updates.
        """

    data: Data


SandboxAVEnginesResponse.model_rebuild()


class SandboxAVEngineSettingsResponse(BaseResponse):
    """Response from ``/av-engines/{item_id}`` — settings of a specific AV engine."""

    class Data(BaseModel):
        class License(BaseModel):
            content: str | None = None
            """License file content"""

            name: str | None = None
            """License file name"""

        licenses: list[License] = Field(default_factory=list[License])
        """List of licenses"""

        use_proxy_url: bool | None = Field(default=None, alias="useProxyUrl")

        update_url: str | None = Field(default=None, alias="updateUrl")

        enabled: bool

        license_expiration: int | None = Field(default=None, alias="licenseExpiration")

        distribution_pack: str | None = Field(default=None, alias="distributionPack")

        distribution_version: str | None = Field(default=None, alias="distributionVersion")

        engine_code_name: str | None = Field(default=None, alias="engineCodeName")

        maintenance_status: str | None = Field(default=None, alias="maintenanceStatus")

        # TODO: The backend returns an opaque error structure here that varies
        # across engine types. Typed once the format is documented.
        errors: list[Any] = Field(default_factory=list[Any])

    data: Data


SandboxAVEngineSettingsResponse.model_rebuild()


class SandboxAVDistributionPacksResponse(BaseResponse):
    """Response from ``/av-distribution-packs`` — list of AV distributions available for installation."""

    class Data(BaseModel):
        class License(BaseModel):
            extensions: list[str] = Field(default_factory=list[str])
            """Possible file extensions for the license"""

            multiple: bool = False
            """Whether multiple license files are allowed"""

        class Requirements(BaseModel):
            os: str | None = None
            """Required OS"""

            bit: str | None = None
            """Required architecture"""

        class Installer(BaseModel):
            name: str | None = None
            """Installer file/package name"""

            uploaded: bool = False

            requirements: SandboxAVDistributionPacksResponse.Data.Requirements | None = None

        class Files(BaseModel):
            installer: SandboxAVDistributionPacksResponse.Data.Installer | None = None

        class DistributionPack(BaseModel):
            engine_code_name: str = Field(alias="engineCodeName")
            """AV engine code name"""

            maintenance_status: str = Field(alias="maintenanceStatus")
            """Maintenance status"""

            pack: str
            """Pack name"""

            version: str
            """AV version"""

            license: SandboxAVDistributionPacksResponse.Data.License | None = None

            files: SandboxAVDistributionPacksResponse.Data.Files | None = None

        distribution_packs: list[DistributionPack] = Field(alias="distributionPacks")

    data: Data


SandboxAVDistributionPacksResponse.model_rebuild()
