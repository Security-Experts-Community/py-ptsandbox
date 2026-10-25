from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Literal
from uuid import UUID

import aiohttp
from aiohttp import ClientError
from pydantic import ValidationError

from ptsandbox.exceptions import SandboxApiError
from ptsandbox.models.core.base import BaseResponse
from ptsandbox.sandbox._payload import Payload

logger = logging.getLogger(__name__)

Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

# requests with these methods can be safely sent again, others must opt in with retry=True
_IDEMPOTENT_METHODS: frozenset[str] = frozenset({"GET", "PUT", "DELETE"})


def _prepare_params(params: Mapping[str, Any]) -> dict[str, Any]:
    """
    Convert query parameters into types accepted by yarl.

    yarl rejects ``bool`` and silently turns ``UUID`` into a decimal integer,
    so both are converted to the string form the sandbox expects.
    """

    prepared: dict[str, Any] = {}
    for name, value in params.items():
        match value:
            case None:
                continue
            case bool():
                prepared[name] = "true" if value else "false"
            case UUID():
                prepared[name] = str(value)
            case _:
                prepared[name] = value
    return prepared


async def _raise_api_error(response: aiohttp.ClientResponse) -> None:
    """Raise SandboxApiError with the error details the sandbox put into the body."""

    body = await response.text(errors="replace")

    errors: list[BaseResponse.Error] = []
    try:
        raw_errors = json.loads(body).get("errors") or []
        errors = [BaseResponse.Error.model_validate(error) for error in raw_errors]
    except (ValueError, AttributeError, TypeError, ValidationError):
        pass

    message = response.reason or ""
    if errors:
        message += "; errors=" + ", ".join(f"{error.type}: {error.message}" for error in errors)

    raise SandboxApiError(
        response.request_info,
        response.history,
        status=response.status,
        message=message,
        headers=response.headers,
        errors=errors,
        body=body,
    )


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
        method: Method,
        url: str,
        *,
        retry: bool,
        payload: Payload | None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        # a one-shot stream can't be sent twice, so there's no point in retrying it
        attempts = self.retries if retry and (payload is None or payload.replayable) else 1

        for attempt in range(1, attempts + 1):
            try:
                if payload is None:
                    response = await self._session.request(method, url, **kwargs)
                else:
                    with payload.open() as data:
                        response = await self._session.request(method, url, data=data, **kwargs)

                if response.status < 500 or attempt == attempts:
                    return response

                # 5xx — retryable, close the response and back off
                response.release()
            except ClientError:
                if attempt == attempts:
                    raise

            delay = self.backoff_factor * attempt
            logger.debug("Attempt %d failed, retrying in %.1fs", attempt, delay)
            await asyncio.sleep(delay)

        raise RuntimeError("HTTP request failed with no response or exception")

    @asynccontextmanager
    async def request(
        self,
        method: Method,
        url: str,
        *,
        raise_for_status: bool = True,
        retry: bool | None = None,
        payload: Payload | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse]:
        """
        Send a request and yield the response.

        Args:
            raise_for_status: raise SandboxApiError on 4xx/5xx responses
            retry:
                Resend the request on connection errors and 5xx responses.

                By default only idempotent methods (GET, PUT, DELETE) are retried:
                resending e.g. a scan creation request may create duplicate tasks.
            payload: request body, reopened for every attempt
        """

        if retry is None:
            retry = method in _IDEMPOTENT_METHODS

        if isinstance(params := kwargs.get("params"), Mapping):
            kwargs["params"] = _prepare_params(params)

        response = await self._retry_request(method, url, retry=retry, payload=payload, **kwargs)
        try:
            if raise_for_status and response.status >= 400:
                await _raise_api_error(response)
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
