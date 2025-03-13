"""
All enums are collected in one place, because there are many intersections in the models and it is easy to repeat.
"""

from enum import Enum
from typing import Any

from loguru import logger
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class SoftEnum(str, Enum):
    """
    A soft enum in order not to throw exceptions in production

    It is necessary because the library does not always keep up with api updates
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,  # pylint: disable=unused-argument
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(function=cls._validate)

    @classmethod
    def _validate(cls, value: str) -> "SoftEnum":
        if value not in cls.__members__.values():
            logger.warning(f'enum "{cls.__name__}" get unknown {value=}')

            # extended enum class with unknown value
            cls = Enum(
                cls.__name__,
                cls._member_map_ | {value.lower(): value},  # pylint: disable=self-cls-assignment,no-member
            )

        return cls(value)  # pyright: ignore[reportCallIssue, reportUnknownVariableType]


class HashType(SoftEnum):
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    UNKNOWN = "UNKNOWN"


class EngineName(SoftEnum):
    CURL = "CURL"
    WEB_ENGINE = "WEB_ENGINE"


class ScanState(SoftEnum):
    """
    Status of completed analysis
    """

    UNKNOWN = "UNKNOWN"
    """
    What happened?
    """

    PARTIAL = "PARTIAL"
    """
    Partial check
    """

    FULL = "FULL"
    """
    Full check
    """

    UNSCANNED = "UNSCANNED"
    """
    The analysis was not carried out
    """


class Verdict(SoftEnum):
    CLEAN = "CLEAN"
    """
    No threats detected
    """

    UNWANTED = "UNWANTED"
    """
    Potentially dangerous
    """

    DANGEROUS = "DANGEROUS"
    """
    Malicious object
    """

    UNKNOWN = "UNKNOWN"
    """
    Threats are unknown (missing from the documentation)
    """


class ThreatPlatform(SoftEnum):
    ANDROID = "ANDROID"
    IOS = "IOS"
    LINUX = "LINUX"
    OSX = "OSX"
    WINDOWS = "WINDOWS"

    NO_PLATFORM = "NO_PLATFORM"


class ThreatClassification(SoftEnum):
    ADWARE = "ADWARE"
    BACKDOOR = "BACKDOOR"
    BOOTKIT = "BOOTKIT"
    CLIENT_IRC = "CLIENT_IRC"
    CLIENT_P2P = "CLIENT_P2P"
    CLIENT_SMTP = "CLIENT_SMTP"
    CONSTRUCTOR = "CONSTRUCTOR"
    DIALER = "DIALER"
    DOS = "DOS"
    DOWNLOADER = "DOWNLOADER"
    EMAIL_FLOODER = "EMAIL_FLOODER"
    EMAIL_WORM = "EMAIL_WORM"
    EXPLOIT = "EXPLOIT"
    FLOODER = "FLOODER"
    FRAUDTOOL = "FRAUDTOOL"
    HACKTOOL = "HACKTOOL"
    HOAX = "HOAX"
    IM_FLOODER = "IM_FLOODER"
    IM_WORM = "IM_WORM"
    IRC_WORM = "IRC_WORM"
    MONITOR = "MONITOR"
    NETTOOL = "NETTOOL"
    NET_WORM = "NET_WORM"
    P2P_WORM = "P2P_WORM"
    PHISHING = "PHISHING"
    PSWTOOL = "PSWTOOL"
    REMOTEADMIN = "REMOTEADMIN"
    RISKTOOL = "RISKTOOL"
    ROOTKIT = "ROOTKIT"
    SERVER_FTP = "SERVER_FTP"
    SERVER_PROXY = "SERVER_PROXY"
    SERVER_TELNET = "SERVER_TELNET"
    SERVER_WEB = "SERVER_WEB"
    SMS_FLOODER = "SMS_FLOODER"
    SPAM = "SPAM"
    SPOOFER = "SPOOFER"
    TROJAN = "TROJAN"
    TROJAN_ARCBOMB = "TROJAN_ARCBOMB"
    TROJAN_BANKER = "TROJAN_BANKER"
    TROJAN_CLICKER = "TROJAN_CLICKER"
    TROJAN_DDOS = "TROJAN_DDOS"
    TROJAN_DOWNLOADER = "TROJAN_DOWNLOADER"
    TROJAN_DROPPER = "TROJAN_DROPPER"
    TROJAN_FAKEAV = "TROJAN_FAKEAV"
    TROJAN_GAMETHIEF = "TROJAN_GAMETHIEF"
    TROJAN_IM = "TROJAN_IM"
    TROJAN_MAILFINDER = "TROJAN_MAILFINDER"
    TROJAN_NOTIFIER = "TROJAN_NOTIFIER"
    TROJAN_PROXY = "TROJAN_PROXY"
    TROJAN_PSW = "TROJAN_PSW"
    TROJAN_RANSOM = "TROJAN_RANSOM"
    TROJAN_SMS = "TROJAN_SMS"
    TROJAN_SPY = "TROJAN_SPY"
    UNKNOWN = "UNKNOWN"
    UNKNOWN_THREAT = "UNKNOWN_THREAT"
    VIRTOOL = "VIRTOOL"
    VIRUS = "VIRUS"
    WEBTOOLBAR = "WEBTOOLBAR"
    WORM = "WORM"


class VNCMode(SoftEnum):
    DISABLED = "DISABLED"
    """
    Manual analysis is disabled
    """

    FULL = "FULL"
    """
    Manual analysis is enabled
    """

    READ_ONLY = "READ_ONLY"
    """
    Manual analysis in viewing mode only
    """


class NetworkObjectType(SoftEnum):
    URL = "URL"
    IP = "IP"
    DOMAIN = "DOMAIN"


class LogType(SoftEnum):
    NETWORK = "NETWORK"
    """
    A copy of the network traffic in PCAP format
    """

    SCREENSHOT = "SCREENSHOT"
    """
    Snapshot or video recording from the virtual machine screen
    """

    EVENT_RAW = "EVENT_RAW"
    """
    Raw events from system
    """

    EVENT_CORRELATED = "EVENT_CORRELATED"
    """
    Correlated events
    """

    EVENT_NORMALIZED = "EVENT_NORMALIZED"
    """
    Normalized events
    """

    DEBUG = "DEBUG"
    """
    Debugging files
    """

    GRAPH = "GRAPH"
    """
    .graph file of the graph
    """


class ArtifactType(SoftEnum):
    """
    The type of the analyzed object
    """

    ARCHIVE = "ARCHIVE"
    COMPRESSED = "COMPRESSED"
    EMAIL = "EMAIL"
    FILE = "FILE"
    PROCESS_DUMP = "PROCESS_DUMP"
    URL = "URL"


class EngineSubsystem(SoftEnum):
    """
    The analysis method
    """

    AV = "AV"
    SANDBOX = "SANDBOX"
    STATIC = "STATIC"


class Action(SoftEnum):
    BLOCK = "BLOCK"
    NOTHING = "NOTHING"
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"


class EmailType(SoftEnum):
    DISARMED = "DISARMED"
    NOTHING = "NOTHING"
    NOTIFICATION = "NOTIFICATION"
    SOURCE = "SOURCE"
    UNKNOWN = "UNKNOWN"


class DeliveryStatus(SoftEnum):
    FAIL = "FAIL"
    SKIP = "SKIP"
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"


class EntryPointType(SoftEnum):
    CHECK_ME = "CHECK_ME"
    DPI = "DPI"
    FILE_INBOX = "FILE_INBOX"
    FILE_MONITOR = "FILE_MONITOR"
    ICAP = "ICAP"
    INTERACTIVE_ANALYSIS = "INTERACTIVE_ANALYSIS"
    MAIL_AGENT = "MAIL_AGENT"
    MAIL_BCC = "MAIL_BCC"
    MAIL_GATEWAY = "MAIL_GATEWAY"
    MAIL_GATEWAY_MTA = "MAIL_GATEWAY_MTA"
    PTNAD = "PTNAD"
    PT_CS = "PT_CS"
    PT_EDR = "PT_EDR"
    PUBLIC_API = "PUBLIC_API"
    SCAN_API = "SCAN_API"
    UNKNOWN = "UNKNOWN"
    WEB = "WEB"


class EntryPointStatus(SoftEnum):
    UNKNOWN = "UNKNOWN"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


class EntryPointAction(SoftEnum):
    BLOCK = "BLOCK"
    NOTHING = "NOTHING"
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"


class QuarantineState(SoftEnum):
    UNKNOWN = "UNKNOWN"
    QUARANTINED = "QUARANTINED"
    REMOVED = "REMOVED"


class QuarantineEventType(SoftEnum):
    QUARANTINE = "QUARANTINE"
    REMOVE = "REMOVE"
    SEND = "SEND"


class DPIState(SoftEnum):
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    TRUNCATED = "TRUNCATED"
    UNKNOWN = "UNKNOWN"


class FileInfoTypes(SoftEnum):
    ARCHIVE = "ARCHIVE"
    COMPRESSED_FILE = "COMPRESSED_FILE"
    EMAIL = "EMAIL"
    EMAIL_BODY = "EMAIL_BODY"
    FILE = "FILE"
    FOLDER = "FOLDER"
    HTTP = "HTTP"
    SANDBOX_DROP = "SANDBOX_DROP"
    SANDBOX_MEMORY_DUMP = "SANDBOX_MEMORY_DUMP"
    SANDBOX_PROCESS_MEMORY_DUMP = "SANDBOX_PROCESS_MEMORY_DUMP"
    URL = "URL"


class FileInfoProperties(SoftEnum):
    ARCHIVE = "ARCHIVE"
    COMPRESSED = "COMPRESSED"
    CORRUPTED = "CORRUPTED"
    EMAIL = "EMAIL"
    ENCRYPTED = "ENCRYPTED"
    HAS_ACTION = "HAS_ACTION"
    HAS_ACTIVE_X = "HAS_ACTIVE_X"
    HAS_ADD_IN = "HAS_ADD_IN"
    HAS_DDE = "HAS_DDE"
    HAS_EMBEDDED = "HAS_EMBEDDED"
    HAS_JAVASCRIPT = "HAS_JAVASCRIPT"
    HAS_MACROS = "HAS_MACROS"
    HAS_OPEN_ACTION = "HAS_OPEN_ACTION"
    HAS_REMOTE_DATA = "HAS_REMOTE_DATA"
    HAS_REMOTE_TEMPLATE = "HAS_REMOTE_TEMPLATE"
    MULTI_VOLUME = "MULTI_VOLUME"
    OFFICE = "OFFICE"
    PROTECTED = "PROTECTED"
    PY_INSTALLER = "PY_INSTALLER"
    SFX = "SFX"
    SFX_7Z = "SFX_7z"
    SFX_7z = "SFX_7z"
    SFX_ACE = "SFX_ACE"
    SFX_RAR = "SFX_RAR"
    SFX_ZIP = "SFX_ZIP"
    UPX = "UPX"


class TreeEngineName(SoftEnum):
    BITDEFENDER = "bitdefender"
    CLAMAV = "clamav"
    DRWEB = "drweb"
    KASPERSKY = "kaspersky"
    NANO = "nano"
    PTESC = "ptesc"
    PTIOC = "ptioc"
    PT_CATEGORIZER = "ptcategorizer"
    PT_SANDBOX_OVERALL = "pt_sandbox_overall"
    RULE_ENGINE = "rule_engine"
    VBA = "vba"
    YARA_ENGINE = "yara_engine"


class TreeNodeType(SoftEnum):
    ARTIFACT = "ARTIFACT"
    SANDBOX = "SANDBOX"
    SANDBOX_STAGE = "SANDBOX_STAGE"


class ScanArtifactType(SoftEnum):
    CORRELATED = "SANDBOX_CORRELATED_EVENT"
    DEBUG = "SANDBOX_DEBUG_FILE"
    EMAIL = "EMAIL_HEADERS_PTESC"
    GRAPH = "SANDBOX_GRAPH"
    NORMALIZED = "SANDBOX_NORMALIZED_EVENT"
    PCAP = "SANDBOX_NETWORK_FILE"
    RAW_EVENT_FILE = "SANDBOX_RAW_EVENT_FILE"
    VIDEO = "SANDBOX_VIDEO"


class ContextType(SoftEnum):
    EMPTY = ""
    CRAWLER = "CRAWLER"
    PTESC = "PTESC"
    SANDBOX = "SANDBOX"


class BootkitmonStage(SoftEnum):
    UNKNOWN = "UNKNOWN"
    BEFORE_REBOOT = "BEFORE_REBOOT"
    AFTER_REBOOT = "AFTER_REBOOT"


class ErrorType(SoftEnum):
    BOOTKITMON_REBOOT_TIMEOUT = "BOOTKITMON_REBOOT_TIMEOUT"
    CANCELLED_BY_RULES = "CANCELLED_BY_RULES"
    CANCELLED_BY_USER = "CANCELLED_BY_USER"
    COLLISION_ERROR = "COLLISION_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CONNECT_TIMEOUT = "CONNECT_TIMEOUT"
    CONTAINS_ENCRYPTED = "CONTAINS_ENCRYPTED"
    CORRUPTED = "CORRUPTED"
    ENCRYPTED = "ENCRYPTED"
    ENGINE_ERROR = "ENGINE_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INIT_ERROR = "INIT_ERROR"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    LISTS_NOT_READY_ERROR = "LISTS_NOT_READY_ERROR"
    MAX_DOWNLOAD_LIMIT_EXCEEDED = "MAX_DOWNLOAD_LIMIT_EXCEEDED"
    MAX_REDIRECT_EXCEEDED = "MAX_REDIRECT_EXCEEDED"
    MAX_SIZE_EXCEEDED = "MAX_SIZE_EXCEEDED"
    NODE_LIMIT_EXCEEDED = "NODE_LIMIT_EXCEEDED"
    NOT_ALLOWED_REDIRECT = "NOT_ALLOWED_REDIRECT"
    NOT_ENOUGH_IMAGE_COPIES = "NOT_ENOUGH_IMAGE_COPIES"
    NOT_FILE = "NOT_FILE"
    NOT_UNPACKABLE_FILE = "NOT_UNPACKABLE_FILE"
    NO_SUITABLE_UNPACKER = "NO_SUITABLE_UNPACKER"
    READ_TIMEOUT = "READ_TIMEOUT"
    RESPONSE_ERROR = "RESPONSE_ERROR"
    SCAN_MACHINE_ERROR = "SCAN_MACHINE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    UNKNOWN = "UNKNOWN"


class HTTPDirection(SoftEnum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    UNKNOWN = "UNKNOWN"


class BlacklistStatus(SoftEnum):
    IN_BLACK_LIST = "IN_BLACK_LIST"
    IN_WHITE_LIST = "IN_WHITE_LIST"
    NOT_IN_LISTS = "NOT_IN_LISTS"
    UNKNOWN = "UNKNOWN"


class SandboxImageType(SoftEnum):
    BASE = "base"
    CUSTOM = "custom"
    USER = "user"


class BaqueueState(SoftEnum):
    CREATED = "CREATED"
    DEDUPLICATION = "DEDUPLICATION"
    FINISHED_SUCCESSFULLY = "FINISHED_SUCCESSFULLY"
    FINISHED_WITH_ERROR = "FINISHED_WITH_ERROR"
    READY = "READY"
    READY_WITH_ERROR = "READY_WITH_ERROR"
    STARTED = "STARTED"
    STARTING = "STARTING"


class TokenPermissions(SoftEnum):
    SCAN_WITH_EXTENDED_SETTINGS = "SCAN_WITH_EXTENDED_SETTINGS"
    SCAN_WITH_PREDEFINED_SETTINGS = "SCAN_WITH_PREDEFINED_SETTINGS"


class SystemGroup(SoftEnum):
    AUTO_UPDATE = "AUTO_UPDATE"
    DATA_DB = "DATA_DB"
    ENGINE = "ENGINE"
    ENTRY_POINT = "ENTRY_POINT"
    EOS = "EOS"
    EVENTS_DB = "EVENTS_DB"
    FILES_STORAGE = "FILES_STORAGE"
    NODE = "NODE"
    SANDBOX = "SANDBOX"
    SERVICES = "SERVICES"


class SystemCode(SoftEnum):
    AV_ENGINE_IN_NOT_GENERAL_AVAILABILITY = "AV_ENGINE_IN_NOT_GENERAL_AVAILABILITY"
    COMPONENT_CAPACITY_EXCEEDED_MAX_SIZE = "COMPONENT_CAPACITY_EXCEEDED_MAX_SIZE"
    COMPONENT_CAPACITY_EXCEEDED_THRESHOLD = "COMPONENT_CAPACITY_EXCEEDED_THRESHOLD"
    COMPONENT_ERROR = "COMPONENT_ERROR"
    COMPONENT_PARTIALLY_AVAILABLE = "COMPONENT_PARTIALLY_AVAILABLE"
    END_OF_SUPPORT = "END_OF_SUPPORT"
    END_OF_SUPPORT_SOON = "END_OF_SUPPORT_SOON"
    IMAGE_INSTALL_ERROR = "IMAGE_INSTALL_ERROR"
    NEW_VERSION_AVAILABLE = "NEW_VERSION_AVAILABLE"
    NEW_VERSION_INSTALLATION_SCHEDULED = "NEW_VERSION_INSTALLATION_SCHEDULED"
    NODE_HAVE_ERROR = "NODE_HAVE_ERROR"
    NODE_IS_NOT_READY = "NODE_IS_NOT_READY"
    SANDBOX_RECONFIGURING = "SANDBOX_RECONFIGURING"
    STORAGE_CAPACITY_EXCEEDED_COMPONENTS_MAX_SIZE_BYTES = "STORAGE_CAPACITY_EXCEEDED_COMPONENTS_MAX_SIZE_BYTES"
    STORAGE_CAPACITY_EXCEEDED_MINIMUM = "STORAGE_CAPACITY_EXCEEDED_MINIMUM"


class UploadStrategy(SoftEnum):
    ALL_THREATS = "ALL_THREATS"
    DO_NOT_UPLOAD = "DO_NOT_UPLOAD"
    THREAT_SOURCE_ONLY = "THREAT_SOURCE_ONLY"


class EOSStatus(SoftEnum):
    ENDED = "ENDED"
    ENDS_SOON = "ENDS_SOON"
    OK = "OK"


class ComponentStatus(SoftEnum):
    NOT_READY = "NOT_READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    READY = "READY"


class ComponentType(SoftEnum):
    BEHAVIORAL_ANALYSIS = "BEHAVIORAL_ANALYSIS"
    CORE = "CORE"
    DATABASE = "DATABASE"
    FILE_STORAGE = "FILE_STORAGE"
    INTEGRATIONS = "INTEGRATIONS"
    MANAGEMENT = "MANAGEMENT"
    MONITORING = "MONITORING"
    OTHER = "OTHER"
    SCAN_ENGINES = "SCAN_ENGINES"
    SOURCES = "SOURCES"
    USER = "USER"
    VERIFICATION_RESULTS = "VERIFICATION_RESULTS"


class LicenseStatus(SoftEnum):
    EXPIRED = "EXPIRED"
    NO_LICENSE = "NO_LICENSE"
    VALID = "VALID"


class LicenseUpdateError(SoftEnum):
    BAD_LICENSE = "BAD_LICENSE"
    FUS_UNAVAILABLE = "FUS_UNAVAILABLE"
    LICENSE_FROM_ANOTHER_PRODUCT = "LICENSE_FROM_ANOTHER_PRODUCT"
    LICENSE_NOT_FOUND = "LICENSE_NOT_FOUND"
    NO_ERROR = ""
    PRODUCT_NOT_SUPPORTED = "PRODUCT_NOT_SUPPORTED"
    TIMEOUT = "TIMEOUT"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class LicenseEntryPoint(SoftEnum):
    CHECK_ME = "check-me"
    EXCHANGE_MTA = "exchange-mta"
    FILES_INBOX = "files-inbox"
    FILES_MONITOR = "files-monitor"
    ICAP = "icap"
    MAIL_BCC = "mail-bcc"
    MAIL_GATEWAY = "mail-gateway"
    MAIL_GATEWAY_MTA = "mail-gateway-mta"
    PT_CS = "pt-cs"
    PT_EDR = "pt-edr"
    PT_NAD = "pt-nad"
    PUBLIC_API = "public-api"
    SCAN_API = "scan-api"


class LicenseAvEngine(SoftEnum):
    AVAST = "avast"
    AVIRA = "avira"
    BITDEFENDER = "bitdefender"
    CLAMAV = "clamav"
    DRWEB = "drweb"
    ESET = "eset"
    KASPERSKY = "kaspersky"
    NANO = "nano"
    SYMANTEC = "symantec"
    VBA = "vba"


class LicensePerformanceType(SoftEnum):
    EMAIL_LIMIT = "EMAIL_LIMIT"
    NETWORK_STORAGE_LIMIT = "NETWORK_STORAGE_LIMIT"
    NETWORK_TRAFFIC_LIMIT = "NETWORK_TRAFFIC_LIMIT"
