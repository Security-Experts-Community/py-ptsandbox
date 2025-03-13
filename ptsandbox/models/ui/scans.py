from pydantic import BaseModel, Field

from ptsandbox.models.ui.common import Scan


class SandboxScansResponse(BaseModel):
    """
    Scan results
    """

    scans: list[Scan] = []

    yara_test_info: Scan | None = Field(default=None, alias="yaraTestInfo")

    yara_main_info: Scan | None = Field(default=None, alias="yaraMainInfo")
