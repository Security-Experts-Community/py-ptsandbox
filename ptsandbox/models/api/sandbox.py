from ptsandbox.models.core.base import BaseResponse
from ptsandbox.models.core.common import SandboxImageInfo


class SandboxGetImagesResponse(BaseResponse):
    """
    Your application can get a list of virtual machine images installed in the PT Sandbox.

    `<URL>/engines/sandbox/getImages`
    """

    data: list[SandboxImageInfo] = []
