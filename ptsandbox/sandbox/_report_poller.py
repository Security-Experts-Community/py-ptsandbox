from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING
from uuid import UUID

from ptsandbox.exceptions import SandboxTooManyErrorsException
from ptsandbox.models import (
    SandboxBaseTaskResponse,
    SandboxCheckTaskResponse,
    ScanState,
)
from ptsandbox.models.core.base import BaseResponse

if TYPE_CHECKING:
    from ptsandbox.sandbox.sandbox import Sandbox

logger = logging.getLogger(__name__)

_POLL_MAX_INTERVAL = 20.0
_POLL_MIN_INTERVAL = 2.0

NON_FULL_TERMINAL_SCAN_STATES = frozenset(
    {
        ScanState.PARTIAL,
        ScanState.UNSCANNED,
        ScanState.UNKNOWN,
    }
)

UNAVAILABLE_SCAN_STATES = frozenset({ScanState.UNSCANNED, ScanState.UNKNOWN})
TERMINAL_SCAN_STATES = NON_FULL_TERMINAL_SCAN_STATES | {ScanState.FULL}
BA_SUCCEEDED_SCAN_STATES = frozenset({ScanState.FULL, ScanState.PARTIAL})


def collect_behavioral_analysis_results(
    report: SandboxBaseTaskResponse,
) -> tuple[list[ScanState], list[BaseResponse.Error]]:
    long_report = report.get_long_report()
    if long_report is None:
        return [], []

    states: list[ScanState] = []
    errors: list[BaseResponse.Error] = []
    for artifact in long_report.artifacts:
        for engine_result in artifact.get_sandbox_results():
            states.append(engine_result.result.scan_state)
            errors.extend(engine_result.result.errors)
    return states, errors


def has_completed_behavioral_analysis(report: SandboxBaseTaskResponse) -> bool:
    ba_states, _ = collect_behavioral_analysis_results(report)
    if not ba_states:
        return True
    return any(state in BA_SUCCEEDED_SCAN_STATES for state in ba_states)


class ReportPoller:
    def __init__(self, sandbox: Sandbox, scan_with_source: bool) -> None:
        self._sandbox = sandbox
        self._scan_with_source = scan_with_source

    @staticmethod
    def poll_interval(elapsed_time: float, wait_time: float) -> float:
        remaining = (wait_time - elapsed_time) / wait_time
        start = min(_POLL_MAX_INTERVAL, wait_time / 4)
        return remaining * (start - _POLL_MIN_INTERVAL) + _POLL_MIN_INTERVAL

    @staticmethod
    def poll_schedule(wait_time: float) -> Iterator[float]:
        elapsed = 0.0
        while elapsed < wait_time:
            interval = min(ReportPoller.poll_interval(elapsed, wait_time), wait_time - elapsed)
            yield interval
            elapsed += interval

    @staticmethod
    def count_poll_error(error_counter: int, error_limit: int, scan_id: UUID, error: Exception) -> int:
        error_counter += 1
        logger.error("Maybe dead sandbox scan_id=%s", scan_id, exc_info=error)
        if error_counter >= error_limit:
            raise SandboxTooManyErrorsException("Too many errors while waiting report") from error
        return error_counter

    async def status(self, scan_id: UUID) -> SandboxCheckTaskResponse:
        if self._scan_with_source:
            return await self._sandbox.source_get_status(scan_id, allow_preflight=True)
        return await self._sandbox.check_task(scan_id, allow_preflight=True)

    async def report(self, scan_id: UUID) -> SandboxBaseTaskResponse:
        if self._scan_with_source:
            return await self._sandbox.api.source_get_report(scan_id)
        return await self._sandbox.get_report(scan_id)
