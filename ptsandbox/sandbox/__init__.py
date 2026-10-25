from typing import TYPE_CHECKING, Any

from ptsandbox.sandbox.sandbox import Sandbox

__all__ = ["Sandbox"]


if not TYPE_CHECKING:

    def __getattr__(name: str) -> Any:
        # the UI client is imported lazily (see Sandbox.__init__), but `ptsandbox.sandbox.ui` must stay reachable
        if name == "ui":
            import ptsandbox.sandbox.ui

            return ptsandbox.sandbox.ui

        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
