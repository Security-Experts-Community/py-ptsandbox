from collections.abc import AsyncIterator
from typing import Any, Literal, Self, TypeVar, overload

import aiohttp
from aiohttp_socks import ProxyConnector
from pydantic import BaseModel

from ptsandbox.models import SandboxKey
from ptsandbox.sandbox._http_client import AsyncHTTPClient

_CHUNK_SIZE = 1024 * 1024

T = TypeVar("T", bound=BaseModel)


class BaseSandboxClient:
    """
    Shared base for SandboxApi and SandboxUI.

    Centralizes aiohttp session creation (with proxy/connector logic),
    the AsyncHTTPClient wrapper, session cleanup via close(), and async
    context manager support (`async with client: ...`).
    """

    key: SandboxKey
    session: aiohttp.ClientSession
    default_timeout: aiohttp.ClientTimeout
    http_client: AsyncHTTPClient

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: aiohttp.ClientTimeout,
        proxy: str | None = None,
        connection_retries: int = 3,
        **session_kwargs: Any,
    ) -> None:
        assert connection_retries > 0, "Connection retries must be greater than 0"

        self.key = key
        self.default_timeout = default_timeout

        # i know this is strange, but aiodns => c-ares can't correctly resolve dns names
        # https://github.com/c-ares/c-ares/issues/642
        connector = (
            ProxyConnector.from_url(proxy, ssl=False)
            if proxy
            else aiohttp.TCPConnector(
                ssl=False,
                resolver=aiohttp.ThreadedResolver(),
            )
        )
        self.session = aiohttp.ClientSession(
            timeout=self.default_timeout,
            connector=connector,
            **session_kwargs,
        )
        self.http_client = AsyncHTTPClient(
            self.session,
            retries=connection_retries,
        )

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if not self.session.closed:
            await self.session.close()

    @overload
    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        response_model: type[T],
        **kwargs: Any,
    ) -> T: ...

    @overload
    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        response_model: None = None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse: ...

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        response_model: type[T] | None = None,
        **kwargs: Any,
    ) -> T | aiohttp.ClientResponse:
        """
        Send an HTTP request, raise on error, and optionally parse the response.

        When *response_model* is provided: calls ``raise_for_status()`` and
        parses the JSON body into the given model.

        When *response_model* is ``None``: returns the raw response without
        ``raise_for_status()`` — the caller handles error checking.
        """
        response = await self.http_client.request(method, url, **kwargs)
        if response_model is not None:
            response.raise_for_status()
            return response_model.model_validate(await response.json())
        return response

    @staticmethod
    async def _iter_chunks(response: aiohttp.ClientResponse) -> AsyncIterator[bytes]:
        """Yield response body in 1 MiB chunks."""
        async for chunk in response.content.iter_chunked(_CHUNK_SIZE):
            yield chunk

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()
