from enum import Enum
from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field


class SandboxKey(BaseModel):
    """
    Abstraction over the key that is used to send to the sandbox
    """

    class UI(BaseModel):
        model_config = ConfigDict(use_enum_values=True)

        class AuthType(int, Enum):
            default = 0
            ldap = 1

        login: str
        password: str
        auth_type: AuthType = AuthType.default

    name: str
    """
    Custom key name
    """

    key: str
    """
    The key received in the sandbox interface
    """

    host: str
    """
    Hostname of the sandbox instance

    For example: `1.1.1.1` or `sandbox.example.com` without https etc
    """

    description: str = ""
    """
    A description of the key for easy representation somewhere in the interface
    """

    max_workers: int = Field(default=8, ge=1)
    """
    The maximum number of simultaneously running behavioral nodes

    The quantity can be found in the interface
    """

    ui: UI | None = None
    """
    If necessary, you can also access the sandbox via the UI API
    """

    @cached_property
    def url(self) -> str:
        """
        https address for connecting via API
        """

        return f"https://{self.host}/api/v1"

    @cached_property
    def debug_url(self) -> str:
        """
        https address for connecting via debug API
        """

        return f"https://{self.host}/api/debug"

    @cached_property
    def ui_url(self) -> str:
        """
        https address for connecting via UI API
        """

        return f"https://{self.host}/api/ui"

    def __repr__(self) -> str:
        return f"{self.name} for {self.host} ({self.max_workers})" + (
            f"({self.description})" if self.description else ""
        )

    def __key(self) -> tuple[str, str, str]:
        return (self.name, self.key, self.host)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, value: object) -> bool:
        if isinstance(value, SandboxKey):
            return self.__key() == value.__key()

        return False
