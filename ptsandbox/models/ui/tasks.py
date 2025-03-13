from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ptsandbox.models.core import FileInfoTypes
from ptsandbox.models.ui.common import CorrelationInfo, EntryPoint, FilterValues


class Task(BaseModel):
    id: UUID
    """
    Task ID
    """

    name: str
    """
    Task Name
    """

    object_type: FileInfoTypes = Field(alias="objectType")
    """
    Object type
    """

    start: datetime
    """
    Task creation time (UNIX timestamp)
    """

    correlation: CorrelationInfo | None = None
    """
    The overall verdict of the product on the file. It's based on the sandbox,
    so it is on antiviruses and the result of static analysis.
    """

    sandbox_correlation: CorrelationInfo | None = Field(None, alias="sandboxCorrelation")
    """
    The verdict is exclusively sandbox
    """

    entry_point: EntryPoint = Field(alias="entryPoint")
    """
    Where did the task come from
    """

    start_time: float = Field(alias="startTime")
    """
    Task creation time (float UNIX timestamp)
    """

    processed_time: float = Field(alias="processedTime")
    """
    Task execution time (float UNIX timestamp)
    """

    verdict_time: float = Field(alias="verdictTime")
    """
    Task verdict time (float UNIX timestamp)
    """


class SandboxTasksResponse(BaseModel):
    """
    Tasks listing

    `<URL>/api/ui/v2/tasks`
    """

    tasks: list[Task]
    """
    Array of tasks
    """

    current_cursor: str = Field(alias="currentCursor")
    """
    The cursor for pagination, points to the data after the first record (if any)
    """

    next_cursor: str = Field(alias="nextCursor")
    """
    The cursor is for pagination, if the line is empty, then there is no more data.
    Indicates the data after the last record
    """


class SandboxTasksFilterValuesResponse(FilterValues):
    """
    Possible values for filters based on sources and validation results

    `<URL>/api/ui/v2/tasks/filter-values`
    """

    ...


class SandboxTasksSummaryResponse(BaseModel):
    """
    Information about a specific task

    `<URL>/api/ui/v2/tasks/{scanId}/summary`
    """

    task: Task
