from typing import Any

import aiohttp
import aiohttp.client_exceptions
from loguru import logger
from pydantic import BaseModel, ConfigDict, ValidationError
from typing_extensions import Self

from ptsandbox import config


class SandboxBaseModel(BaseModel):
    """Базовый класс для всех Response моделей, связанных с песком"""

    @classmethod
    async def build_with_debug(
        cls,
        response: aiohttp.ClientResponse,
        report_suffix: str = "",
        **kwargs: Any,
    ) -> Self:
        try:
            return cls.model_validate(await response.json())
        except (ValidationError, aiohttp.client_exceptions.ContentTypeError) as err:
            report_name = f"report_debug{f'_{report_suffix}' if report_suffix else ''}.json"
            logger.warning(f"Invalid model deserialization for '{cls}'")
            if config.settings.DEBUG:
                logger.warning(f"Created '{report_name}'")
            logger.warning(f"error: {err}")
            logger.warning(f"Info: {kwargs}")
            config.create_debug_json(await response.read(), report_name)
            raise err


class SandboxBaseRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    # Базовый класс для всех моделей, отправляемых в песок

    def dict(self, exclude_none: bool = True, **kwargs: Any) -> dict[str, Any]:
        # Песок плюется на поля, в которых есть None, поэтому их надо исключить перед экспортом
        return super().model_dump(exclude_none=exclude_none, **kwargs)

    def json(self, exclude_none: bool = True, **kwargs: Any) -> str:
        # Песок плюется на поля, в которых есть None, поэтому их надо исключить перед экспортом
        return super().model_dump_json(exclude_none=exclude_none, **kwargs)


class SandboxBaseResponse(SandboxBaseModel):
    class Error(SandboxBaseModel):
        message: str
        type: str

    data: SandboxBaseModel
    errors: list[Error]


class SandboxException(Exception):
    pass
