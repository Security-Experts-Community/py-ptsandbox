from __future__ import annotations

from pydantic import Field

from ptsandbox.models.core.base import SandboxModel
from ptsandbox.models.ui.common import Token


class SandboxTokensResponse(SandboxModel):
    """
    Listing of current Public API tokens
    """

    total: int
    """
    The number of tokens in the system
    """

    entries: list[Token] = Field(default_factory=list[Token])
    """
    List of tokens
    """


class SandboxCreateTokenResponse(Token):
    token: str
    """
    The secret value of the token, which is shown only when creating a new PublicAPI token.
    """

    key: str
    """
    Hash of the secret value
    """
