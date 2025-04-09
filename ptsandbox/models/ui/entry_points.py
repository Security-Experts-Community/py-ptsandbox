from typing import Literal

from pydantic import BaseModel, Field

from ptsandbox.models.core import EntryPointTypeUI, FilterProperties
from ptsandbox.models.core.base import BaseRequest
from ptsandbox.models.ui.common import EntryPointToken, SMTPDefaultRecord


class EntryPointRules(BaseModel):
    class _SandboxInternal(BaseModel):
        enabled: bool
        """
        Turn on the sandbox
        """

        name: str
        """
        Sandbox name
        """

        description: str
        """
        Sandbox Description
        """

        analysis_duration: int = Field(alias="analysisDuration")
        """
        Scan time in the sandbox
        """

        file_types: list[str] | None = Field(default=None, alias="fileTypes")
        """
        Types of files sent to the sandbox for analysis
        """

        mitm_enabled: bool = Field(alias="mitmEnabled")
        """
        Enable mitm
        """

        save_video: bool = Field(alias="saveVideo")
        """
        Save BA videos
        """

        filter_by_properties: FilterProperties = Field(alias="filterByProperties")
        """
        Filtering a group of files by properties for sending to the sandbox for analysis
        """

    class Sandbox(_SandboxInternal):
        image_name: str = Field(alias="imageName")
        """
        Sandbox image name
        """

    class SandboxMultiple(_SandboxInternal):
        image_names: list[str] = Field(alias="imageNames")
        """
        A set of BA images for auto-selection
        """

    class ScanConfig(BaseModel):
        class _BaseRule(BaseModel):
            class Detect(BaseModel):
                classification: str
                name: str

            description: str
            """
            Description of a custom rule for detecting files
            """

            enabled: bool
            """
            Enable a custom exclusion rule for file detection
            """

            detect: Detect
            """
            Rule detection result
            """

        class FileRule(_BaseRule):
            """
            A custom rule for detecting files
            """

            class File(BaseModel):
                types: list[str]
                """
                List of file extensions to detect
                """

                name_patterns: list[str] = Field(alias="namePatterns")
                """
                List of file name patterns for detection
                """

                mime_type_patterns: list[str] = Field(alias="mimeTypePatterns")
                """
                List of mime type patterns for detection
                """

                properties: list[list[str]]
                """
                List of file properties for detection
                """

            file: File
            """
            A custom rule for detecting files
            """

        class FileInverseRule(_BaseRule):
            """
            Inverse user rule for file detection
            """

            class FileInverse(BaseModel):
                types: list[str]
                """
                List of file extensions to detect
                """

                name_patterns: list[str] = Field(alias="namePatterns")
                """
                List of file name patterns for detection
                """

                mime_type_patterns: list[str] = Field(alias="mimeTypePatterns")
                """
                List of mime type patterns for detection
                """

            file_inverse: FileInverse = Field(alias="fileInverse")

        class URLRule(_BaseRule):
            """
            Custom rule for link detection
            """

            class URL(BaseModel):
                categories_list: list[list[str]] = Field(alias="categoriesList")
                """
                List of lists by link category
                """

            url: URL

        rules: list[FileRule | FileInverseRule | URLRule] = []
        """
        List of custom detection rules
        """

    base_url: str | None = Field(default=None, alias="baseUrl")
    """
    Web interface address
    """

    notify_destination: str | None = Field(default=None, alias="notifyDistention")
    """
    Where to send notifications: to the sender or recipient
    """

    locale: str | None = None
    """
    Language
    """

    quarantine: bool | None = None
    """
    Use quarantine
    """

    scan_timeout: int | None = Field(default=None, alias="scanTimeout")
    """
    Timeout
    """

    max_execution_time: int | None = Field(default=None, alias="maxExecutionTime")
    """
    Maximum scan execution time
    """

    exclude_blocks: list[str] | None = Field(default=None, alias="excludeBlocks")
    """
    Exclude mail addresses from blocking
    """

    max_unpack_level: int | None = Field(default=None, alias="maxUnpackLevel")
    """
    Archive unpacking depth
    """

    notify_domains: list[str] | None = Field(default=None, alias="notifyDomains")
    """
    Email domains for notifications
    """

    notify_sender_message: str | None = Field(default=None, alias="notifySenderMessage")
    """
    Message to sender
    """

    notify_recipient_message: str | None = Field(default=None, alias="notifyRecipientMessage")
    """
    Message to the recipient
    """

    send_notify: bool | None = Field(default=None, alias="sendNotify")
    """
    Sending notifications
    """

    background_dynamic_analysis: bool | None = Field(default=None, alias="backgroundDynamicAnalysis")
    """
    Dynamic scanning in the background
    """

    sandbox_enabled: bool | None = Field(default=None, alias="sandboxEnabled")
    """
    Sandbox scanning
    """

    save_clean_files: bool | None = Field(default=None, alias="saveCleanFiles")
    """
    Save non-dangerous files to the incubator
    """

    url_extract_enabled: bool | None = Field(default=None, alias="urlExtractEnabled")
    """
    Link Extraction
    """

    url_content_analysis_enabled: bool | None = Field(default=None, alias="urlContentAnalysisEnabled")
    """
    Scanning content by links
    """

    url_heuristic_prefilter_enabled: bool | None = Field(default=None, alias="urlHeuristicPrefilterEnabled")
    """
    Using heuristic analysis to scan links
    """

    url_patterns_included: list[str] | None = Field(default=None, alias="urlPatternsIncluded")
    """
    List of domains for link scanning (wildcards are allowed)
    """

    url_patterns_excluded: list[str] | None = Field(default=None, alias="urlPatternsExcluded")
    """
    List of domain exclusions for link scanning (wildcards are allowed)
    """

    url_limit_scanning_per_email: int | None = Field(default=None, alias="urlLimitScanningPerEmail")
    """
    Limit the number of scanned links per email
    """

    exclude_categories: list[list[str]] | None = Field(default=None, alias="excludeCategories")
    """
    A list of lists of url categories excluded from scanning
    """

    without_behavior_analysis_if_has_dangerous: bool | None = Field(
        default=None,
        alias="withoutBehaviorAnalysisIfHasDangerous",
    )
    """
    Don't run behavioral analysis if a dangerous file is found in the task
    """

    without_behavior_analysis_if_has_suspicious: bool | None = Field(
        default=None,
        alias="withoutBehaviorAnalysisIfHasSuspicious",
    )
    """
    Don't run behavioral analysis if a suspicious file is found in the task
    """

    sandboxes: list[Sandbox] | None = None

    auto_select_sandbox_enabled: bool | None = Field(default=None, alias="autoSelectSandboxEnabled")
    """
    Sandbox scanning with auto-image selection
    """

    auto_select_sandboxes: list[SandboxMultiple] | None = Field(default=None, alias="autoSelectSandboxes")

    disarming_enabled: bool | None = Field(default=None, alias="disarmingEnabled")
    """
    Enable email neutralization
    """

    disarming_by_conditions: bool | None = Field(default=None, alias="disarmingByConditions")
    """
    Neutralize emails according to the conditions
    """

    disarming_from_senders: list[str] | None = Field(default=None, alias="disarmingFromSenders")
    """
    The list of senders whose emails need to be neutralized
    """

    disarming_to_recipients: list[str] | None = Field(default=None, alias="disarmingToRecipients")
    """
    The list of recipients whose emails need to be neutralized
    """

    disarming_blocked_emails: bool | None = Field(default=None, alias="disarmingBlockedEmails")
    """
    Neutralize blocked emails
    """

    rules_scan_config: ScanConfig | None = Field(default=None, alias="rulesScanConfig")
    """
    Custom rules for detection
    """

    enable_experimental_yara_rules: bool | None = Field(default=None, alias="enableExperimentalYaraRules")
    """
    Enable object verification using yara test rules
    """


class EntryPointSettings(BaseModel):
    class SMTPSettings(BaseModel):
        class Route(BaseModel):
            enabled: bool
            """
            On/Off Route
            """

            pattern: str
            """
            The template for the domain
            """

        class Resolver(BaseModel):
            type: Literal["static", "dynamic"]

            records: list[SMTPDefaultRecord] = []
            """
            Only available if type is "static"
            """

        routes: list[Route] = []

    balancer_host: str | None = Field(default=None, alias="balancerHost")
    """
    Balancer Host
    """

    balancer_port: int | None = Field(default=None, alias="balancerPort")
    """
    Balancer port
    """

    destination_login: str | None = Field(default=None, alias="destinationLogin")
    """
    Login of the destination file resource
    """

    destination_options: str | None = Field(default=None, alias="destinationOptions")
    """
    Connection settings for the destination file resource
    """

    destination_password: str | None = Field(default=None, alias="destinationPassword")
    """
    Password of the destination file resource
    """

    destination_port: int | None = Field(default=None, alias="destinationPort")
    """
    The port of the destination file resource
    """

    destination_server: str | None = Field(default=None, alias="destinationServer")
    """
    Destination file resource address
    """

    destination_share_path: str | None = Field(default=None, alias="destinationSharePath")
    """
    The path to the destination file resource
    """

    destination_type: str | None = Field(default=None, alias="destinationType")
    """
    The type of the destination file resource
    """

    destination_version: str | None = Field(default=None, alias="destinationVersion")
    """
    Version of the destination file resource
    """

    email: str | None = Field(default=None, alias="email")
    """
    Mailing address
    """

    smtp_host: str | None = Field(default=None, alias="smtpHost")

    smtp_port: int | None = Field(default=None, alias="smtpPort")

    smtp_use_ssl: bool | None = Field(default=None, alias="smtpUseSsl")

    smtp_auth_type: str | None = Field(default=None, alias="smtpAuthType")

    imap_auth_type: str | None = Field(default=None, alias="imapAuthType")
    """
    The type of IMAP authentication
    """

    imap_host: str | None = Field(default=None, alias="imapHost")
    """
    IMAP server address
    """

    imap_port: int | None = Field(default=None, alias="imapPort")
    """
    IMAP server port
    """

    imap_use_ssl: bool | None = Field(default=None, alias="imapUseSsl")
    """
    Use ssl
    """

    login: str | None = Field(default=None, alias="login")
    """
    Login
    """

    password: str | None = Field(default=None, alias="password")
    """
    Password
    """

    port: int | None = Field(default=None, alias="port")
    """
    Port
    """

    quarantine_login: str | None = Field(default=None, alias="quarantineLogin")
    """
    Login for quarantine
    """

    quarantine_options: str | None = Field(default=None, alias="quarantineOptions")
    """
    Quarantine parameters
    """

    quarantine_password: str | None = Field(default=None, alias="quarantinePassword")
    """
    Quarantine password
    """

    quarantine_port: int | None = Field(default=None, alias="quarantinePort")
    """
    Quarantine port
    """

    quarantine_server: str | None = Field(default=None, alias="quarantineServer")
    """
    Quarantine server
    """

    quarantine_share_path: str | None = Field(default=None, alias="quarantineSharePath")
    """
    Quarantine path to the directory
    """

    quarantine_type: str | None = Field(default=None, alias="quarantineType")
    """
    Type of quarantine
    """

    quarantine_version: str | None = Field(default=None, alias="quarantineVersion")
    """
    Quarantine version
    """

    scan_max_file_size: int | None = Field(default=None, alias="scanMaxFileSize")
    """
    Maximum size of the scanned file
    """

    smtp_settings: SMTPSettings | None = Field(default=None, alias="smtpSettings")

    source_login: str | None = Field(default=None, alias="sourceLogin")
    """
    Login of the source file resource
    """

    source_options: str | None = Field(default=None, alias="sourceOptions")
    """
    Source file resource settings
    """

    source_password: str | None = Field(default=None, alias="sourcePassword")
    """
    The password of the source file resource
    """

    source_server: str | None = Field(default=None, alias="sourceServer")
    """
    The server address of the source file resource
    """

    source_share_path: str | None = Field(default=None, alias="sourceSharePath")
    """
    The server port of the source file resource
    """

    source_type: str | None = Field(default=None, alias="sourceType")
    """
    The type of the source file resource
    """

    source_version: str | None = Field(default=None, alias="sourceVersion")
    """
    Version of the source file resource
    """

    use_tls: bool | None = Field(default=None, alias="useTls")
    """
    Use TLS
    """

    token: EntryPointToken | None = None
    """
    API token
    """

    incoming_hosts: list[str] | None = Field(default=None, alias="incomingHosts")
    """
    List of additional source IP addresses
    """

    whitelist_ips: list[str] | None = Field(default=None, alias="whitelistIps")
    """
    The list of allowed IP addresses for connecting to the source.

    Format: ip/cidr, if set without /cidr, we assume that this is a specific ip address.

    Cidr can be set from 1 to 32.
    """

    use_whitelist_ips: bool | None = Field(default=None, alias="useWhitelistIps")
    """
    Use the list of allowed IP addresses to connect to the source
    """


class SandboxEntryPointsTypesResponse(BaseModel):
    """
    List of possible sources to check
    """

    class EntryPoint(BaseModel):
        allow_blocking: bool = Field(alias="allowBlocking")
        """
        Blocking mode
        """

        entrypoint_id: str = Field(alias="entrypointId")
        """
        The unique name of the source
        """

        type: EntryPointTypeUI
        """
        Type of scan source
        """

        rules: EntryPointRules

        settings: EntryPointSettings | None = None

    data: list[EntryPoint]


class SandboxEntryPointsResponse(BaseModel):
    class EntryPoint(BaseModel):
        """
        Information about the verification source
        """

        enabled: bool
        """
        Source status
        """

        errors: list[str]
        """
        Errors
        """

        name: str
        """
        Source name
        """

        type: EntryPointTypeUI
        """
        Source type
        """

        target: str
        """
        The server address for verified mail
        """

        id: str
        """
        Unique name of the source
        """

        blocking_enabled: bool | None = Field(default=None, alias="blockingEnabled")
        """
        Blocking mode
        """

        allow_blocking: bool | None = Field(default=None, alias="allowBlocking")
        """
        Allow email blocking notifications
        """

        sandbox_enabled: bool = Field(alias="sandboxEnabled")
        """
        Checking in the sandbox
        """

        token: EntryPointToken | None = None
        """
        Token
        """

    data: list[EntryPoint]


class SandboxEntryPointResponse(BaseModel):
    class EntryPoint(BaseModel):
        """
        Information about the verification source
        """

        enabled: bool
        """
        Source status
        """

        errors: list[str]
        """
        Errors
        """

        name: str
        """
        Source name
        """

        type: EntryPointTypeUI
        """
        Source type
        """

        target: str
        """
        The server address for verified mail
        """

        id: str
        """
        Unique name of the source
        """

        blocking_enabled: bool | None = Field(default=None, alias="blockingEnabled")
        """
        Blocking mode
        """

        allow_blocking: bool | None = Field(default=None, alias="allowBlocking")
        """
        Allow email blocking notifications
        """

        rules: EntryPointRules

        settings: EntryPointSettings | None = None
        """
        Entry point settings
        """

    data: EntryPoint


class SandboxCreateEntryPointRequest(BaseRequest):
    enabled: bool = True
    """
    Status of the verification source
    """

    name: str
    """
    Name of the source
    """

    type: EntryPointTypeUI
    """
    Type of the source
    """

    settings: EntryPointSettings = EntryPointSettings()

    rules: EntryPointRules = EntryPointRules()
