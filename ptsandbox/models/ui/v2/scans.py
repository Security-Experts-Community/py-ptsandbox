from ptsandbox.models.core import SandboxBaseModel
from ptsandbox.models.ui.v2.common import Scan


class SandboxUIScansResponse(SandboxBaseModel):
    """Результаты сканирования"""

    scans: list[Scan]
