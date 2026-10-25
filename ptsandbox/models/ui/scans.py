from __future__ import annotations

from pydantic import Field

from ptsandbox.models.core.base import SandboxModel
from ptsandbox.models.ui.common import Scan


class SandboxScansResponse(SandboxModel):
    """
    Scan results
    """

    scans: list[Scan] = Field(default_factory=list[Scan])

    yara_test_info: Scan | None = Field(default=None, alias="yaraTestInfo")

    yara_main_info: Scan | None = Field(default=None, alias="yaraMainInfo")
