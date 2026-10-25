from collections.abc import AsyncIterator
from typing import Any, Literal, Self, TypeVar

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
        if connection_retries < 1:
            raise ValueError("Connection retries must be greater than 0")

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

    def _timeout(self, **overrides: float | None) -> aiohttp.ClientTimeout:
        """Return the default timeout with the given fields replaced."""
        default = self.default_timeout
        fields: dict[str, Any] = {
            "total": default.total,
            "connect": default.connect,
            "sock_read": default.sock_read,
            "sock_connect": default.sock_connect,
            "ceil_threshold": default.ceil_threshold,
        }
        fields.update(overrides)
        return aiohttp.ClientTimeout(**fields)

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if not self.session.closed:
            await self.session.close()

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        response_model: type[T],
        **kwargs: Any,
    ) -> T:
        """
        Send an HTTP request, raise on error, and parse the response.

        Raises on error statuses and parses the JSON body into the given
        ``response_model``. The underlying response is released automatically.
        """
        async with self.http_client.request(method, url, **kwargs) as response:
            # parsing the raw bytes in pydantic-core is faster than json.loads + model_validate
            # and doesn't build an intermediate dict for large reports
            return response_model.model_validate_json(await response.read())

    @staticmethod
    async def _iter_chunks(response: aiohttp.ClientResponse) -> AsyncIterator[bytes]:
        """Yield response body in 1 MiB chunks."""
        async for chunk in response.content.iter_chunked(_CHUNK_SIZE):
            yield chunk

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()
