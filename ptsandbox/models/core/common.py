"""Модели, которые аналогичны и для API, и для UI"""

from datetime import datetime

from ptsandbox.models.core.base import SandboxBaseModel, SandboxBaseResponse
from ptsandbox.models.core.enum import (
    ArtifactType,
    EngineSubsystem,
    LogType,
    NetworkObjectType,
    ScanState,
    Verdict,
)


class SandboxResult(SandboxBaseModel):
    """Результат проверки файла"""

    scan_state: ScanState
    """Статус проверки."""

    duration: float | None = None
    """
    Длительность проверки в секундах. Записывается только в общих
    результатах проверки (в JSON-объекте `data → result`).
    Отсутствует в ответе на запрос `checkTask` с результатами про-
    верки, запущенной асинхронным запросом `createScanTask` (с
    включенным параметром `async_result`)
    """

    duration_full: float | None = None
    """Длительность проверки с учетом записи в БД или времени запроса."""

    verdict: Verdict | None = None
    """Результат проверки"""

    threat: str | None = None
    """Тип вредоносного ПО"""

    errors: list[SandboxBaseResponse.Error]
    """Ошибки, возникшие в ходе проверки."""


class NetworkObject(SandboxBaseModel):
    type: NetworkObjectType
    """Тип сетевого объекта"""

    value: str
    """Значение сетевого объекта"""


class SuspiciousBehaviors(SandboxBaseModel):
    """Подозрительное поведение"""

    name: str
    """Название"""

    version: str | None = None
    """Версия"""

    mitre_threat_id: str
    """Идентификатор MITRE Threat ID"""

    weight: int
    """Вес"""


class Detection(SandboxBaseModel):
    """Обнаруженное вредоносное ПО"""

    detect: str
    """Вредоносное ПО"""

    threat: str
    """Тип вредоносного ПО"""


class Log(SandboxBaseModel):
    """Копия сетевого трафика, видеозапись, журналы событий."""

    type: LogType
    """Тип лога"""

    file_uri: str
    """Идентификатор файла, используется для скачивания"""

    file_name: str
    """Название файла"""


class SandboxImageInfo(SandboxBaseModel):
    """
    Информация об образе виртуальной машины
    Может быть пустым словарем ({}), если песок отрыгнул пустоту.
    (хорошая моделька, ультимативно-опциональная!)
    """

    class OS(SandboxBaseModel):
        """Информация об операционной системе образа виртуальной машины"""

        name: str
        """Название операционной системы"""

        version: str
        """Версия операционной системы"""

        architecture: str
        """Архитектура процессора, которую поддерживает операционная система"""

        service_pack: str | None = None
        """Название пакета обновления операционной системы (есть в ответе от api)"""

        servicePack: str | None = None
        """Название пакета обновления операционной системы (есть в ответе от UI)"""

        locale: str
        """Локаль операционной системы"""

    image_id: str | None = None
    """
    Идентификатор образа виртуальной машины
    Опционален для возможности переиспользования в моделях фронта
    Почему фронт его не возвращает - мистика
    """

    name: str | None = None
    """Новый фронт стал-таки возвращать название образа. Правда, в виде name."""

    type: str | None = None
    """Новое поле на фронте"""

    version: str | None = None
    """
    Версия образа виртуальной машины
    """

    os: OS | None = None
    """
    Информация об операционной системе образа виртуальной машины
    """


class Artifact(SandboxBaseModel):
    class FileInfo(SandboxBaseModel):
        """Информация о проверенном файле"""

        class FileInfoDetails(SandboxBaseModel):
            class ProcessDump(SandboxBaseModel):
                process_name: str
                """Имя процесса."""

                process_id: int
                """Идентификатор (PID) процесса."""

                dump_trigger: str
                """Причина снятия дампа"""

                dump_create_time: float
                """Время создания дампа"""

            process_dump: ProcessDump

        file_uri: str
        """Идентификатор файла. Может использоваться для его скачивания"""

        file_path: str
        """
        Путь к файлу (исключая корневой файл структуры), включая его
        название. Например, для файла `readme.txt` в корне архива
        `archive.zip` в качестве значения этого поля будет указано
        `readme.txt`, для самого архива — пустое значение
        """

        mime_type: str
        """MIME-тип файла, определенный в процессе проверки"""

        md5: str
        """MD5-хеш-сумма файла"""

        sha1: str
        """SHA-1-хеш-сумма файла"""

        sha256: str
        """SHA-256-хеш-сумма файла"""

        size: int
        """Размер файла в байтах"""

        details: FileInfoDetails | None = None

    class EngineResult(SandboxBaseModel):
        class Details(SandboxBaseModel):
            class Sandbox(SandboxBaseModel):
                """Подробная информация о поведенческом анализе (если проводился)"""

                class Stage(SandboxBaseModel):
                    """Результат одной стадии сканирования с bootkitmon."""

                    result: SandboxResult

                    detections: list[Detection] = []
                    """Список обнаружения ПА данной стадии."""

                    logs: list[Log] = []
                    """Копия сетевого трафика, видеозапись, журналы событий, граф, дебаг файлы, почтовые заголовки."""

                    artifacts: list["Artifact"] = []
                    """Артефакты ловушки — файлы, созданные в ходе поведенческого анализа."""

                    analysis_duration: float | None = None
                    """Фактическая продолжительность поведенческого анализа в секундах"""

                    suspicious_behaviors: list[SuspiciousBehaviors] = []

                image: SandboxImageInfo
                """Информация об образе виртуальной машины"""

                logs: list[Log]
                """Копия сетевого трафика, видеозапись, журналы событий."""

                artifacts: list["Artifact"] | None = None
                """
                Артефакты виртуальной машины — файлы, созданные в ходе поведенческого анализа.
                """

                stages: list[Stage] = []
                """Стадии анализа буткитмона"""

                analysis_duration: float | None = None
                """Фактическая продолжительность поведенческого анализа в секундах"""

                bootkitmon: bool | None = None
                """Был ли выполнен bootkitmon анализ при ПА"""

                network_objects: list[NetworkObject] = []
                """Сетевые объекты (url, ip, domain)"""

                suspicious_behaviors: list[SuspiciousBehaviors] = []
                """Подозрительное поведение"""

            sandbox: Sandbox | None = None
            """Подробная информация о поведенческом анализе (если проводился)"""

        engine_subsystem: EngineSubsystem
        """Метод проверки."""

        engine_code_name: str
        """Название антивируса или компонента"""

        engine_version: str | None = None
        """Версия антивируса или компонента"""

        database_version: str | None = None
        """Версия антивирусной базы или базы знаний"""

        database_time: datetime | None = None
        """Время обновления антивирусной базы или базы знаний"""

        result: SandboxResult
        """Результат проверки антивирусом или другим компонентом"""

        detections: list[Detection]
        """Массив с описанием обнаруженного вредоносного ПО"""

        details: Details | None = None

    type: ArtifactType
    """Тип проверенного объекта"""

    result: SandboxResult | None = None
    """Результат проверки файла"""

    file_info: FileInfo | None = None
    """Информация о проверенном файле"""

    engine_results: list[EngineResult] | None = None
    """Результаты проверки файла конкретными антивирусами или другими компонентами."""

    artifacts: list["Artifact"] | None = None
    """
    Файлы, запакованные в архив.
    Если отправленный на проверку файл не является архивом или превышена допустимая глубина распаковки,
    массив `artifacts` пустой.
    """

    network_objects: list[NetworkObject]
    """Сетевые объекты (url, ip, domain)"""

    def find_sandbox_result(self) -> EngineResult | None:
        if self.type == ArtifactType.ARCHIVE:
            if self.artifacts is not None:
                return self.artifacts[0].find_sandbox_result()
            return None
        if self.engine_results is not None:
            for result in self.engine_results:
                if result.engine_subsystem == EngineSubsystem.SANDBOX:
                    return result
        return None

    def find_static_result(self) -> EngineResult | None:
        if self.engine_results is not None:
            for result in self.engine_results:
                if result.engine_subsystem == EngineSubsystem.STATIC:
                    return result
        return None


# Решение проблемы с вложенностью моделей друг в друга
Artifact.model_rebuild()
Artifact.EngineResult.Details.Sandbox.model_rebuild()
