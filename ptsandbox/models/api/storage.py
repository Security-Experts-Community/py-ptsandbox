from pydantic import BaseModel

from ptsandbox.models.core.base import BaseResponse


class SandboxUploadScanFileResponse(BaseResponse):
    """
    Before running the file analysis using the API, your application must upload this file to the sandbox.

    `<URL>/storage/uploadScanFile`
    """

    class Data(BaseModel):
        file_uri: str
        """
        The ID of the uploaded file, used to create the analysis task.
        """

        ttl: int
        """
        The waiting time for the scan to start after uploading the file (in seconds).
        If the analysis has not been started during this time, the file will be deleted.
        """

    data: Data
