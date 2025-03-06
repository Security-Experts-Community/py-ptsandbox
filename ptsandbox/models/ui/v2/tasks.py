import datetime
from uuid import UUID

from pydantic import Field

from ptsandbox.models.core import FileInfoTypes, SandboxBaseModel, SandboxBaseRequest
from ptsandbox.models.ui.v2.common import CorrelationInfo, EntryPoint


class SandboxUITasksRequest(SandboxBaseRequest):
    """
    Запрос - GET <песок>/api/ui/v2/tasks?<параметры>
    """

    limit: int = Field(20, ge=0, le=200)
    """Лимит на количество возвращаемых записей"""

    nextCursor: str | None = None
    """
    Курсор для пагинации, берется из ответа предыдущего листинга
    """

    offset: int = Field(0, ge=0, le=10000)
    """Смещение возвращаемых записей. Если указан nextCursor, смещение от курсора"""

    query: str = ""
    """
    Запрос на QSL.
    Пример: такого запроса: age < 30d AND (task.correlated.state != UNKNOWN ) ORDER BY start desc

    Фильтрация с помощью языка запросов. Синтаксис см. в документации пользователя
    """

    utcOffsetSeconds: int = 0
    """
    Это просто есть везде. Фактически - часовой пояс. Зачем - ¯\\_(ツ)_/¯

    Смещение времени пользователя от UTC, которое будет использовано для времени в запросах QL
    """

    def set_date(self, ts_from: datetime.datetime, ts_to: datetime.datetime) -> None:
        date_query = (
            f"start >= {ts_from.isoformat(timespec='seconds')} AND "  #
            f"start <= {ts_to.isoformat(timespec='seconds')}"
        )
        self.query += f"({date_query})"

    def set_sandbox(self, state: bool = True) -> None:
        if state:
            self.query += " AND (sandbox.state IN (UNSCANNED, PARTIAL, FULL))"
        else:
            self.query += (
                " AND (task.sandbox.correlated.state = UNKNOWN AND task.correlated.state IN (FULL,UNSCANNED,PARTIAL))"
            )

    def set_order(self) -> None:
        self.query += " ORDER BY start desc"


class Task(SandboxBaseModel):
    id: UUID
    """Идентификатор задания"""

    name: str
    """Имя задания"""

    object_type: FileInfoTypes = Field(..., alias="objectType")
    """Тип объекта"""

    start: datetime.datetime
    """Время создания задания (UNIX timestamp)"""

    correlation: CorrelationInfo
    """
    Общий вердикт продукта по файлу. Основан как на песке,
    так и на антивирусах и результате статического анализа
    """

    sandbox_correlation: CorrelationInfo | None = Field(None, alias="sandboxCorrelation")
    """Вердикт исключительно песка"""

    entry_point: EntryPoint = Field(..., alias="entryPoint")
    """Откуда приехало задание. Там какая-то хитрая структура, пока fallback в дикт"""

    start_time: float = Field(..., alias="startTime")
    """Время создания задания (float UNIX timestamp)"""

    processed_time: float = Field(..., alias="processedTime")
    """Время выполнения действия по заданию (float UNIX timestamp)"""

    verdict_time: float = Field(..., alias="verdictTime")
    """Время вынесения вердикта по заданию (float UNIX timestamp)"""


class SandboxUITasksResponse(SandboxBaseModel):
    """"""

    tasks: list[Task]
    """Массив задач"""

    current_cursor: str = Field(..., alias="currentCursor")
    """Курсор для пагинации, указывает на данные после первой записи (если есть)"""

    next_cursor: str = Field(..., alias="nextCursor")
    """
    Курсор для пагинации, если пустая строка, то данных больше нет. Указывает на данные после последней записи
    """


class SandboxUITaskSummaryResponse(SandboxBaseModel):
    """"""

    task: Task
    """"""
