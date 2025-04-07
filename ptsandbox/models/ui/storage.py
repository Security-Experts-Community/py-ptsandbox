from typing import NotRequired, TypedDict


class StorageItem(TypedDict):
    """
    A small abstraction that allows you to better type an object
    """

    sha256: str
    name: NotRequired[str]
