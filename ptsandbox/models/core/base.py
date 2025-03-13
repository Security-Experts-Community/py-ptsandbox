from typing import Any

import aiohttp
import aiohttp.client_exceptions
from loguru import logger
from pydantic import BaseModel, ConfigDict, ValidationError
from typing_extensions import Self


class BaseRequest(BaseModel):
    """
    The base class for all Request models related to the sandbox
    """

    model_config = ConfigDict(use_enum_values=True)

    def dict(self, exclude_none: bool = True, by_alias: bool = True, **kwargs: Any) -> dict[str, Any]:
        # The API does not like fields with None, so they must be excluded before exporting.
        return super().model_dump(exclude_none=exclude_none, by_alias=by_alias, **kwargs)

    def json(self, exclude_none: bool = True, by_alias: bool = True, **kwargs: Any) -> str:
        # The API does not like fields with None, so they must be excluded before exporting.
        return super().model_dump_json(exclude_none=exclude_none, by_alias=by_alias, **kwargs)


class BaseResponse(BaseModel):
    """
    The base class for all Response models related to the sandbox
    """

    class Error(BaseModel):
        message: str

        type: str

    data: Any
    errors: list[Error]

    @classmethod
    async def build(cls, response: aiohttp.ClientResponse) -> Self:
        try:
            return cls.model_validate(await response.json())
        except (ValidationError, aiohttp.client_exceptions.ContentTypeError) as err:
            logger.error(f"error: {err}")
            raise err


class SandboxException(Exception): ...


class SandboxUploadException(SandboxException): ...


class SandboxTooManyErrorsException(SandboxException): ...


class SandboxWaitTimeoutException(SandboxException): ...


class SandboxFileNotFoundException(SandboxException): ...
