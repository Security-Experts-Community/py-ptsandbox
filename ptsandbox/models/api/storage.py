from ptsandbox.models.core import (
    SandboxBaseModel,
    SandboxBaseRequest,
    SandboxBaseResponse,
)


class SandboxUploadScanFileResponse(SandboxBaseResponse):
    """
    Перед запуском проверки файла с помощью публичного API ваше приложение должно загрузить этот файл в PT Sandbox.

    `<Корневой URL API>/storage/uploadScanFile`
    """

    class Data(SandboxBaseModel):
        file_uri: str
        """Идентификатор загруженного файла, используется для создания задания на проверку."""

        ttl: int
        """
        Время ожидания запуска проверки после загрузки файла (в секундах).
        Если в течение этого времени проверка не была запущена, файл будет удален.
        """

    data: Data


class SandboxDownloadArtifactRequest(SandboxBaseRequest):
    """
    Параметры запроса к API на скачивание файла из PT Sandbox.

    <Корневой URL API>/storage/downloadArtifact
    """

    file_uri: str
    """
    Тело запроса должно содержать параметр file_uri. В качестве значения параметра
    должны быть указаны название алгоритма, по которому была вычислена хеш-сумма файла
    (md5, sha1 или sha256), двоеточие и сама хеш-сумма (algorithm:hash).

    Примечание. Ваше приложение может получить значение для параметра `file_uri` из
    ответа на запрос проверки файла (см. раздел 4.2). В этом случае URI файла в нужном
    формате можно взять из поля `data → artifacts → file_info → file_uri`.
    """
