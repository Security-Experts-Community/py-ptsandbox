from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ptsandbox.models.core import (
    Action,
    DeliveryStatus,
    DPIState,
    EmailType,
    EntryPointAction,
    EntryPointStatus,
    EntryPointType,
    QuarantineEventType,
    ScanState,
    ThreatClassification,
    ThreatPlatform,
    TreeEngineName,
    Verdict,
)
from ptsandbox.models.core.enum import ErrorType, QuarantineState, TokenPermissions


class CorrelationInfo(BaseModel):
    """
    Information about correlation
    """

    state: ScanState
    """
    The state of correlation
    """

    threat_classification: ThreatClassification = Field(alias="threatClassification")
    """
    Object classification (VIRUS, SPAM, WORM, etc.)
    """

    threat_level: Verdict = Field(alias="threatLevel")
    """
    Threat level
    """

    threat_platform: ThreatPlatform = Field(alias="threatPlatform")
    """
    Artifact Platform
    """

    verdict_priority: int | None = Field(default=None, alias="verdictPriority")
    """
    Threat priority
    """


class MailResult(BaseModel):
    recipient: str
    action: Action
    email_type: EmailType = Field(alias="emailType")
    delivery_status: DeliveryStatus = Field(alias="deliveryStatus")
    server_address: str = Field(alias="serverAddress")
    server_port: int = Field(alias="serverPort")


class HTTPDescription(BaseModel):
    referer: str
    """
    The value of the HTTP 'Referer' header, from which page the request was sent
    """

    user_agent: str = Field(alias="userAgent")
    """
    The value of the HTTP header 'User-Agent'
    """

    host: str
    """
    The value of the HTTP header 'Host'
    """

    uri: str
    """
    Full request URL
    """


class EntryPoint(BaseModel):
    """
    Where did the task come from
    """

    class Quarantine(BaseModel):
        class QuarantineEvent(BaseModel):
            type: QuarantineEventType

            time: int
            """
            Event creation time (UNIX timestamp)
            """

            user_id: str | None = Field(default=None, alias="userId")
            """
            User ID (for SEND only)
            """

            smtp_host: str | None = Field(default=None, alias="smtpHost")
            """
            SMTP Host (for SEND only)
            """

            smtp_port: int | None = Field(default=None, alias="smtpPort")
            """
            SMTP Port (for SEND only)
            """

            recipients: list[str] | None = None
            """
            List of recipients (for SEND only)
            """

        state: QuarantineState
        """
        Quarantine state
        """

        events: list[QuarantineEvent] = []
        """
        List of quarantine events. Filled in only in API /summary, there is no such field in the listing.
        """

    class CheckMe(BaseModel):
        from_address: str = Field(alias="fromAddress")
        """
        The sender received from the SMTP session (the 'MAIL FROM' command)
        """

        recipients: list[str]
        """
        The list of recipients received from the SMTP session (the 'RCPT TO' command)
        """

    class ICAP(BaseModel):
        method: str
        """
        ICAP method (RESPMOD, REQMOD)
        """

        url: str
        """
        ICAP address of the service
        """

        version: str
        """
        ICAP version
        """

        client_ip: str = Field(alias="clientIp")
        """
        ICAP header value: 'X-Client-IP'
        """

        client_username: str = Field(alias="clientUsername")
        """
        ICAP header value: 'X-Client-Username'
        """

    class DPI(BaseModel):
        class SMTP(BaseModel):
            message_id: str = Field(..., alias="messageId")
            """
            The EML value of the 'Message-Id' header
            """

            sender: str
            """
            Sender of the received email header 'From'
            """

        src_ip: str = Field(alias="srcIp")
        """
        The IP address where the object was sent from
        """

        src_port: int = Field(alias="srcPort")
        """
        PORT where the object was sent from
        """

        dst_ip: str = Field(alias="dstIp")
        """
        The IP address where the object was sent to
        """

        dst_port: int = Field(..., alias="dstPort")
        """
        PORT where the object was sent to
        """

        proto: str
        """
        Protocol. For HTTP or SMTP values, the corresponding keys are added.
        """

        state: DPIState

        http: HTTPDescription | None = None

        smtp: SMTP | None = None

    class MailAgent(BaseModel):
        from_address: str = Field(alias="fromAddress")
        """
        The sender received from the SMTP session (the 'MAIL FROM' command)
        """

        recipients: list[str]
        """
        The list of recipients received from the SMTP session (the 'RCPT TO' command)
        """

        mail_results: list[MailResult] | None = Field(default=None, alias="mailResults")
        """
        The results are sent by mail. Filled in only in API /summary, there is no such field in the listing.
        """

    class MailBcc(BaseModel):
        from_address: str = Field(alias="fromAddress")
        """
        The sender received from the SMTP session (the 'MAIL FROM' command)
        """

        recipients: list[str]
        """
        The list of recipients received from the SMTP session (the 'RCPT TO' command)
        """

    class FileInbox(BaseModel):
        src_path: str = Field(alias="srcPath")
        """
        The original path to the file
        """

        dst_path: str = Field(alias="dstPath")
        """
        The path where the file was moved
        """

    class FileMonitor(BaseModel):
        src_path: str = Field(alias="srcPath")
        """
        The original path to the file
        """

    class MailGateway(BaseModel):
        from_address: str = Field(alias="fromAddress")
        """
        The sender received from the SMTP session (the 'MAIL FROM' command)
        """

        recipients: list[str]
        """
        The list of recipients received from the SMTP session (the 'RCPT TO' command)
        """

        mail_results: list[MailResult] | None = Field(default=None, alias="mailResults")
        """
        The results are sent by mail. Filled in only in API /summary, there is no such field in the listing.
        """

    class PTNAD(BaseModel):
        src_ip: str = Field(alias="srcIp")
        """
        The IP address where the object was sent from
        """

        src_port: int = Field(alias="srcPort")
        """
        PORT where the object was sent from
        """

        dst_ip: str = Field(..., alias="dstIp")
        """
        The IP address where the object was sent to
        """

        dst_port: int = Field(..., alias="dstPort")
        """
        PORT where the object was sent to
        """

        ref: str
        """
        Link to the PTNAD session
        """

        proto: str
        """
        Protocol
        """

        http: HTTPDescription | None = None

    class ClientWebInfo(BaseModel):
        user_agent: str = Field(alias="userAgent")
        """
        The value of the HTTP header 'User-Agent'
        """

        x_forwarded_for: str = Field(alias="xForwardedFor")
        """
        The value of the HTTP header 'X-Forwarded-For' is used to determine the IP of the HTTP client
        """

        referer: str
        """
        The value of the HTTP 'Referer' header, from which page the request was sent
        """

    class ClientFullWebInfo(ClientWebInfo):
        user_id: str = Field(alias="userId")

        user_login: str = Field(alias="userLogin")

        user_name: str = Field(alias="userName")

        user_is_anonymous: bool = Field(alias="userIsAnonymous")

    id: str
    """
    Source ID
    """

    type: EntryPointType
    """
    Source Type
    """

    status: EntryPointStatus
    """
    Completion status
    """

    action: EntryPointAction
    """
    Type of action
    """

    quarantine: Quarantine
    """
    Quarantine status
    """

    client_ip: str = Field(alias="clientIp")
    """
    The client's IP address
    """

    # TODO: check this field
    # metadata: dict[Any, Any]

    check_me: CheckMe | None = None
    """
    Information about the sender and recipients
    """

    icap: ICAP | None = None

    dpi: DPI | None = None

    mail_agent: MailAgent | None = Field(default=None, alias="mailAgent")

    mail_bcc: MailBcc | None = Field(default=None, alias="mailBcc")

    file_inbox: FileInbox | None = Field(default=None, alias="fileInbox")

    file_monitor: FileMonitor | None = Field(default=None, alias="fileMonitor")

    mail_gateway: MailGateway | None = Field(default=None, alias="mailGateway")

    mail_gateway_mta: MailGateway | None = Field(default=None, alias="mailGatewayMta")

    ptnad: PTNAD | None = None

    public_api: ClientWebInfo | None = Field(default=None, alias="publicApi")

    scan_api: ClientWebInfo | None = Field(default=None, alias="scanApi")

    pt_edr: ClientWebInfo | None = Field(default=None, alias="ptEdr")

    pt_cs: ClientWebInfo | None = Field(default=None, alias="ptCs")

    web: ClientFullWebInfo | None = None

    interactive_analysis: ClientFullWebInfo | None = Field(default=None, alias="interactiveAnalysis")


class DetectionUI(BaseModel):
    name: str
    threat_classification: ThreatClassification = Field(alias="threatClassification")
    id: str | None = None
    description: str | None = None


class Error(BaseModel):
    type: ErrorType

    duration: int | None = None
    """
    Waiting time
    """


class Scan(BaseModel):
    class Engine(BaseModel):
        name: TreeEngineName

        database_time: datetime | None = Field(default=None, alias="databaseTime")

        version: str

        detections: list[DetectionUI] = []

        errors: list[Error] = []

    engine: Engine

    result: CorrelationInfo | None = None


class FilterValues(BaseModel):
    class EntryPoint(BaseModel):
        name: str
        id: str
        type: EntryPointType

    entry_points: list[EntryPoint] = Field(alias="entryPoints")
    """
    Possible values for filters by source
    """

    threat_classifications: list[str] = Field(alias="threatClassifications")
    """
    Possible values for filters based on the analysis result
    """

    properties: list[str]
    """
    Возможные значения для фильтров по свойствам файла
    """

    categories: list[str]
    """
    Possible values for filters by link category
    """


class Token(BaseModel):
    class EntryPoint(BaseModel):
        """
        The entrypoint to which the api token is linked.

        It is used for listing and for obtaining a specific token.
        """

        id: str
        """
        Entrypoint ID
        """

        name: str
        """
        Entrypoint name
        """

    name: str
    """
    Name of the PublicAPI token

    pattern: ^[a-zA-Z][a-zA-Z0-9-]{3,28}[a-zA-Z]$
    """

    comment: str | None = None
    """
    Comment on the token
    """

    permissions: list[TokenPermissions]
    """
    Token Access Rights
    """

    id: int
    """
    ID of the record in the database
    """

    creator_login: str = Field(alias="creatorLogin")
    """
    Login of the user who created the token
    """

    created: float
    """
    UNIX time the time of token creation
    """

    modified: float | None = None
    """
    UNIX time the time when the token comment was changed
    """

    deleted: float | None = None
    """
    UNIX time the time of token deletion
    """

    entry_point: EntryPoint | None = Field(default=None, alias="entryPoint")


class SMTPDefaultRecord(BaseModel):
    """
    SMTP connection settings
    """

    class Config(BaseModel):
        class Credential(BaseModel):
            login: str
            password: str
            id: str

        class Timeout(BaseModel):
            connect: int
            execute: int

        host: str
        port: int
        use_ssl: bool = Field(alias="useSsl")
        auth_type: Literal["any", "plain", "encrypt", "ntlm", "none"] = Field(alias="authType")
        timeout: Timeout | None = None
        credential: Credential | None = None

    config: Config

    priority: int
    """
    Priority for recording
    """
