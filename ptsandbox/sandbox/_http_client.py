from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
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
        last_response: aiohttp.ClientResponse | None = None
        last_exc: ClientError | None = None

        for attempt in range(1, self.retries + 1):
            try:
                response = await self._session.request(method, url, **kwargs)
                if response.status < 500:
                    return response

                # 5xx — retryable, close the response and back off
                last_response = response
                response.release()
            except ClientError as e:
                last_exc = e

            if attempt < self.retries:
                delay = self.backoff_factor * attempt
                logger.debug("Attempt %d failed, retrying in %.1fs", attempt, delay)
                await asyncio.sleep(delay)

        # All retries exhausted — return last 5xx response if we have one,
        # otherwise re-raise the last ClientError
        if last_response is not None:
            return last_response
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("HTTP request failed with no response or exception")

    @asynccontextmanager
    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse]:
        response = await self._retry_request(method, url, **kwargs)
        try:
            if raise_for_status:
                response.raise_for_status()
            yield response
        finally:
            response.release()

    def get(self, url: str, **kwargs: Any) -> AbstractAsyncContextManager[aiohttp.ClientResponse]:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> AbstractAsyncContextManager[aiohttp.ClientResponse]:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> AbstractAsyncContextManager[aiohttp.ClientResponse]:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> AbstractAsyncContextManager[aiohttp.ClientResponse]:
        return self.request("DELETE", url, **kwargs)
