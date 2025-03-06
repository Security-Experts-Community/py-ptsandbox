from datetime import datetime

from pydantic import Field

from ptsandbox.models.core import (
    Action,
    DeliveryStatus,
    DPIState,
    EmailType,
    EntryPointAction,
    EntryPointStatus,
    EntryPointType,
    QuarantineEventType,
    SandboxBaseModel,
    ScanState,
    ThreatClassification,
    ThreatPlatform,
    TreeEngineName,
    Verdict,
)


class CorrelationInfo(SandboxBaseModel):
    """Информация о коррелляции"""

    state: ScanState
    """Состояние корелляции"""

    threat_classification: ThreatClassification = Field(..., alias="threatClassification")
    """Классификация объекта (VIRUS, SPAM, WORM, etc)"""

    threat_level: Verdict = Field(..., alias="threatLevel")
    """Уровень угрозы"""

    verdict_priority: int | None = Field(None, alias="verdictPriority")
    """Приоритет угрозы"""

    threat_platform: ThreatPlatform = Field(..., alias="threatPlatform")
    """Платформа артефакта"""


class MailResult(SandboxBaseModel):
    recipient: str
    action: Action
    email_type: EmailType = Field(..., alias="emailType")
    delivery_status: DeliveryStatus = Field(..., alias="deliveryStatus")
    server_address: str = Field(..., alias="serverAddress")
    server_port: int = Field(..., alias="serverPort")


class HTTPDescription(SandboxBaseModel):
    referer: str
    """Значение HTTP заголовка 'Referer', с какой страницы был послан запрос"""

    user_agent: str = Field(..., alias="userAgent")
    """Значение HTTP заголовка 'User-Agent'"""

    host: str
    """Значение HTTP заголовка 'Host'"""

    uri: str
    """Полный URL запроса"""


class EntryPoint(SandboxBaseModel):
    """Откуда приехало задание"""

    class EntryPointQuarantine(SandboxBaseModel):

        class QuarantineEvent(SandboxBaseModel):
            type: QuarantineEventType
            """Тип события"""

            time: int
            """Время создания события (UNIX timestamp)"""

            user_id: str | None = Field(None, alias="userId")
            """Идентификатор пользователя (только для SEND)"""

            smtp_host: str | None = Field(None, alias="smtpHost")
            """SMTP Host (только для SEND)"""

            smtp_port: int | None = Field(None, alias="smtpPort")
            """SMTP Port (только для SEND)"""

            recipients: list[str] | None = None
            """Список получателей (только для SEND)"""

        state: str
        """Состояние карантина"""

        events: list[QuarantineEvent] | None = None
        """Список событий карантина. Заполнен только в API /summary, в листинге этого поля нет"""

    class EntryPointCheckMe(SandboxBaseModel):
        from_address: str = Field(..., alias="fromAddress")
        """Отправитель полученный из SMTP сессии (команда 'MAIL FROM')"""

        recipients: list[str]
        """Список получателей, полученный из SMTP сессии (команда 'RCPT TO')"""

    class EntryPointICAP(SandboxBaseModel):
        method: str
        """ICAP метод (RESPMOD, REQMOD)"""

        url: str
        """ICAP адрес сервиса"""

        version: str
        """ICAP версия"""

        client_ip: str = Field(..., alias="clientIp")
        """Значение ICAP заголовка: 'X-Client-IP'"""

        client_username: str = Field(..., alias="clientUsername")
        """Значение ICAP заголовка: 'X-Client-Username'"""

    class EntryPointDPI(SandboxBaseModel):

        class DPISMTP(SandboxBaseModel):
            message_id: str = Field(..., alias="messageId")
            """Значение EML заголовка 'Message-Id'"""

            sender: str
            """Отправитель полученный заголовка письма 'From'"""

        src_ip: str = Field(..., alias="srcIp")
        """IP откуда был отправлен объект"""

        src_port: int = Field(..., alias="srcPort")
        """PORT откуда был отправлен объект"""

        dst_ip: str = Field(..., alias="dstIp")
        """IP куда был отправлен объект"""

        dst_port: int = Field(..., alias="dstPort")
        """PORT куда был отправлен объект"""

        proto: str
        """Протокол. При значениях HTTP или SMTP добавляются соответствующие ключи."""

        state: DPIState

        http: HTTPDescription | None = None

        smtp: DPISMTP | None = None

    class EntryPointMailAgent(SandboxBaseModel):
        from_address: str = Field(..., alias="fromAddress")
        """Отправитель полученный из SMTP сессии (команда 'MAIL FROM')"""

        recipients: list[str]
        """Список получателей, полученный из SMTP сессии (команда 'RCPT TO')"""

        mail_results: list[MailResult] | None = Field(None, alias="mailResults")
        """Результаты по почте. Заполнен только в API /summary, в листинге этого поля нет"""

    class EntryPointMailBcc(SandboxBaseModel):
        from_address: str = Field(..., alias="fromAddress")
        """Отправитель полученный из SMTP сессии (команда 'MAIL FROM')"""

        recipients: list[str]
        """Список получателей, полученный из SMTP сессии (команда 'RCPT TO')"""

    class EntryPointFileInbox(SandboxBaseModel):
        src_path: str = Field(..., alias="srcPath")
        """Исходный путь до файла"""

        dst_path: str = Field(..., alias="dstPath")
        """Путь куда был перемещён файл"""

    class EntryPointFileMonitor(SandboxBaseModel):
        src_path: str = Field(..., alias="srcPath")
        """Исходный путь до файла"""

    class EntryPointMailGateway(SandboxBaseModel):
        from_address: str = Field(..., alias="fromAddress")
        """Отправитель полученный из SMTP сессии (команда 'MAIL FROM')"""

        recipients: list[str]
        """Список получателей, полученный из SMTP сессии (команда 'RCPT TO')"""

        mail_results: list[MailResult] | None = Field(None, alias="mailResults")
        """Результаты по почте. Заполнен только в API /summary, в листинге этого поля нет"""

    class EntryPointPTNAD(SandboxBaseModel):
        src_ip: str = Field(..., alias="srcIp")
        """IP откуда был отправлен объект"""

        src_port: int = Field(..., alias="srcPort")
        """PORT откуда был отправлен объект"""

        dst_ip: str = Field(..., alias="dstIp")
        """IP куда был отправлен объект"""

        dst_port: int = Field(..., alias="dstPort")
        """PORT куда был отправлен объект"""

        ref: str
        """Ссылка на сессию PTNAD"""

        proto: str
        """Протокол"""

        http: HTTPDescription | None = None

    class ClientWebInfo(SandboxBaseModel):
        user_agent: str = Field(..., alias="userAgent")
        """Значение HTTP заголовка 'User-Agent'"""

        x_forwarded_for: str = Field(..., alias="xForwardedFor")
        """Значение HTTP заголовка 'X-Forwarded-For', используется для того, чтобы определить IP HTTP клиента"""

        referer: str
        """Значение HTTP заголовка 'Referer', с какой страницы был послан запрос"""

    class ClientFullWebInfo(ClientWebInfo):
        user_id: str = Field(..., alias="userId")
        """ID пользователя"""

        user_login: str = Field(..., alias="userLogin")
        """Логин пользователя"""

        user_name: str = Field(..., alias="userName")
        """Имя пользователя"""

        user_is_anonymous: bool = Field(..., alias="userIsAnonymous")
        """Признак, что пользователь аноним"""

    id: str
    """Идентификатор источника"""

    type: EntryPointType
    """Тип источника"""

    status: EntryPointStatus
    """Статус выполнения"""

    action: EntryPointAction
    """Тип действия"""

    quarantine: EntryPointQuarantine
    """Статус карантина"""

    client_ip: str = Field(..., alias="clientIp")
    """IP-адрес клиента"""

    check_me: EntryPointCheckMe | None = None
    """Информация об отправителе и получателях"""

    icap: EntryPointICAP | None = None

    dpi: EntryPointDPI | None = None

    mail_agent: EntryPointMailAgent | None = Field(None, alias="mailAgent")

    mail_bcc: EntryPointMailBcc | None = Field(None, alias="mailBcc")

    file_inbox: EntryPointFileInbox | None = Field(None, alias="fileInbox")

    file_monitor: EntryPointFileMonitor | None = Field(None, alias="fileMonitor")

    mail_gateway: EntryPointMailGateway | None = Field(None, alias="mailGateway")

    ptnad: EntryPointPTNAD | None = None

    public_api: ClientWebInfo | None = Field(None, alias="publicApi")

    scan_api: ClientWebInfo | None = Field(None, alias="scanApi")

    web: ClientFullWebInfo | None = None

    interactive_analysis: ClientFullWebInfo | None = Field(None, alias="interactiveAnalysis")


class DetectionUI(SandboxBaseModel):
    name: str
    threat_classification: ThreatClassification = Field(..., alias="threatClassification")


class Scan(SandboxBaseModel):
    class Engine(SandboxBaseModel):
        name: TreeEngineName

        database_time: datetime | None = Field(None, alias="databaseTime")
        """В pt_sandbox_overall (результат анализа песка), это поле есть не всегда. Ладно."""

        version: str

        detections: list[DetectionUI]

    engine: Engine

    result: CorrelationInfo
