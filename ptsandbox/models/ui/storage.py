from __future__ import annotations

import sys
from typing import NotRequired

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class StorageItem(TypedDict):
    """
    A small abstraction that allows you to better type an object
    """

    sha256: str
    name: NotRequired[str]
