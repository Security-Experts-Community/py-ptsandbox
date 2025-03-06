from typing import Literal

from pydantic import Field

from ptsandbox.models.core import (
    BlacklistStatus,
    BootkitmonStage,
    ContextType,
    EngineName,
    ErrorType,
    FileInfoProperties,
    FileInfoTypes,
    Hashes,
    HTTPDirection,
    NetworkObjectType,
    SandboxBaseModel,
    SandboxBaseRequest,
    SandboxImageInfo,
    ScanArtifactType,
    ScanState,
    TreeNodeType,
)
from ptsandbox.models.ui.v2.common import CorrelationInfo, DetectionUI, Scan


class SandboxUITreeRequest(SandboxBaseRequest):
    """
    Запрос - GET <песок>/api/ui/v2/tasks/{scanId}/tree?<параметры>
    """

    parent_path: str | None = Field(None, alias="parentPath")
    """Полный путь до родителя, с которого нужно начать загрузку дерева. Список разделенный через запятую, например "0,2,10" """

    filtered_by_ids: str | None = Field(None, alias="filteredByIds")
    """Список идентификаторов конкретных узлов, которые нужно вернуть, например: "0,2,10,11" """

    limit: int = 1000
    """Лимит на количество возвращаемых записей"""

    offset: int = 0
    """Отступ, с которого возвращаются записи. Используется для пагинации"""

    max_tree_level: int = Field(3, alias="maxTreeLevel")
    """Максимальная глубина (относительно родителя) которую нужно вернуть"""

    sort_mode: Literal["DANGEROUS", "ALPHABETICAL"] = Field("ALPHABETICAL", alias="sortMode")
    """Метод сортировки. Сначала опасные 'DANGEROUS' или просто по алфавиту 'ALPHABETICAL'"""


class ScanArtifact(SandboxBaseModel):
    name: str
    sha256: str
    size: int
    type: ScanArtifactType | None = None


class SandboxInfo(SandboxBaseModel):
    class SuspiciousBehavior(SandboxBaseModel):
        name: str
        weight: int | None = None
        mitre_thread_id: str | None = Field(None, alias="mitreThreatId")
        version: str

    class MSDNError(SandboxBaseModel):
        name: str
        """Имя MSDN ошибки инициализации образа"""

        code: int
        """Номер MSDN ошибки инициализации образа"""

    class SandboxError(SandboxBaseModel):
        type: ErrorType
        """Тип ошибки"""

        duration: int | None = None
        """Продолжительность ожидания"""

    analysis_duration: int = Field(..., alias="analysisDuration")
    """Продолжительность динамического анализа"""

    analysis_planned_duration: int = Field(..., alias="analysisPlannedDuration")
    """Запланированная продолжительность анализа"""

    dpi_rules_version: str = Field(..., alias="dpiRulesVersion")
    """Хз, версия каких-то рулей"""

    correlation_rules_version: str = Field(..., alias="correlationRulesVersion")
    """Версия корелляционных рулей"""

    mitm: bool
    """Был ли включен MITM при сканировании"""

    file_type: str | None = Field(None, alias="fileType")
    """
    С каким типом был запущен файл
    Тип файла (видимо, как его решил песок)
    """

    image_info: SandboxImageInfo = Field(..., alias="imageInfo")
    """Информация об образе"""

    auto_select: bool = Field(..., alias="autoSelect")
    """Был ли образ выбран автоматически"""

    suspicious_behaviors: list[SuspiciousBehavior] = Field(..., alias="suspiciousBehaviors")
    """Список подозрительных детектов"""

    detections: list[DetectionUI]
    """Список малварных детектов"""

    init_msdn_error: MSDNError | None = Field(None, alias="initMsdnError")

    errors: list[SandboxError]

    bootkitmon: bool
    """Был ли включен bootkitmon при сканировании"""

    bootkitmon_stage: BootkitmonStage | None = Field(None, alias="bootkitmonStage")
    """Тип стадии bootkitmon анализа"""

    stage_index: int = Field(..., alias="stageIndex")
    """Номер стадии bootkitmon анализа"""


class TreeNode(SandboxBaseModel):
    class ArchiveInfo(SandboxBaseModel):
        password: str

    class Info(SandboxBaseModel):
        type: FileInfoTypes
        """Тип артефакта"""

        name: str
        size: int
        sha1: str
        sha256: str
        md5: str
        ssdeep: str
        mime_type: str = Field(..., alias="mimeType")
        magic_string: str = Field(..., alias="magicString")
        file_type: str = Field(..., alias="fileType")
        properties: list[FileInfoProperties]

    class EmailInfo(SandboxBaseModel):
        subject: str
        from_: str | None = Field(None, alias="from")
        to: list[str]
        cc: list[str]
        bcc: list[str]

    class UrlInfo(SandboxBaseModel):
        class Redirect(SandboxBaseModel):
            url: str | None = None
            status: int | None = None

        url: str | None = None
        redirects: list[Redirect] | None = None

    class SandboxDropInfo(SandboxBaseModel):
        process_id: int = Field(..., alias="processId")
        process_name: str = Field(..., alias="processName")
        create_time: int = Field(..., alias="createTime")
        trigger: str
        bootkitmon: bool
        """Был ли включен bootkitmon при сканировании"""

        bootkitmon_stage: BootkitmonStage = Field(..., alias="bootkitmonStage")
        """ип стадии bootkitmon анализа"""

        stage_index: int | None = None
        """Номер стадии bootkitmon анализа"""

        graph_node_id: int | None = None
        """Идентификатор ноды на графе ПА"""

    class SandboxCorrelatedInfo(SandboxBaseModel):
        result: CorrelationInfo

    class HTTPInfo(SandboxBaseModel):

        class Request(SandboxBaseModel):
            method: str
            url: str
            host: str

            user_agent: str = Field(..., alias="userAgent")
            """Значение HTTP заголовка 'User-Agent'"""

            x_forwarded_for: str = Field(..., alias="xForwardedFor")
            """Значение HTTP заголовка 'X-Forwarded-For', используется для того, чтобы определить IP HTTP клиента"""

            referer: str
            """Значение HTTP заголовка 'Referer', с какой страницы был послан запрос"""

            content_type: str = Field(..., alias="contentType")

        class Response(SandboxBaseModel):
            code: int
            reason: str
            server: str
            content_type: str = Field(..., alias="contentType")
            content_disposition: str = Field(..., alias="contentDisposition")

        direction: HTTPDirection
        """Направление запроса"""

        request: Request | None = None

        response: Response | None = None

    class UnpackerInfo(SandboxBaseModel):
        class Error(SandboxBaseModel):
            type: ErrorType
            """Тип ошибки"""

            duration: int | None = None
            """Продолжительность ожидания"""

            limit_size: int | None = Field(None, alias="limitSize")
            """Значение ограничения"""

        state: ScanState
        """Состояние распаковки"""

        errors: list[Error] = []

    class DownloadUrlInfo(SandboxBaseModel):
        class Error(SandboxBaseModel):
            type: ErrorType
            """Тип ошибки"""

            duration: int | None = None
            """Продолжительность ожидания"""

            limit_size: int | None = Field(None, alias="limitSize")
            """Значение ограничения"""

        state: ScanState
        """Состояние загрузки url"""

        errors: list[Error] = []

    class BwListsInfo(SandboxBaseModel):
        class Error(SandboxBaseModel):

            type: ErrorType
            """Тип ошибки"""

            duration: int | None = None
            """Продолжительность ожидания"""

        state: ScanState
        """Состояние проверки в ЧБ списках"""

        status: BlacklistStatus
        """Результат проверки по ЧБ спискам"""

        hashes: list[Hashes]
        """Тип хэша, по которому найдено совпадение в ЧБ списках"""

    class CacheInfo(SandboxBaseModel):
        source_scan_id: str = Field(..., alias="sourceScanId")
        """Исходный идентификатор задания"""

        source_node_id: str | int = Field(..., alias="sourceNodeId")
        """Исходный идентификатор ноды"""

        timestamp: int
        """Время создания исходного задания (UNIX timestamp)"""

    class NetworkObject(SandboxBaseModel):
        type: NetworkObjectType
        """Тип сетевого объекта"""

        value: str
        """Значение сетевого объекта"""

        is_scanned: bool = Field(..., alias="isScanned")
        """Выполнялось ли сканирование сетевого артефакта"""

    class ParentObjectInfo(SandboxBaseModel):
        type: FileInfoTypes
        """Тип артефакта, из которого был получен текущий узел."""

        name: str
        """Имя артефакта, из которого был получен текущий узел."""

    class ContextCrawlerInfo(SandboxBaseModel):
        url: str
        """URL из которого получен файл"""

        engine_name: EngineName | None = None
        """Имя движка использованного для скачивания"""

    node_id: int = Field(..., alias="nodeId")
    """Идентификатор узла. Начинается с 1"""

    parent_ids: list[int] | None = Field(None, alias="parentIds")
    """
    Список идентификаторов узлов родителей. Начинается с корня
    Цепочка! родителей. 0 -> 1 -> 2 -> 3 <=> nodeId=3, parentIds=[0,1,2]
    """

    node_type: TreeNodeType = Field(..., alias="nodeType")
    """Тип узла"""

    scans: list[Scan]
    """Список сканов"""

    info: Info
    """Информация о ноде - хэши, название файла, mime-тип"""

    correlation: CorrelationInfo
    """Результаты корреляции"""

    rule_engine_info: Scan = Field(..., alias="ruleEngineInfo")

    email_info: EmailInfo | None = Field(None, alias="emailInfo")

    archive_info: ArchiveInfo | None = Field(None, alias="archiveInfo")
    """Если нода - архив, и песку удалось подобрать пароль - он будет в этом поле"""

    url_info: UrlInfo | None = Field(None, alias="urlInfo")

    sandbox_info: SandboxInfo | None = Field(None, alias="sandboxInfo")
    """Результаты сканирования конкретно песком"""

    sandbox_drop_info: SandboxDropInfo | None = Field(None, alias="sandboxDropInfo")
    sandbox_proc_dump_info: SandboxDropInfo | None = Field(None, alias="sandboxProcDumpInfo")
    sandbox_mem_dump_info: SandboxDropInfo | None = Field(None, alias="sandboxMemDumpInfo")

    sandbox_correlated_info: SandboxCorrelatedInfo | None = Field(None, alias="sandboxCorrelatedInfo")
    """Коррелированный результат SandBox (заполняется если sandbox_correlated_state != UNKNOWN)"""

    scan_artifacts: list[ScanArtifact] | None = Field(None, alias="scanArtifacts")
    """Артефакты песка: трассы, ивенты, граф, видео..."""

    http_info: HTTPInfo | None = Field(None, alias="httpInfo")

    unpacker_info: UnpackerInfo | None = Field(None, alias="unpackerInfo")

    download_url_info: DownloadUrlInfo | None = Field(None, alias="downloadUrlInfo")

    bw_lists_info: BwListsInfo | None = Field(None, alias="bwListsInfo")

    cache_info: CacheInfo | None = Field(None, alias="cacheInfo")

    network_objects: list[NetworkObject] | None = Field(None, alias="networkObjects")

    parent_object_info: ParentObjectInfo | None = Field(None, alias="parentObjectInfo")

    context_type: ContextType | None = Field(None, alias="contextType")

    context_crawler_info: ContextCrawlerInfo | None = Field(None, alias="contextCrawlerInfo")

    first_child_count: int = Field(..., alias="firstChildCount")
    """Количество детей первого уровня"""

    is_match: bool | None = Field(None, alias="isMatch")
    """
        Используется для API фильтрации.
        Подходит ли узел под условия поиска, если false, то это просто родительский элемент
    """

    matched_fields: list[list[str]] | None = Field(None, alias="matchedFields")
    """Используется для API фильтрации. Список полей, которые подпадают под текстовый запрос"""


class SandboxUITreeResponse(SandboxBaseModel):
    children: list[TreeNode]

    has_more: bool = Field(False, alias="hasMore")
    """Если true, количество записей больше лимита и можно получить дополнительные используя 'offset'"""


class SandboxUITreeDownloadRequest(SandboxBaseRequest):
    """
    Скачивание всех артефактов дерева

    Запрос делается на `/v2/tasks/{scanId}/tree/download`
    """

    query: str = ""
    """Фильтрация дерева с помощью языка запросов. Синтаксис см. в документации пользователя"""

    include_sandbox_logs: Literal["true", "false"] = Field("true", alias="includeSandboxLogs")
    """Включать ли в результат логи ПА."""
