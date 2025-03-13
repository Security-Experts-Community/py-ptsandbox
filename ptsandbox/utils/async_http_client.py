from __future__ import annotations

import asyncio
from typing import Any, Literal

import aiohttp
import loguru
from aiohttp import ClientError


class AsyncHTTPClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        logger: loguru.Logger,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        self._session = session
        self._logger = logger
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
                    self._logger.debug(f"Try {attempt}, exception during HTTP request - {e}")
                    delay = self.backoff_factor * attempt
                    await asyncio.sleep(delay)
                else:
                    self._logger.error(f"Exception during HTTP request - {ex}")
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
