from typing import NotRequired
from uuid import UUID

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from ptsandbox.models.core import (
    Artifact,
    BaseRequest,
    BaseResponse,
    SandboxException,
    SandboxResult,
    VNCMode,
)
from ptsandbox.models.core.enum import FileInfoProperties


class DebugOptions(TypedDict):
    """
    Description of all available debugging options for very detailed scan configuration
    """

    keep_sandbox: NotRequired[bool]
    """
    Don't destroy the sandbox after scanning
    """

    skip_work: NotRequired[bool]
    """
    Perform a scan, skipping the data collection stage for analysis
    """

    extract_crashdumps: NotRequired[bool]
    """
    Extract crashdumps from the sandbox
    """

    save_debug_files: NotRequired[bool]
    """
    Save files necessary for debugging (error logs, tcpdump logs, etc)
    """

    rules_url: NotRequired[str]
    """
    Use the specified normalization and correlation rules
    The rules are specified as a link to the archive containing the compiled rules
    """

    sleep_work: NotRequired[bool]
    """
    Perform a scan, replacing the data collection stage for analysis with an equivalent waiting time
    """

    disable_syscall_hooks: NotRequired[bool]
    """
    Disable syscall hooks functionality

    Read more about these hooks in documentation
    """

    disable_dll_hooks: NotRequired[bool]
    """
    Disable dll hooks functionality

    Read more about these hooks in documentation
    """

    custom_syscall_hooks: NotRequired[str]
    """
    Use the specified list of system calls to intercept

    The list is transmitted as an http link to a file with the names of system calls

    Read more about this file in [documentation](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/debug-options/#custom_syscall_hooks)
    """

    custom_dll_hooks: NotRequired[str]
    """
    Use the specified list of system calls to intercept

    The list is transmitted as an http link to a file with the names of dll hooks for apimon plugin

    Read more about this file in [documentation](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/debug-options/#custom_dll_hooks)
    """

    disable_retries: NotRequired[bool]
    """
    Disable task re-execution in case of a scan error
    """

    enable_sanitizers: NotRequired[bool]
    """
    Enable the debugging mechanisms of the sanitizers group
    """

    allowed_outbound_connections: NotRequired[list[str]]
    """
    Whitelist of IP addresses to which connections from a VM are allowed (backconnect)
    """

    payload_completion_event: NotRequired[str]
    """
    A regular expression for the raw DRAKVUF event, signaling the end of the useful work of the sample.

    If this option is specified, sandbox-worker will calculate and log the PAYLOAD_SCAN_TIME metric.
    """

    disable_procdump_on_finish: NotRequired[bool]
    """
    Disable the functionality of removing the memory dump from the sample at the end of the observation
    """

    skip_update_time: NotRequired[bool]
    """
    Do not synchronize the time in the VM with the host
    """

    disable_manual_scan_events: NotRequired[bool]
    """
    Do not send lifecycle notifications for manual behavioral analysis (console is ready, console is closed, etc.)
    """

    bootkitmon_boot_timeout: NotRequired[int]
    """
    The maximum waiting time for VM loading in seconds (90 seconds by default)
    """

    custom_procdump_exclude: NotRequired[str]
    """
    A file with a list of processes for which memory dumps should not be removed.

    Each line in the file is a regular expression of the path to the process file on disk.

    Read more about this file in [documentation](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/debug-options/#custom_procdump_exclude)
    """

    custom_fileextractor_exclude: NotRequired[str]
    """
    A file with a list of files that should not be extracted

    Each line in the file is a regular expression of the path to the file on disk.

    Read more about this file in [documentation](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/debug-options/#custom_fileextractor_exclude)
    """

    validate_plugins: NotRequired[bool]
    """
    Check plugins for at least one event during the entire behavioral analysis
    """

    extra_vm_init_url: NotRequired[str]
    """
    Run this script in the VM immediately before launching the behavioral analysis.

    It is useful, for example, to check the network during analysis.
    """


class SandboxOptions(BaseRequest):
    """
    Parameters of behavioral analysis.

    In the absence, the source parameters are used for analysis, which are set in the system by default.
    """

    class FilterProperties(BaseModel):
        """
        Filtering a group of files by properties to send to the sandbox for analysis
        """

        pdf: list[FileInfoProperties] = []

        office: list[FileInfoProperties] = []

    enabled: bool = True
    """
    Perform a behavioral analysis
    """

    image_id: str = "win7-sp1-x64"
    """
    ID of the VM image.

    You can view it in the sandbox interface.
    """

    custom_command: str | None = None
    """
    The command to run the file.

    The `{file}` marker in the string is replaced with the path to the file.

    For example: `rundll32.exe {file},#1`
    """

    procdump_new_processes_on_finish: bool = False
    """
    Take dumps for all spawned and non-dead processes
    """

    analysis_duration: int = Field(default=120, ge=10)
    """
    The duration of analysis the file in seconds. minimum: 10
    """

    bootkitmon: bool = False
    """
    Perform bootkitmon analysis
    """

    analysis_duration_bootkitmon: int = Field(default=60, ge=10)
    """
    The duration of analysis at the bootkitmon stage in seconds. minimum: 10
    """

    save_video: bool = True
    """
    Save video capture of the screen
    """

    mitm_enabled: bool = True
    """
    Enable certificates injection with PT Sandbox certificates when decrypting and analyzing secure traffic
    """

    file_types: list[str] | None = None
    """
    A list of the final file types or groups of files that will be sent for behavioral analysis

    For example:
    ["adobe-acrobat/", "databases/", "executable-files/", "presentations/", "spreadsheets/", "word-processor/"]
    """

    filter_by_properties: FilterProperties | None = None
    """
    Filtering a group of files by properties to send to the sandbox for analysis
    """

    debug_options: DebugOptions = {"save_debug_files": False}
    """
    Fine-tuning
    """


class SandboxOptionsAdvanced(BaseRequest):
    """
    Run an advanced analysis of the uploaded file in the VM without unpacking.

    Provides an opportunity to fine-tuning.

    **The options are in beta, so they may change in the future.**
    """

    class ExtraFile(BaseModel):
        """
        An additional file to be placed next to the sample
        """

        uri: str
        """
        Link to the uploaded object
        """

        name: str
        """
        Name in the VM
        """

    image_id: str = "win7-sp1-x64"
    """
    ID of the VM image.

    You can view it in the sandbox interface.
    """

    custom_command: str | None = None
    """
    The command to run the file.

    The `{file}` marker in the string is replaced with the path to the file.

    For example: `rundll32.exe {file},#1`
    """

    procdump_new_processes_on_finish: bool = False
    """
    Take dumps for all spawned and non-dead processes
    """

    analysis_duration: int = Field(default=120, ge=10)
    """
    The duration of analysis the file in seconds. minimum: 10
    """

    bootkitmon: bool = False
    """
    Perform bootkitmon analysis
    """

    analysis_duration_bootkitmon: int = Field(default=60, ge=10)
    """
    The duration of analysis at the bootkitmon stage in seconds. minimum: 10
    """

    save_video: bool = True
    """
    Save video capture of the screen
    """

    mitm_enabled: bool = True
    """
    Enable certificates injection with PT Sandbox certificates when decrypting and analyzing secure traffic
    """

    disable_clicker: bool = False
    """
    Disable auto-clicker startup

    Useful when enabling manual analysis.
    """

    skip_sample_run: bool = False
    """
    Disable sample launch
    """

    vnc_mode: VNCMode = VNCMode.DISABLED
    """
    Manual analysis mode
    """

    extra_files: list[ExtraFile] = []
    """
    A list of additional files that are placed in the VM
    """

    debug_options: DebugOptions = {"save_debug_files": False}
    """
    Fine-tuning
    """


class SandboxBaseScanTaskRequest(BaseRequest):
    """
    Base class for all scan requests
    """

    class Options(BaseModel):
        class SuspiciousFilesOptions(BaseModel):
            """
            Settings for marking files as suspicious
            """

            encrypted_not_unpacked: bool = True
            """
            Encrypted and not unpacked file
            """

            max_depth_exceeded: bool = True
            """
            Unpacking depth exceeded
            """

            office_encrypted: bool = True
            """
            Encrypted office file
            """

            office_has_macros: bool = True
            """
            Office file with macros
            """

            office_has_embedded: bool = True
            """
            Office file with embedded objects
            """

            office_has_active_x: bool = True
            """
            Office file with ActiveX controls
            """

            office_has_dde: bool = True
            """
            Office file with dynamic data exchange
            """

            office_has_remote_data: bool = True
            """
            Office file with remote data
            """

            office_has_remote_template: bool = True
            """
            Office file with remote templates
            """

            office_has_action: bool = True
            """
            Office file with Action
            """

            pdf_encrypted: bool = True
            """
            Encrypted PDF file
            """

            pdf_has_embedded: bool = True
            """
            PDF file with embedded objects
            """

            pdf_has_open_action: bool = True
            """
            PDF file with Open Action
            """

            pdf_has_action: bool = True
            """
            PDF file with Action
            """

            pdf_has_javascript: bool = True
            """
            PDF file with Javascript
            """

            pdf_protected: bool = True
            """
            Protected PDF file
            """

        analysis_depth: int = 0
        """
        The depth of the check.

        The maximum level of decomposition of objects with a hierarchical structure (archives, emails, links, etc.)
        or the decompression level of compressed files.

        If the value is 0, the check is performed without decomposition and decompression.

        The higher the number, the longer the check can take.
        """

        scan_timeout: int = Field(default=1200, ge=10, le=3600)
        """
        Maximum response time
        """

        max_execution_time: int = Field(default=3600, ge=300, le=10800)
        """
        Maximum waiting time for analysis
        """

        passwords_for_unpack: list[str] = []
        """
        List of passwords for unpacking encrypted archives
        """

        cache_enabled: bool = False
        """
        If the file has already been analyzed before, it will be taken from the cache, and not analyzed again.
        """

        url_extract_enabled: bool = True
        """
        Extract links from objects
        """

        enable_experimental_yara_rules: bool = False
        """
        Enable object analysis using yara test rules
        """

        mark_suspicious_files_options: SuspiciousFilesOptions | None = None
        """
        Settings for marking files as suspicious. By default, we do not send, but take the settings from the sandbox.

        You can configure it by passing an object with the necessary options.
        """

        sandbox: SandboxOptions = SandboxOptions()
        """
        Behavioral Analysis Parameters
        """

    file_name: str | None = None
    """
    The name of the file to be checked, which will be displayed in the sandbox web interface.

    If not specified, the hash value of the file is calculated using the SHA—256 algorithm.
    """

    short_result: bool = False
    """
    Return only the overall result of the check.

    The parameter value is ignored (true is used) if the value of the `async_result` parameter is also `true`.
    """

    async_result: bool = True
    """
    Return only the scan_id.

    Enabling this option may be usefull to send async requests for file checking.

    You can receive full report in a separate request.
    """

    priority: int = Field(default=3, ge=1, le=4)
    """
    The priority of the task. The higher it is, the faster it will get to work
    """


class SandboxScanTaskRequest(SandboxBaseScanTaskRequest):
    """
    Parameters of an API request to start analyzing a file previously uploaded to the product.

    `<URL>/analysis/createScanTask`
    """

    file_uri: str
    """
    The file URI received when uploading the file
    """

    options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options()
    """
    Additional scanning options
    """


class SandboxAdvancedScanTaskRequest(SandboxBaseScanTaskRequest):
    """
    Parameters of an API request to start analyzing a file previously uploaded to the product.

    `<URL>/analysis/createBAScanTask`
    """

    file_uri: str
    """
    The file URI received when uploading the file
    """

    sandbox: SandboxOptionsAdvanced = SandboxOptionsAdvanced()
    """
    Additional advanced scanning options
    """


class SandboxRescanTaskRequest(SandboxBaseScanTaskRequest):
    """
    API request parameters for launching retro analysis.

    Allows scanning with the new drakvuf-trace.log.zst and tcpdump.pcap rules

    `<URL>/analysis/createRetroTask`
    """

    file_uri: str
    """
    The file URI received when uploading the file
    """

    raw_events_uri: str | None = None
    """
    Temporary URI of the raw trace file
    """

    raw_network_uri: str | None = None
    """
    Temporary URI of the network file
    """

    options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options()
    """
    Additional scanning options
    """


class SandboxScanURLTaskRequest(SandboxBaseScanTaskRequest):
    """
    Parameters of the API request to start URL analysis.

    `<URL>/analysis/createScanURLTask`
    """

    url: str
    """
    URL address for analysis
    """

    options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options()
    """
    Additional scanning options
    """


class SandboxBaseTaskResponse(BaseResponse):
    """
    Base class for all scan responses
    """

    class ShortReport(BaseModel):
        scan_id: UUID
        """
        ID of the created task
        """

    class LongReport(ShortReport):
        result: SandboxResult
        """
        The overall result of the check.

        Missing from search responses:
            * `createScanTask` with the `async_result` parameter enabled;
            * `checkTask`, if the file analysis has not been completed yet
        """

        artifacts: list[Artifact]
        """
        A file, email, or other object that was checked during file analysis.

        Missing from search responses:
            * `createScanTask` with the `async_result` or `short_result` option enabled;
            * `checkTask`
        """

    data: LongReport | ShortReport = Field(union_mode="left_to_right")
    """
    Only the ShortReport is returned if async_result = True
    """

    def get_short_report(self) -> ShortReport:
        if self.errors:
            raise SandboxException(f"{self.errors}")

        return self.data

    def get_long_report(self) -> LongReport | None:
        if self.errors:
            raise SandboxException(f"{self.errors}")

        if isinstance(self.data, SandboxBaseTaskResponse.LongReport):
            return self.data

        return None


class SandboxCheckTaskRequest(BaseRequest):
    """
    Parameters of the API request for receiving file analysis results.

    The request can be used to get the results of the file analysis,
    which was started by an asynchronous request (`createScanTask` with the `async_result` parameter enabled).

    `<URL>/analysis/checkTask`
    """

    scan_id: UUID
    """
    ID of the task
    """

    allow_preflight: bool = True
    """
    If this flag is set, an intermediate result with the `is_preflight` attribute
    will be returned for scanning with multiple stages (for example, static + BA).
    """


class SandboxCheckTaskResponse(BaseResponse):
    class Data(BaseModel):
        scan_id: UUID
        """
        ID of the created task
        """

        result: SandboxResult | None = None
        """
        The overall result of the check.

        Missing from search responses:
            * `createScanTask` with the `async_result` parameter enabled;
            * `checkTask`, if the file analysis has not been completed yet
        """

        is_preflight: bool
        """
        Is the result preliminary, for example, only static has completed
        """

    data: Data
