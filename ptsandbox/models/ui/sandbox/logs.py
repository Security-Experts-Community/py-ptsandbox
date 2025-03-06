from ptsandbox.models.core import SandboxBaseModel, SandboxBaseRequest


class SandboxFileEntry(SandboxBaseModel):
    name: str
    """Имя"""

    sha256: str
    """Хэш сумма"""


class SandboxUILogsRequest(SandboxBaseRequest):
    """
    Указывается список файлов, которые необходимо скачать

    Запрос делается на `/sandbox/logs`
    """

    logs: list[SandboxFileEntry]
