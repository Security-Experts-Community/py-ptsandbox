from pydantic import BaseModel

from ptsandbox.models.core.base import BaseResponse


class CheckHealthResponse(BaseResponse):
    """
    Healthcheck results
    """

    class Data(BaseModel):
        status: str
        """
        Health status
        """

    data: Data


class GetVersionResponse(BaseResponse):
    """
    Get information about product
    """

    class Data(BaseModel):
        version: str
        """
        Product version, for example '5.11.0.12345'
        """

        edition: str
        """
        Filled in for test builds or certification builds.
        """

    data: Data
