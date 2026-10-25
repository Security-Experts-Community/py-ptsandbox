from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING
from uuid import UUID

import aiohttp

if TYPE_CHECKING:
    from multidict import MultiMapping

    from ptsandbox.models.core.base import BaseResponse
    from ptsandbox.models.core.enum import ScanState


class SandboxException(Exception):
    """Base exception for all custom errors raised by the library."""


class SandboxApiError(aiohttp.ClientResponseError, SandboxException):
    """
    Raised when the sandbox responds with an HTTP error status.

    It is a ``ClientResponseError``, so existing handlers keep working, but it also
    carries what the sandbox said about the failure: the ``errors`` list from the
    JSON body (if any) and the raw ``body`` text.
    """

    def __init__(
        self,
        request_info: aiohttp.RequestInfo,
        history: tuple[aiohttp.ClientResponse, ...],
        *,
        status: int,
        message: str,
        headers: MultiMapping[str] | None = None,
        errors: Iterable[BaseResponse.Error] = (),
        body: str = "",
    ) -> None:
        super().__init__(request_info, history, status=status, message=message, headers=headers)
        self.errors = list(errors)
        self.body = body


class SandboxUploadException(SandboxException):
    """Raised when uploading one or more files to the sandbox fails."""


class SandboxTooManyErrorsException(SandboxException):
    """
    Raised by ``wait_for_report`` when the number of consecutive errors
    while polling for a scan result exceeds the configured ``error_limit``.
    """


class SandboxWaitTimeoutException(SandboxException):
    """
    Raised by ``wait_for_report`` when the scan result is not ready
    within the specified ``wait_time``.
    """


class SandboxScanNotFullException(SandboxException):
    """
    Raised by ``wait_for_report`` when the scan reaches a terminal state but the
    behavioral analysis did not produce a full report.

    This means the task is no longer running, so it is useless to keep waiting: the
    report endpoint will never return a full (long) report for it. The terminal state
    and any scan errors are attached for the caller to react to — the error ``type``
    values (e.g. ``sandbox_run_sample``, ``internal``, ``max_depth_exceeded``) carry
    the closest thing to an error code available via the public API.
    """

    def __init__(
        self,
        scan_id: UUID,
        scan_state: ScanState,
        errors: Iterable[BaseResponse.Error] = (),
    ) -> None:
        self.scan_id = scan_id
        self.scan_state = scan_state
        self.errors = list(errors)

        msg = f"Scan {scan_id} finished with state={scan_state}, but no full report is available"
        if self.errors:
            details = ", ".join(f"{error.type}: {error.message}" for error in self.errors)
            msg += f"; errors={details}"

        super().__init__(msg)
