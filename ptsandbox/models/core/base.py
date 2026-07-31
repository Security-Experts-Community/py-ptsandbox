from __future__ import annotations

import logging
from typing import Any, Self

import aiohttp
import aiohttp.client_exceptions
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger(__name__)


class BaseRequest(BaseModel):
    """
    The base class for all Request models related to the sandbox.

    Alias conventions:
        - Public API requests (api/): fields use snake_case names that match
          the API directly — no aliases needed.
        - UI API requests (ui/): fields use snake_case Python names with
          ``serialization_alias="camelCase"`` so that ``dict()`` / ``json()``
          produce the camelCase keys the UI API expects.

    ``dict()`` and ``json()`` always exclude ``None`` fields and use aliases,
    because the API rejects requests containing ``null`` values.
    """

    model_config = ConfigDict(use_enum_values=True)

    def dict(self, exclude_none: bool = True, by_alias: bool = True, **kwargs: Any) -> dict[str, Any]:
        # The API does not like fields with None, so they must be excluded before exporting.
        # mode="json" ensures that UUID, datetime, and other non-JSON-native types are
        # converted to their string representations so aiohttp's json= can serialize them.
        return super().model_dump(exclude_none=exclude_none, by_alias=by_alias, mode="json", **kwargs)

    def json(self, exclude_none: bool = True, by_alias: bool = True, **kwargs: Any) -> str:
        # The API does not like fields with None, so they must be excluded before exporting.
        return super().model_dump_json(exclude_none=exclude_none, by_alias=by_alias, **kwargs)


class BaseResponse(BaseModel):
    """
    The base class for all Response models related to the sandbox.

    Alias conventions:
        - All response models use ``alias="camelCase"`` for validation, since
          both Public and UI APIs return camelCase JSON keys.
        - ``by_alias=True`` is not needed for responses (they are only parsed,
          not serialized back to the API), but ``dict()`` / ``json()`` on
          responses will use aliases by default via ``model_config``.
    """

    class Error(BaseModel):
        message: str

        type: str

    data: Any
    errors: list[Error] = Field(default_factory=list[Error])

    @classmethod
    async def build(cls, response: aiohttp.ClientResponse) -> Self:
        try:
            return cls.model_validate(await response.json())
        except (ValidationError, aiohttp.client_exceptions.ContentTypeError):
            logger.exception("Can't validate sandbox response")
            raise
