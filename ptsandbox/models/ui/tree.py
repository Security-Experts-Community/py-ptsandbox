from datetime import datetime

from pydantic import BaseModel, Field

from ptsandbox.models.core import (
    BlacklistStatus,
    BootkitmonStage,
    ContextType,
    EngineName,
    ErrorType,
    FileInfoProperties,
    FileInfoTypes,
    HashType,
    HTTPDirection,
    NetworkObjectType,
    SandboxImageInfo,
    ScanArtifactType,
    ScanState,
    SuspiciousBehaviors,
    TreeEngineName,
    TreeNodeType,
)
from ptsandbox.models.ui.common import CorrelationInfo, DetectionUI, Scan


class ScanArtifact(BaseModel):
    name: str
    sha256: str
    size: int
    type: ScanArtifactType | None = None


class SandboxInfo(BaseModel):
    class MSDNError(BaseModel):
        name: str
        """
        MSDN name of the image initialization error
        """

        code: int
        """
        The MSDN number of the image initialization error
        """

    class SandboxError(BaseModel):
        type: ErrorType

        duration: int | None = None
        """
        Waiting time
        """

    class Network(BaseModel):
        database_time: int | None = Field(default=None, alias="databaseTime")

        database_version: str = Field(alias="databaseVersion")

        version: str

        detections: list[DetectionUI] = []

        suspicious_behaviors: list[SuspiciousBehaviors] = Field(alias="suspiciousBehaviors")

    analysis_duration: int = Field(alias="analysisDuration")
    """
    Duration of behavioral analysis
    """

    analysis_planned_duration: int = Field(alias="analysisPlannedDuration")
    """
    Planned duration of the analysis
    """

    dpi_rules_version: str = Field(alias="dpiRulesVersion")
    """
    PT DPI rules version
    """

    correlation_rules_version: str = Field(alias="correlationRulesVersion")
    """
    Version of the correlation rules
    """

    mitm: bool
    """
    Was MITM enabled during the scan?
    """

    file_type: str | None = Field(default=None, alias="fileType")
    """
    What type of file was launched with

    File type (apparently, how the sandbox decided)
    """

    image_info: SandboxImageInfo = Field(alias="imageInfo")
    """
    Image Information
    """

    auto_select: bool = Field(alias="autoSelect")
    """
    Was the image selected automatically
    """

    suspicious_behaviors: list[SuspiciousBehaviors] = Field(alias="suspiciousBehaviors")
    """
    List of suspicious rules
    """

    detections: list[DetectionUI]
    """
    List of malware rules
    """

    init_msdn_error: MSDNError | None = Field(default=None, alias="initMsdnError")

    errors: list[SandboxError]

    bootkitmon: bool
    """
    Was bootkitmon enabled during the scan?
    """

    bootkitmon_stage: BootkitmonStage | None = Field(default=None, alias="bootkitmonStage")
    """
    Type of bootkitmon analysis stage
    """

    stage_index: int = Field(alias="stageIndex")
    """
    The number of the bootkitmon analysis stage
    """

    network: Network | None = None

    result: CorrelationInfo | None = None


class TreeNode(BaseModel):
    class ArchiveInfo(BaseModel):
        password: str

    class Info(BaseModel):
        type: FileInfoTypes

        name: str
        size: int
        sha1: str
        sha256: str
        md5: str
        ssdeep: str
        mime_type: str = Field(alias="mimeType")
        magic_string: str = Field(alias="magicString")
        file_type: str = Field(alias="fileType")
        properties: list[FileInfoProperties]

    class EmailInfo(BaseModel):
        subject: str
        from_: str | None = Field(default=None, alias="from")
        to: list[str]
        cc: list[str]
        bcc: list[str]

    class UrlInfo(BaseModel):
        class Redirect(BaseModel):
            url: str | None = None
            status: int | None = None

        url: str | None = None
        redirects: list[Redirect] | None = None

    class SandboxDropInfo(BaseModel):
        process_id: int = Field(alias="processId")
        process_name: str = Field(alias="processName")
        create_time: int = Field(alias="createTime")
        trigger: str
        bootkitmon: bool
        """
        Was bootkitmon enabled during the scan?
        """

        bootkitmon_stage: BootkitmonStage = Field(alias="bootkitmonStage")
        """
        ID of the bootkitmon analysis stage
        """

        stage_index: int | None = Field(alias="stageIndex")
        """
        The number of the bootkitmon analysis stage
        """

        graph_node_id: int | None = Field(alias="graphNodeId")
        """
        ID of the node in the BA graph
        """

    class SandboxCorrelatedInfo(BaseModel):
        result: CorrelationInfo

    class HTTPInfo(BaseModel):
        class Request(BaseModel):
            method: str
            url: str
            host: str

            user_agent: str = Field(alias="userAgent")
            """
            The value of the HTTP header 'User-Agent'
            """

            x_forwarded_for: str = Field(..., alias="xForwardedFor")
            """
            The value of the HTTP header 'X-Forwarded-For' is used to determine the IP of the HTTP client
            """

            referer: str
            """
            The value of the HTTP 'Referer' header, from which page the request was sent
            """

            content_type: str = Field(alias="contentType")

        class Response(BaseModel):
            code: int
            reason: str
            server: str
            content_type: str = Field(alias="contentType")
            content_disposition: str = Field(alias="contentDisposition")

        direction: HTTPDirection
        """
        Direction of HTTP query
        """

        request: Request | None = None

        response: Response | None = None

    class UnpackerInfo(BaseModel):
        class Error(BaseModel):
            type: ErrorType

            duration: int | None = None
            """
            Waiting time
            """

            limit_size: int | None = Field(None, alias="limitSize")
            """
            The value of the restriction
            """

        state: ScanState
        """
        Unpacking status
        """

        errors: list[Error] = []

    class DownloadUrlInfo(BaseModel):
        class Error(BaseModel):
            type: ErrorType

            duration: int | None = None
            """
            Waiting time
            """

            limit_size: int | None = Field(None, alias="limitSize")
            """
            The value of the restriction
            """

        state: ScanState
        """
        Url loading status
        """

        errors: list[Error] = []

        version: str
        """
        Engine version
        """

        status_code: int = Field(alias="statusCode")
        """
        Status code from the HTTP Status Line
        """

        reason_phrase: str = Field(alias="reasonPhrase")
        """
        The reason for the code from the HTTP Status Line
        """

    class BwListsInfo(BaseModel):
        class Error(BaseModel):
            type: ErrorType

            duration: int | None = None
            """
            Waiting time
            """

        state: ScanState
        """
        Check status in WB lists
        """

        status: BlacklistStatus
        """
        The result of the check on the WB lists
        """

        hashes: list[HashType]
        """
        The type of hash for which a match was found in the WB lists
        """

        errors: list[Error] = []
        """
        Errors in checking by WB lists
        """

    class CategorizerInfo(BaseModel):
        class Engine(BaseModel):
            class Error(BaseModel):
                type: ErrorType

                duration: int | None = None
                """
                Waiting time
                """

            name: TreeEngineName

            database_time: datetime | None = Field(default=None, alias="databaseTime")

            version: str

            errors: list[Error] = []

        class Result(BaseModel):
            class Error(BaseModel):
                type: ErrorType

                duration: int | None = None
                """
                Waiting time
                """

            state: ScanState
            """
            Check status in PTCategorizer
            """

            categories: list[str] = []
            """
            PTCategorizer Categories
            """

            errors: list[Error] = []
            """
            PTCategorizer check errors
            """

        engine: Engine

        result: Result | None = None

    class CacheInfo(BaseModel):
        source_scan_id: str = Field(alias="sourceScanId")
        """
        The original task ID
        """

        source_node_id: str = Field(alias="sourceNodeId")
        """
        The source node ID
        """

        timestamp: int
        """
        The time of creation of the initial task (UNIX timestamp)
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

        is_scanned: bool = Field(alias="isScanned")
        """
        Has the network artifact been scanned?
        """

    class ParentObjectInfo(BaseModel):
        type: FileInfoTypes
        """
        The type of artifact that the current node was derived from.
        """

        name: str
        """
        The name of the artifact from which the current node was derived.
        """

    class ContextCrawlerInfo(BaseModel):
        url: str
        """
        The URL from which the file was received
        """

        engine_name: EngineName | None = None
        """
        The name of the engine used for downloading
        """

    node_id: int = Field(alias="nodeId")
    """
    The node ID. It starts from 1
    """

    parent_ids: list[int] | None = Field(None, alias="parentIds")
    """
    A list of parent node IDs. It starts from the root

    The chain! parents. 0 -> 1 -> 2 -> 3 <=> nodeId=3, parentIds=[0,1,2]
    """

    node_type: TreeNodeType = Field(..., alias="nodeType")
    """
    Node Type
    """

    scans: list[Scan]
    """
    List of scans
    """

    info: Info
    """
    Node information - hashes, file name, mime type
    """

    correlation: CorrelationInfo | None = None
    """
    Correlation results
    """

    rule_engine_info: Scan | None = Field(default=None, alias="ruleEngineInfo")

    email_info: EmailInfo | None = Field(default=None, alias="emailInfo")

    archive_info: ArchiveInfo | None = Field(default=None, alias="archiveInfo")
    """
    If the node is an archive, and the sandbox has managed to find a password, it will be in this field.
    """

    url_info: UrlInfo | None = Field(default=None, alias="urlInfo")

    sandbox_info: SandboxInfo | None = Field(default=None, alias="sandboxInfo")
    """
    Sandbox-specific scan results
    """

    sandbox_drop_info: SandboxDropInfo | None = Field(default=None, alias="sandboxDropInfo")
    sandbox_procdump_info: SandboxDropInfo | None = Field(default=None, alias="sandboxProcDumpInfo")
    sandbox_memdump_info: SandboxDropInfo | None = Field(default=None, alias="sandboxMemDumpInfo")

    sandbox_correlated_info: SandboxCorrelatedInfo | None = Field(default=None, alias="sandboxCorrelatedInfo")
    """
    Correlated sandbox result (filled in if sandbox_correlated_state != UNKNOWN)
    """

    scan_artifacts: list[ScanArtifact] | None = Field(default=None, alias="scanArtifacts")
    """
    Sandbox artifacts: trails, events, graph, videos...
    """

    http_info: HTTPInfo | None = Field(default=None, alias="httpInfo")

    unpacker_info: UnpackerInfo | None = Field(default=None, alias="unpackerInfo")

    download_url_info: DownloadUrlInfo | None = Field(default=None, alias="downloadUrlInfo")

    bw_lists_info: BwListsInfo | None = Field(default=None, alias="bwListsInfo")

    ptcategorizer_info: CategorizerInfo | None = Field(default=None, alias="ptcategorizerInfo")

    yara_test_info: Scan | None = Field(default=None, alias="yaraTestInfo")

    yara_main_info: Scan | None = Field(default=None, alias="yaraMainInfo")

    cache_info: CacheInfo | None = Field(default=None, alias="cacheInfo")

    network_objects: list[NetworkObject] | None = Field(default=None, alias="networkObjects")

    parent_object_info: ParentObjectInfo | None = Field(default=None, alias="parentObjectInfo")

    context_type: ContextType | None = Field(default=None, alias="contextType")

    context_crawler_info: ContextCrawlerInfo | None = Field(default=None, alias="contextCrawlerInfo")

    first_child_count: int = Field(alias="firstChildCount")
    """
    Number of children of the first level
    """

    is_match: bool | None = Field(default=None, alias="isMatch")
    """
    Used for the filtering API.

    Does the node match the search conditions, if false, then it's just the parent element?
    """

    matched_fields: list[list[str]] | None = Field(default=None, alias="matchedFields")
    """
    Used for the filtering API. The list of fields that fall under the text query

    The path to the field, for example ['info', 'name']
    """


class SandboxTreeResponse(BaseModel):
    children: list[TreeNode]

    has_more: bool = Field(default=False, alias="hasMore")
    """
    If true, the number of records is greater than the limit and you can get additional ones using 'offset'
    """
