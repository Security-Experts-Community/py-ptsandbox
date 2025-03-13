from pydantic import BaseModel

from ptsandbox.models.ui.common import Token


class SandboxTokensResponse(BaseModel):
    """
    Listing of current Public API tokens
    """

    total: int
    """
    The number of tokens in the system
    """

    entries: list[Token] = []
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
