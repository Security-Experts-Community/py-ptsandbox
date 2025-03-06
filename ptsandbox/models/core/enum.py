"""
Все enum собраны в одном месте, т.к. есть много пересечений в моделях и легко повториться
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
        cls, source_type: Any, handler: GetCoreSchemaHandler  # pylint: disable=unused-argument
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(function=cls._validate)

    @classmethod
    def _validate(cls, value: str) -> "SoftEnum":
        if value not in cls.__members__.values():
            logger.warning(f'enum "{cls.__name__}" get unknown {value=}')

            # extended enum class with unknown value
            cls = Enum(
                cls.__name__, cls._member_map_ | {value.lower(): value}  # pylint: disable=self-cls-assignment,no-member
            )

        return cls(value)


class Hashes(SoftEnum):
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    UNKNOWN = "UNKNOWN"


class EngineName(SoftEnum):
    CURL = "CURL"
    WEB_ENGINE = "WEB_ENGINE"


class ScanState(SoftEnum):
    """Статус проверки."""

    UNKNOWN = "UNKNOWN"
    """неизвестность"""

    PARTIAL = "PARTIAL"
    """частичная проверка"""

    FULL = "FULL"
    """полная проверка"""

    UNSCANNED = "UNSCANNED"
    """проверка не проведена"""


class Verdict(SoftEnum):
    """Результат проверки"""

    CLEAN = "CLEAN"
    """угроз не обнаружено"""

    UNWANTED = "UNWANTED"
    """потенциально опасный"""

    DANGEROUS = "DANGEROUS"
    """опасный"""

    UNKNOWN = "UNKNOWN"
    """угрозы неизвестны (отсутствует в документации)"""


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
    FULL = "FULL"
    READ_ONLY = "READ_ONLY"


class NetworkObjectType(SoftEnum):
    URL = "URL"
    IP = "IP"
    DOMAIN = "DOMAIN"


class LogType(SoftEnum):
    NETWORK = "NETWORK"
    """Копия сетевого трафика в формате PCAP"""

    SCREENSHOT = "SCREENSHOT"
    """Снимок или видеозапись с экрана виртуальной машины"""

    EVENT_RAW = "EVENT_RAW"
    """Журнал событий"""

    EVENT_CORRELATED = "EVENT_CORRELATED"
    """Коррелированные события"""

    EVENT_NORMALIZED = "EVENT_NORMALIZED"
    """Нормализованные события"""

    DEBUG = "DEBUG"
    """Отладочные файлы"""

    GRAPH = "GRAPH"
    """graph-файл графа"""


class ArtifactType(SoftEnum):
    """Тип проверенного объекта"""

    FILE = "FILE"
    """обычный файл"""

    ARCHIVE = "ARCHIVE"
    """архив"""

    COMPRESSED = "COMPRESSED"
    """сжатый файл"""

    EMAIL = "EMAIL"
    """электронное письмо"""

    PROCESS_DUMP = "PROCESS_DUMP"
    """дамп процесса"""

    URL = "URL"
    """ссылка"""


class EngineSubsystem(SoftEnum):
    """Метод проверки."""

    AV = "AV"
    """антивирусное сканирование"""

    SANDBOX = "SANDBOX"
    """поведенческий анализ"""

    STATIC = "STATIC"
    """экспертная оценка файлов"""


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
    PTNAD = "PTNAD"
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
    UNKNOWN = "UNKNOWN"
    COMPLETED = "COMPLETED"
    TRUNCATED = "TRUNCATED"
    ERROR = "ERROR"


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
    PY_INSTALLER = "PY_INSTALLER"
    SFX = "SFX"
    SFX_7Z = "SFX_7z"
    SFX_ACE = "SFX_ACE"
    SFX_RAR = "SFX_RAR"
    SFX_ZIP = "SFX_ZIP"
    UPX = "UPX"
    PROTECTED = "PROTECTED"


class TreeEngineName(SoftEnum):
    BITDEFENDER = "bitdefender"
    CLAMAV = "clamav"
    DRWEB = "drweb"
    KASPERSKY = "kaspersky"
    NANO = "nano"
    PTESC = "ptesc"
    PTIOC = "ptioc"
    PT_SANDBOX_OVERALL = "pt_sandbox_overall"
    VBA = "vba"
    RULE_ENGINE = "rule_engine"


class TreeNodeType(SoftEnum):
    """
    Тип узла
    """

    ARTIFACT = "ARTIFACT"
    SANDBOX = "SANDBOX"
    SANDBOX_STAGE = "SANDBOX_STAGE"


class ScanArtifactType(SoftEnum):
    EMAIL = "EMAIL_HEADERS_PTESC"
    NORMALIZED = "SANDBOX_NORMALIZED_EVENT"
    CORRELATED = "SANDBOX_CORRELATED_EVENT"
    GRAPH = "SANDBOX_GRAPH"
    DEBUG = "SANDBOX_DEBUG_FILE"
    VIDEO = "SANDBOX_VIDEO"
    RAW_EVENT_FILES = "SANDBOX_RAW_EVENT_FILE"
    PCAP = "SANDBOX_NETWORK_FILE"


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
    UNKNOWN = "UNKNOWN"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"


class BlacklistStatus(SoftEnum):
    IN_BLACK_LIST = "IN_BLACK_LIST"
    IN_WHITE_LIST = "IN_WHITE_LIST"
    NOT_IN_LISTS = "NOT_IN_LISTS"
    UNKNOWN = "UNKNOWN"


class SandboxImageType(SoftEnum):
    BASE = "BASE"
    CUSTOM = "CUSTOM"
