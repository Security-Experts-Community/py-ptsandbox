from pydantic import BaseModel, Field


class SandboxAVEnginesResponse(BaseModel):
    class Data(BaseModel):
        class EnginesInfo(BaseModel):
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

                errors: list[Error] = []
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

            kaspersky: Engine | None = None
            bitdefender: Engine | None = None
            symantec: Engine | None = None
            eset: Engine | None = None
            drweb: Engine | None = None
            clamav: Engine | None = None
            avast: Engine | None = None
            avira: Engine | None = None

        engines_info: EnginesInfo = Field(alias="enginesInfo")

    data: Data


SandboxAVEnginesResponse.model_rebuild()
