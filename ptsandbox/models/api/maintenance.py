from __future__ import annotations

from ptsandbox.models.core.base import BaseResponse, SandboxModel


class SandboxGetHealthStatusResponse(BaseResponse):
    """
    Healthcheck results
    """

    class Data(SandboxModel):
        status: str
        """
        Health status
        """

    data: Data


class SandboxGetVersionResponse(BaseResponse):
    """
    Get information about the product
    """

    class Data(SandboxModel):
        version: str
        """
        Product version, for example '5.11.0.12345'
        """

        edition: str
        """
        Filled in for test builds or certification builds.
        """

    data: Data
