from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any

from ptsandbox.exceptions import SandboxException

_CHUNK_SIZE = 1024 * 1024


class Payload:
    """
    A request body that can be sent more than once.

    Every ``open()`` call yields a fresh body positioned at the start of the data,
    so the HTTP client can safely resend it on retry. Non-seekable streams can only
    be read once, so ``replayable`` is ``False`` for them and the request is not retried.
    """

    def __init__(self, file: str | Path | bytes | bytearray | memoryview | IO[bytes]) -> None:
        match file:
            case str() | Path():
                self._path: Path | None = Path(file)
                self._data: bytes | None = None
                self._stream: IO[bytes] | None = None
                self.replayable = True
            case bytes() | bytearray() | memoryview():
                self._path = None
                self._data = bytes(file)
                self._stream = None
                self.replayable = True
            case _ if hasattr(file, "read"):
                self._path = None
                self._data = None
                self._stream = file
                self.replayable = file.seekable()
                self._start = file.tell() if self.replayable else 0
            case _:
                raise SandboxException(f"Specified file type doesn't supported {type(file)}!")

    @staticmethod
    async def _iter_stream(stream: IO[bytes]) -> AsyncIterator[bytes]:
        while chunk := stream.read(_CHUNK_SIZE):
            yield chunk

    @contextmanager
    def open(self) -> Iterator[Any]:
        """Yield a body suitable for aiohttp's ``data=`` argument."""

        if self._path is not None:
            # we can't use aiofiles here, because aiohttp try use chunked encoding
            # sandbox (or maybe aiohttp) can't correctly handle chunked encoding
            # so we need this clunky code
            try:
                fd = open(self._path, "rb")
            except OSError as e:
                raise SandboxException(f"Can't open file {str(self._path)!r}") from e
            with fd:
                yield fd
        elif self._data is not None:
            yield self._data
        else:
            assert self._stream is not None
            if self.replayable:
                self._stream.seek(self._start)
            # a generator, so aiohttp doesn't close the caller's stream after sending
            yield self._iter_stream(self._stream)
