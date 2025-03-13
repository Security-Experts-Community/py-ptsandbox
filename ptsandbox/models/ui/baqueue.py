from pydantic import BaseModel, Field

from ptsandbox.models.core.enum import BaqueueState, EntryPointType


class SandboxBaqueueTasksResponse(BaseModel):
    """
    Listing of issues in the BA queue
    """

    class Task(BaseModel):
        task_id: str = Field(alias="taskId")

        correlation_id: str = Field(alias="correlationId")

        result_task_id: str | None = Field(default=None, alias="resultTaskId")
        """
        ID of the task from which the result was taken
        """

        order_number: int | None = Field(default=None, alias="orderNumber")
        """
        Sequence number in the queue (for unfinished tasks)
        """

        state: BaqueueState
        """
        Task status
        """

        priority: int
        """
        Task priority
        """

        priority_name: str = Field(alias="priorityName")
        """
        String representation of task priority
        """

        entry_point_id: str = Field(alias="entryPointId")
        """
        Source ID
        """

        entry_point_type: EntryPointType = Field(alias="entryPointType")
        """
        Source Type
        """

        object_mime_type: str = Field(alias="objectMimeType")
        """
        The object's mime type
        """

        task_object_name: str = Field(alias="taskObjectName")
        """
        Task Name
        """

        task_object_type: str = Field(alias="taskObjectType")
        """
        The type of the task object (FILE, EMAIL, ...)
        """

        object_properties: list[str] = Field(alias="objectProperties")
        """
        List of file labels
        """

        image_id: str | None = Field(default=None, alias="imageId")
        """
        ID of the BA image
        """

        planned_duration: int = Field(alias="plannedDuration")
        """
        Planned analysis time (seconds)
        """

        bootkitmon_enable: bool = Field(alias="bootkitmonEnable")
        """
        Is bootkitmon enabled or not
        """

        planned_bootkitmon_duration: int | None = Field(default=None, alias="plannedBootkitmonDuration")
        """
        Planned time of the second stage analysis (seconds)
        """

        planned_total_duration: float | None = Field(default=None, alias="plannedTotalDuration")
        """
        Scheduled total time (main + bootkit + costs) - seconds
        """

        real_duration: float | None = Field(default=None, alias="realDuration")
        """
        Actual duration (seconds)
        """

        object_name: str = Field(alias="objectName")
        """
        File Name
        """

        object_sha256: str = Field(alias="objectSha256")
        """
        sha256 file
        """

        object_sandbox_type: str = Field(alias="objectSandboxType")
        """
        Sandbox file type
        """

        save_video: bool = Field(alias="saveVideo")
        """
        Is video saving enabled or not
        """

        convert_video: bool = Field(alias="convertVideo")
        """
        Is video conversion enabled or not
        """

        procdump_enable: bool = Field(alias="procdumpEnable")
        """
        Is procdump enabled or not
        """

        custom_command: str = Field(alias="customCommand")
        """
        A custom command to run
        """

        ts_created: float = Field(alias="tsCreated")
        """
        Task creation timestamp
        """

        ts_starting: float | None = Field(default=None, alias="tsStarting")
        """
        Timestamp recruitment attempts
        """

        ts_started: float | None = Field(default=None, alias="tsStarted")
        """
        Timestamp of the start of work
        """

        ts_ready: float | None = Field(default=None, alias="tsReady")
        """
        Readiness timestamp
        """

        ts_finished: float | None = Field(default=None, alias="tsFinished")
        """
        Completion timestamp
        """

        estimated_ts_finished: float | None = Field(default=None, alias="estimatedTsFinished")
        """
        Predicted completion time
        """

        error_text: str | None = Field(default=None, alias="errorText")
        """
        The error text. In addition to the constants defined below, there may be any error text.

        TIMEOUT_START_EXCEEDED, TIMEOUT_FINISH_EXCEEDED, TIMEOUT_DOOMED_TO_START
        """

    total: int
    """
    The total number of tasks that meet the search conditions
    """

    tasks: list[Task]
    """
    Task list
    """
