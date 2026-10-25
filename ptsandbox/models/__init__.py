from typing import TYPE_CHECKING, Any

from ptsandbox.models import api, core
from ptsandbox.models.api import *
from ptsandbox.models.core import *

if TYPE_CHECKING:
    from ptsandbox.models.ui import *

# UI API models are rarely needed and their import is relatively slow,
# so ptsandbox.models.ui is loaded on first access to any of them
_UI_NAMES = frozenset(
    {
        "CorrelationInfo",
        "DetectionUI",
        "EntryPoint",
        "EntryPointRules",
        "EntryPointSettings",
        "EntryPointToken",
        "Error",
        "ErrorWithLimit",
        "FilterValues",
        "HTTPDescription",
        "MailResult",
        "SMTPDefaultRecord",
        "SandboxAVDistributionPacksResponse",
        "SandboxAVEngineSettingsResponse",
        "SandboxAVEnginesResponse",
        "SandboxArtifactsFilterValuesResponse",
        "SandboxBaqueueTasksResponse",
        "SandboxClusterStatusResponse",
        "SandboxComponentsResponse",
        "SandboxCreateEntryPointRequest",
        "SandboxCreateTokenResponse",
        "SandboxEntryPointResponse",
        "SandboxEntryPointsResponse",
        "SandboxEntryPointsTypesResponse",
        "SandboxInfo",
        "SandboxLicenseResponse",
        "SandboxLicenseUpdateResponse",
        "SandboxScansResponse",
        "SandboxSystemSettingsResponse",
        "SandboxSystemStatusResponse",
        "SandboxSystemVersionResponse",
        "SandboxTasksFilterValuesResponse",
        "SandboxTasksSummaryResponse",
        "SandboxTokensResponse",
        "SandboxTreeResponse",
        "SandboxUITasksResponse",
        "SandboxUpdateSystemSettingsRequest",
        "Scan",
        "ScanArtifact",
        "StorageItem",
        "Task",
        "Token",
        "TreeNode",
    }
)

__all__ = [*api.__all__, *core.__all__, *sorted(_UI_NAMES)]


if not TYPE_CHECKING:
    # hidden from type checkers: they see the real names via the import above,
    # so typos like `from ptsandbox.models import Typo` are still reported

    def __getattr__(name: str) -> Any:
        # `ptsandbox.models.ui` itself: a submodule becomes an attribute only after it's imported
        if name == "ui":
            import ptsandbox.models.ui

            return ptsandbox.models.ui

        if name in _UI_NAMES:
            from ptsandbox.models import ui

            value = getattr(ui, name)
            globals()[name] = value
            return value

        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __dir__() -> list[str]:
        return sorted({*globals(), *_UI_NAMES})
