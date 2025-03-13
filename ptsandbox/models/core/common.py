"""Модели, которые аналогичны и для API, и для UI"""

from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field

from ptsandbox.models.core.base import BaseResponse
from ptsandbox.models.core.enum import (
    ArtifactType,
    EngineSubsystem,
    LogType,
    NetworkObjectType,
    SandboxImageType,
    ScanState,
    Verdict,
)


class SandboxResult(BaseModel):
    """
    File analysis result
    """

    scan_state: ScanState
    """
    Analysis status
    """

    duration: float
    """
    The duration of the analsysis in seconds.

    It is recorded only in the general results (in the JSON object `data → result`).
    """

    duration_full: float
    """
    The duration of the check, taking into account the record in the database or the time of the request.
    """

    verdict: Verdict | None = None
    """
    Analysis verdict
    """

    threat: str | None = None
    """
    Type of malware
    """

    errors: list[BaseResponse.Error] = []
    """
    Errors that occurred during analysis.
    """


class NetworkObject(BaseModel):
    type: NetworkObjectType
    """
    Type of network object
    """

    value: str
    """
    The value of the network object
    """


class SuspiciousBehaviors(BaseModel):
    """
    The correlation rule
    """

    name: str
    """
    Name of the rule
    """

    version: str | None = None
    """
    Version of the rule
    """

    mitre_threat_id: str = Field(
        validation_alias=AliasChoices(
            "mitre_threat_id",
            "mitreThreatId",
        )
    )
    """
    The MITRE Threat ID
    """

    weight: int
    """
    The weight of the rule (how much it affects the overall detection)
    """

    id: str | None = None
    description: str | None = None


class Detection(BaseModel):
    """
    Detected malware
    """

    detect: str
    """
    Malware
    """

    threat: str
    """
    Type of malware
    """


class Log(BaseModel):
    """
    A copy of network traffic, video recording, event logs, graph, debug files, mail headers.
    """

    type: LogType
    """
    Log type
    """

    file_uri: str
    """
    ID of the file used for downloading
    """

    file_name: str
    """
    File name
    """


class SandboxImageInfo(BaseModel):
    """
    Information about the VM image
    """

    class OS(BaseModel):
        """
        Information about the operating system of the virtual machine
        """

        name: str
        """
        Name of the operating system
        """

        version: str
        """
        Operating system version
        """

        architecture: str
        """
        Processor architecture supported by the operating system
        """

        service_pack: str | None = Field(
            default=None,
            validation_alias=AliasChoices("service_pack", "servicePack"),
        )
        """
        The name of the operating system update package
        """

        locale: str
        """
        Operating system locale
        """

    image_id: str | None = Field(default=None, validation_alias=AliasChoices("image_id", "name", "id"))
    """
    ID of the VM image

    The new UI began to return the name of the image. However, in the form of a name.
    """

    type: SandboxImageType | None = None
    """
    The type of image.
    """

    version: str | None = None
    """
    Version of the VM image
    """

    os: OS | None = None
    """
    Information about the operating system of the virtual machine image
    """


class Artifact(BaseModel):
    """
    A file, email, or other object
    """

    class FileInfo(BaseModel):
        """
        Information about the scanned file

        Filled in for binary objects
        """

        class FileInfoDetails(BaseModel):
            """
            The type of the nested object depends on the type value.
            """

            class ProcessDump(BaseModel):
                """
                It is filled in for process memory dumps.

                Type is equal to PROCESS_DUMP
                """

                process_name: str
                """
                The name of the process
                """

                process_id: int
                """
                The process ID (PID).
                """

                dump_trigger: str
                """
                The reason for extracting the dump
                """

                dump_create_time: float
                """
                Dump creation time
                """

            process_dump: ProcessDump

        file_uri: str
        """
        ID of the file used for downloading
        """

        file_path: str
        """
        The path to the file (excluding the root file of the structure), including its title.

        For example, for the file `readme.txt` at the root of the archive
        `archive.zip` will be specified as the value of this field.
        `readme.txt `, is an empty value for the archive itself.
        """

        mime_type: str
        """
        The MIME type of the artifact is determined during the verification process.
        """

        md5: str
        """
        MD5 hash of the file
        """

        sha1: str
        """
        SHA1 hash of the file
        """

        sha256: str
        """
        SHA256 hash of the file
        """

        ssdeep: str | None = None
        """
        SSDEEP hash of the file
        """

        size: int
        """
        File size in bytes
        """

        details: FileInfoDetails | None = None

    class EngineResult(BaseModel):
        class Details(BaseModel):
            class Sandbox(BaseModel):
                """
                Detailed information about behavioral analysis (if enabled)
                """

                class Stage(BaseModel):
                    """
                    The result of a single scan stage with bootkitmon
                    """

                    result: SandboxResult
                    """
                    The overall result of the check
                    """

                    detections: list[Detection] = []
                    """
                    A list of BA detections at this stage
                    """

                    logs: list[Log] = []
                    """
                    A copy of network traffic, video recording, event logs, graph, debug files, mail headers
                    """

                    artifacts: list["Artifact"] = []
                    """
                    Virtual machine artifacts are files created during behavioral analysis.
                    """

                    analysis_duration: float | None = None
                    """
                    The actual duration of the behavioral analysis in seconds
                    """

                    suspicious_behaviors: list[SuspiciousBehaviors] = []
                    """
                    List of triggered correlation rules
                    """

                image: SandboxImageInfo
                """
                Information about the VM image
                """

                logs: list[Log]
                """
                A copy of network traffic, video recording, event logs, graph, debug files, mail headers.
                """

                artifacts: list["Artifact"] | None = None
                """
                Virtual machine artifacts are files created during behavioral analysis.
                """

                stages: list[Stage] = []
                """
                The stages of bootkit analysis.
                """

                analysis_duration: float | None = None
                """
                The actual duration of the behavioral analysis in seconds
                """

                bootkitmon: bool | None = None
                """
                Was the bootkitmon analysis performed during BA
                """

                network_objects: list[NetworkObject] = []
                """
                Network objects (url, ip, domain)
                """

                suspicious_behaviors: list[SuspiciousBehaviors] = []
                """
                List of triggered correlation rules
                """

            sandbox: Sandbox | None = None
            """
            Detailed information about behavioral analysis (if enabled)
            """

        engine_subsystem: EngineSubsystem
        """
        The analysis method
        """

        engine_code_name: str
        """
        The name of the antivirus or component
        """

        engine_version: str | None = None
        """
        Antivirus or component version
        """

        database_version: str | None = None
        """
        Version of the antivirus database or knowledge base
        """

        database_time: datetime | None = None
        """
        Time to update the antivirus database or knowledge base
        """

        result: SandboxResult
        """
        The result of an antivirus or other component check
        """

        detections: list[Detection] = []
        """
        An array with a description of the detected malware
        """

        details: Details | None = None

    type: ArtifactType
    """
    The type of the analyzed object
    """

    result: SandboxResult | None = None
    """
    File analysis result
    """

    file_info: FileInfo | None = None
    """
    Information about the scanned file
    """

    engine_results: list[EngineResult] | None = None
    """
    The results of checking the file with specific antiviruses or other components
    """

    artifacts: list["Artifact"] | None = None
    """
    Files that are archived.

    If the file sent for analysis is not an archive or the allowed decompression depth is exceeded, the `artifacts` array is empty.
    """

    network_objects: list[NetworkObject]
    """
    Network objects (url, ip, domain)
    """

    def find_sandbox_result(self) -> EngineResult | None:
        if self.type == ArtifactType.ARCHIVE:
            if self.artifacts is not None:
                return self.artifacts[0].find_sandbox_result()
            return None
        if self.engine_results is not None:
            for result in self.engine_results:
                if result.engine_subsystem == EngineSubsystem.SANDBOX:
                    return result
        if self.artifacts is not None:
            for artifact in self.artifacts:
                if (sb_result := artifact.find_sandbox_result()) is not None:
                    return sb_result
        return None

    def find_static_result(self) -> EngineResult | None:
        if self.engine_results is not None:
            for result in self.engine_results:
                if result.engine_subsystem == EngineSubsystem.STATIC:
                    return result
        return None


# Solving the problem of nesting models into each other
Artifact.model_rebuild()
Artifact.EngineResult.Details.Sandbox.model_rebuild()
