import functools
import inspect
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, overload

if TYPE_CHECKING:
    from ptsandbox.sandbox.ui import SandboxUI

P = ParamSpec("P")
R = TypeVar("R")


@overload
def token_required(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...


@overload
def token_required(func: Callable[P, AsyncIterator[bytes]]) -> Callable[P, AsyncIterator[bytes]]: ...


def token_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that ensures a valid UI access token before calling the wrapped method."""

    if inspect.isasyncgenfunction(func):

        @functools.wraps(func)
        # idk how to fix mypy complains about next line
        def wrapper_iter(self: "SandboxUI", *args: P.args, **kwargs: P.kwargs) -> Any:  # type: ignore
            async def inner() -> Any:
                await self._ensure_token()
                async for chunk in func(self, *args, **kwargs):
                    yield chunk

            return inner()

        return wrapper_iter
    else:

        @functools.wraps(func)
        # idk how to fix mypy complains about next line
        async def wrapper(self: "SandboxUI", *args: P.args, **kwargs: P.kwargs) -> Any:  # type: ignore
            await self._ensure_token()
            return await func(self, *args, **kwargs)

        return wrapper
