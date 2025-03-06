from uuid import UUID

from pydantic import Field
from typing_extensions import NotRequired, TypedDict

from ptsandbox.models.core import (
    Artifact,
    SandboxBaseModel,
    SandboxBaseRequest,
    SandboxBaseResponse,
    SandboxException,
    SandboxImageInfo,
    SandboxResult,
    VNCMode,
)


class DebugOptions(TypedDict):
    keep_sandbox: NotRequired[bool]
    """Не разрушать песочницу после сканирования"""

    skip_work: NotRequired[bool]
    """Выполнить сканирование, пропустив этап сбора данных для анализа"""

    extract_crashdumps: NotRequired[bool]
    """Извлекать crashdumps из песочницы"""

    save_debug_files: NotRequired[bool]
    """Сохранять необходимые для отладки файлы"""

    rules_url: NotRequired[str]
    """
    Использовать указанные правила нормализации и корелляции.
    Правила передаются в виде ссылки на архив, содержащий скомпилированные правила
    """

    sleep_work: NotRequired[bool]
    """Выполнить сканирование, заменив этап сбора данных для анализа эквивалентным по времени ожиданием."""

    disable_syscall_hooks: NotRequired[bool]
    """Отключить функциональность syscall hooks."""

    disable_dll_hooks: NotRequired[bool]
    """Отключить функциональность dll hooks."""

    custom_syscall_hooks: NotRequired[str]
    """
    Использовать указанный список системных вызовов для перехвата.
    Список передаётся в виде http-ссылки на файл с именами системных вызовов (по одному на строку)
    """

    custom_dll_hooks: NotRequired[str]
    """
    Использовать указанный список пользовательских функций для перехвата.
    Функции передаются в виде http-ссылки на файл в формате плагина apimon.
    """

    disable_retries: NotRequired[bool]
    """Отключить повторное исполнение задания в случае ошибки сканирования"""

    enable_sanitizers: NotRequired[bool]
    """Включение отладочных механизмов группы "sanitizers" """

    allowed_outbound_connections: NotRequired[list[str]]
    """Белый список IP-адресов, к которым разрешены подключения из ВМ."""

    payload_completion_event: NotRequired[str]
    """
    Регулярное выражение для сырого события DRAKVUF, сигнализирующего окончание полезной работы семпла.
    Если данная опция указана, sandbox-worker расчитает и выведет в лог метрику PAYLOAD_SCAN_TIME
    """

    disable_procdump_on_finish: NotRequired[bool]
    """Отключить функциональность снятия дампа памяти с образца в конце наблюдения."""

    skip_update_time: NotRequired[bool]
    """Не синхронизировать время в ОС ВМ с хостом."""

    disable_manual_scan_events: NotRequired[bool]
    """Не отправлять уведомления жизненного цикла ручного поведенческого анализа (консоль готова, консоль закрыты и т.д.)"""

    bootkitmon_boot_timeout: NotRequired[int]
    """Максимальное время ожидания загрузки ВМ в секундах (по-умолчанию 90 секунд)"""

    custom_procdump_exclude: NotRequired[str]
    """
    Файл со списком процессов для которых не следует снимать дампы памяти.

    Каждая строка в файле представляет собой регулярное выражение пути к файлу процесса на диске.
    """

    custom_fileextractor_exclude: NotRequired[str]
    """
    Файл со списком файлов, которые не следует извлекать

    Каждая строка в файле представляет собой регулярное выражение пути к файлу процесса на диске.
    """

    validate_plugins: NotRequired[bool]
    """Проверять плагины на наличие хотя бы одного события за ПА."""

    extra_vm_init_url: NotRequired[str]
    """
    Запустить этот скрипт в ВМ непосредственно перед запуском ПА.

    Можно использовать для ускорения цикла тестирования шеллкода (для установки новой версии шеллкода в виртуалку перед запуском анализ без перестроения подобразов).

    Или для запуска команды диагностики (например, проверка сети во время ПА).
    """


class SandboxOptions(SandboxBaseRequest):
    """
    Параметры поведенческого анализа.
    При отсутствии используются параметры источника для проверки, заданные в системе
    """

    enabled: bool = True
    """Выполнить поведенческий анализ"""

    image_id: str = "win7-sp1-x64"
    """Идентификатор образа виртуальной машины"""

    custom_command: str | None = None
    """Команда для запуска исследуемого файла. Маркер {file} в составе строки заменяется на путь к образцу."""

    procdump_new_processes_on_finish: bool = False
    """Снимать дампы для всех порожденных и не умерших процессов"""

    analysis_duration: int = 300
    """Продолжительность наблюдения за файлом в ходе поведенческого анализа (в секундах). minimum: 10, maximum: 600"""

    bootkitmon: bool = False
    """Выполнить bootkitmon анализ."""

    analysis_duration_bootkitmon: int = 60
    """Продолжительность наблюдения за файлом на стадии bootkitmon (в секундах). minimum: 10, maximum: 600"""

    save_video: bool = True
    """Сохранять видео-захват экрана при ПА."""

    mitm_enabled: bool = True
    """Включить подмену сертификатов ПО сертификатами PT Sandbox при расшифровке и анализе защищенного трафика"""

    debug_options: DebugOptions = {"save_debug_files": False}


class SandboxOptionsNew(SandboxBaseRequest):
    class ExtraFile(SandboxBaseRequest):
        uri: str
        name: str

    image_id: str = "win7-sp1-x64"
    """Идентификатор образа ловушки."""

    custom_command: str | None = None
    """Команда для запуска исследуемого файла. Маркер {file} в составе строки заменяется на путь к образцу."""

    procdump_new_processes_on_finish: bool = False
    """Снимать дампы для всех порожденных и не умерших процессов"""

    analysis_duration: int = 300
    """Продолжительность наблюдения за файлом (в секундах)."""

    bootkitmon: bool = False
    """Выполнить bootkitmon анализ."""

    analysis_duration_bootkitmon: int = Field(default=60, ge=10, le=600)
    """Продолжительность наблюдения за файлом на стадии bootkitmon (в секундах)."""

    save_video: bool = True
    """Сохранять видео-захват экрана при ПА."""

    mitm_enabled: bool = True
    """Включить MITM при ПА."""

    disable_clicker: bool = False
    """Отключить запуск кликера"""

    skip_sample_run: bool = False
    """Отключить запуск образца"""

    vnc_mode: VNCMode = VNCMode.DISABLED
    """Режим VNC"""

    debug_options: DebugOptions = {"save_debug_files": False}

    extra_files: list[ExtraFile] = []
    """Список дополнительных файлов, который подкладываются в ловушку"""


class SandboxBaseCreateScanTaskRequest(SandboxBaseRequest):
    class Options(SandboxBaseRequest):
        class SuspiciousFilesOptions(SandboxBaseRequest):
            """Настройки пометки файлов как подозрительных"""

            encrypted_not_unpacked: bool = False
            """Зашифрованный и не распакованный файл"""

            max_depth_exceeded: bool = False
            """Глубина распаковки превышена"""

            office_encrypted: bool = False
            """Зашифрованный офисный файл"""

            office_has_macros: bool = False
            """Офисный файл с макросами"""

            office_has_embedded: bool = False
            """Офисный файл с встроенными объектами"""

            office_has_active_x: bool = False
            """Офисный файл с элементами ActiveX"""

            office_has_dde: bool = False
            """Офисный файл с динамическим обменом данных"""

            office_has_remote_data: bool = False
            """Офисный файл с внешними данными"""

            office_has_remote_template: bool = False
            """Офисный файл с внешними шаблонами"""

            office_has_action: bool = False
            """Офисный файл с Action"""

            pdf_encrypted: bool = False
            """Зашифрованный PDF файл"""

            pdf_has_embedded: bool = False
            """PDF файл со встроенными объектами"""

            pdf_has_open_action: bool = False
            """PDF файл с Open Action"""

            pdf_has_action: bool = False
            """PDF файл с Action"""

            pdf_has_javascript: bool = False
            """PDF файл с Javascript"""

        analysis_depth: int = 0
        """
        Глубина проверки. Максимальный уровень декомпозиции объектов с иерархической структурой
        (архивов, электронных писем, ссылок и т. п.) или уровень декомпрессии сжатых файлов.
        При значении 0 проверка без декомпозиции и декомпрессии.
        Чем больше число, тем дольше может выполняться проверка
        """

        passwords_for_unpack: list[str] = []
        """Список паролей для распаковки зашифрованных архивов"""

        cache_enabled: bool = False
        """Учитывать результаты предыдущих проверок"""

        url_extract_enabled: bool = False
        """Извлекать ссылки из объектов"""

        mark_suspicious_files_options: SuspiciousFilesOptions | None = None
        """
        Настройки пометки файлов как подозрительных. По умолчанию не отправляем, а берём настройки из песка.
        Можно настроить передав объект с нужными опциями.
        """

        sandbox: SandboxOptions = SandboxOptions()

    async_result: bool = False
    """
    Возвращать только идентификатор задания на проверку.
    Включение этого параметра может понадобиться для отправки асинхронных запросов на проверку файлов:
    ваше приложение может не дожидаться результатов проверки, а получать их отдельным запросом
    """

    short_result: bool = False
    """
    Возвращать только общий результат проверки.
    Значение параметра игнорируется (используется true), если значение параметра `async_result` тоже true
    """

    options: Options


class SandboxCreateScanTaskRequest(SandboxBaseCreateScanTaskRequest):
    """
    Параметры запроса к API на запуск проверки файла, ранее загруженного в продукт.

    <Корневой URL API>/analysis/createScanTask
    """

    file_uri: str
    """Временный URI файла, полученный в одноименном параметре в ответе"""

    file_name: str | None = None
    """Название проверяемого файла, которое будет отображаться в веб-интерфейсе PT Sandbox.
    Если не указано — хеш-сумма файла, вычисленная по алгоритму SHA-256"""


class SandboxCreateNewScanTaskRequest(SandboxBaseRequest):
    """
    Параметры запроса к API на запуск проверки файла, ранее загруженного в продукт.

    <Корневой URL API>/analysis/createBAScanTask
    """

    file_uri: str
    """URI проверяемого файла."""

    file_name: str | None = None
    """Название проверяемого файла."""

    short_result: bool = False
    """Возвращать только общий результат проверки."""

    async_result: bool = False
    """
        Возвращать только идентификатор задания без ожидания окончания сканирования.
        В ответе есть отсутствует ключ "result".
    """

    priority: int = Field(default=3, ge=1, le=4)
    """Приоритет задачи. Чем выше тем быстрее возьмется в работу"""

    sandbox: SandboxOptionsNew = SandboxOptionsNew()


class SandboxCreateRescanTaskRequest(SandboxCreateScanTaskRequest):
    raw_events_uri: str | None = None
    """Временный URI файла с raw трассой"""

    raw_network_uri: str | None = None
    """Временный URI файла с raw сетью"""


class SandboxCreateScanURLTaskRequest(SandboxBaseCreateScanTaskRequest):
    """
    Параметры запроса к API на запуск проверки URL адреса.

    <Корневой URL API>/analysis/createScanURLTask
    """

    url: str
    """URL адрес"""


class SandboxBaseTaskResponse(SandboxBaseResponse):
    class ShortReport(SandboxBaseModel):
        scan_id: UUID
        """Идентификатор задания на проверку."""

    class LongReport(ShortReport):
        result: SandboxResult
        """
        Общий результат проверки.
        Отсутствует в ответах на запросы:
            — `createScanTask` с включенным параметром `async_result`;
            — `checkTask`, если проверка файла еще не завершена
        """

        artifacts: list[Artifact]
        """
        Файл, электронное письмо или другой объект, которые были проверены в ходе проверки файла,
        URI которого был указан в запросе `createScanTask`.
        Отсутствует в ответах на запросы:
            — `createScanTask` с включенным параметром `async_result` или
            `short_result`;
            — `checkTask`
        """

    data: LongReport | ShortReport = Field(union_mode="left_to_right")

    def get_short_report(self) -> ShortReport | None:
        if self.errors:
            raise SandboxException(f"{self.errors}")

        return self.data

    def get_long_report(self) -> LongReport | None:
        if self.errors:
            raise SandboxException(f"{self.errors}")

        if isinstance(self.data, SandboxBaseTaskResponse.LongReport):
            return self.data

        return None


class SandboxCheckTaskRequest(SandboxBaseRequest):
    """
    Параметры запроса к API на получение результатов проверки файла.
    Запрос можно использовать для получения результатов проверки файла,
    которая была запущена асинхронным запросом (`createScanTask` с включенным
    параметром `async_result`).

    `<Корневой URL API>/analysis/checkTask`
    """

    scan_id: UUID
    """Идентификатор задания на проверку файла"""

    allow_preflight: bool = True
    """Если задан этот флаг, для сканирования с несколькими стадиями (например статика + ПА) будет возвращаться промежуточный результат с признаком is_preflight"""


class SandboxCheckTaskResponse(SandboxBaseTaskResponse):
    is_preflight: bool
    """Является ли результат предварительным, например завершилась только статика"""


class SandboxReportRequest(SandboxBaseRequest):
    """
    Получение полного отчета о сканировании задания

    `<Корневой URL API>/analysis/report`
    """

    scan_id: UUID
    """Идентификатор задания на проверку файла"""


class SandboxGetImagesResponse(SandboxBaseResponse):
    """
    Ваше при­ло­же­ние мо­жет по­лу­чить спи­сок об­ра­зов вир­ту­аль­ных ма­шин, уста­нов­лен­ных в PT Sandbox.

    `POST <Корневой URL API>/engines/sandbox/getImages`
    """

    data: list[SandboxImageInfo]  # type: ignore
