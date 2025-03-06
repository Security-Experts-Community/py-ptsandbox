from ptsandbox.models.core import SandboxBaseModel


class SandboxUIFilesResponse(SandboxBaseModel):
    """
    Абстракция скачанных файлов для удобной работы с ними
    """

    class File(SandboxBaseModel):
        """"""

        name: str
        """"""

        file: bytes
        """"""

    files: list[File]
    """"""

    archive: bytes
    """"""
