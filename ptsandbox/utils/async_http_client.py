from __future__ import annotations

import asyncio
import logging
from typing import Any, Literal

import aiohttp
from aiohttp import ClientError

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        self._session = session
        self.retries = retries
        self.backoff_factor = backoff_factor

    async def _retry_request(
        self,
        method: Literal["GET", "POST", "DELETE", "PUT", "PATCH"],
        url: str,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        ex = Exception()
        for attempt in range(1, self.retries + 1):
            try:
                response = await self._session.request(method, url, **kwargs)
                if response.status < 500:
                    return response
            except ClientError as e:
                ex = e
                if attempt < self.retries:
                    logger.debug("Attempt %d, exception during HTTP request - %r", e)

                    delay = self.backoff_factor * attempt
                    await asyncio.sleep(delay)
                else:
                    logger.exception("Unknown exception during HTTP request")
                    raise e
        raise ex or Exception("Unknown error during HTTP request")

    async def get(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        response = await self._retry_request("GET", url, **kwargs)
        return response

    async def post(self, url: str, data: Any | None = None, **kwargs: Any) -> aiohttp.ClientResponse:
        response = await self._retry_request("POST", url, data=data, **kwargs)
        return response

    async def put(self, url: str, data: Any | None = None, **kwargs: Any) -> aiohttp.ClientResponse:
        response = await self._retry_request("PUT", url, data=data, **kwargs)
        return response

    async def delete(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        response = await self._retry_request("DELETE", url, **kwargs)
        return response
