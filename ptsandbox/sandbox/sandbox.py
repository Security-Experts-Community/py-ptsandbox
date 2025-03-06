import asyncio
from collections.abc import AsyncIterator
from os import PathLike
from pathlib import PurePath
from typing import BinaryIO
from uuid import UUID

from aiohttp import ClientTimeout
from loguru import logger

from ptsandbox import config
from ptsandbox.models import (
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
    SandboxCreateRescanTaskRequest,
    SandboxCreateScanTaskRequest,
    SandboxCreateScanURLTaskRequest,
    SandboxDownloadArtifactRequest,
    SandboxKey,
    SandboxReportRequest,
)
from ptsandbox.models.api.analysis import (
    SandboxCreateNewScanTaskRequest,
    SandboxOptionsNew,
)
from ptsandbox.sandbox.sandbox_api import SandboxApi


class Sandbox:
    """
    Основной класс описывающий взаимодействие с песочницей через API
    """

    api: SandboxApi

    def __init__(
        self,
        key: SandboxKey,
        default_timeout: ClientTimeout = ClientTimeout(
            total=None,
            connect=None,
            sock_read=40.0,
            sock_connect=20.0,
        ),
        upload_semaphore_size: int = 4,
        proxy: str | None = None,
    ):
        self.api = SandboxApi(
            key,
            default_timeout=default_timeout,
            upload_semaphore_size=upload_semaphore_size,
            proxy=proxy,
        )

    async def new_rescan(
        self,
        raw_trace: str | PurePath | BinaryIO,
        raw_network: str | PurePath | BinaryIO,
        rules: bytes | None = None,
        options: SandboxCreateRescanTaskRequest.Options | None = None,
        read_timeout: int | None = None,
        async_result: bool = False,
    ) -> SandboxBaseTaskResponse:
        """
        Создание рескана в песке для проверки корреляционных правил
        """

        uploaded_dummy = await self.api.upload_file(data=config.FAKE_PDF)
        uploaded_trace = await self.api.upload_file(file=raw_trace)
        uploaded_network = await self.api.upload_file(file=raw_network)

        options = options or SandboxCreateScanTaskRequest.Options()

        if rules is not None:
            uploaded_rules = await self.api.upload_file(data=rules)
            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxCreateRescanTaskRequest(
            file_uri=uploaded_dummy.data.file_uri,
            file_name=config.FAKE_NAME,
            raw_events_uri=uploaded_trace.data.file_uri,
            raw_network_uri=uploaded_network.data.file_uri,
            options=options,
            async_result=async_result,
        )

        return await self.api.create_rescan(scan, read_timeout)

    async def new_scan(
        self,
        file: str | PurePath | BinaryIO,
        name: str | None = None,
        rules: bytes | None = None,
        options: SandboxCreateScanTaskRequest.Options | None = None,
        read_timeout: int | None = None,
        upload_timeout: float = 300,
        async_result: bool = False,
    ) -> SandboxBaseTaskResponse:
        """Отправить образец на сканирование в песок"""

        options = options or SandboxCreateScanTaskRequest.Options()

        upload_name = None
        if name:
            upload_name = name
        elif isinstance(file, str):
            upload_name = file
        elif isinstance(file, PathLike):
            upload_name = str(file)

        uploaded_file = await self.api.upload_file(file=file, upload_timeout=upload_timeout)
        file_uri = uploaded_file.data.file_uri

        if rules is not None:
            uploaded_rules = await self.api.upload_file(data=rules, upload_timeout=upload_timeout)
            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxCreateScanTaskRequest(
            file_uri=file_uri,
            file_name=upload_name,
            options=options,
            async_result=async_result,
        )

        return await self.api.create_scan(scan, read_timeout)

    async def new_scan_v2(
        self,
        file: str | PurePath | BinaryIO,
        name: str | None = None,
        rules: bytes | None = None,
        options: SandboxOptionsNew = SandboxOptionsNew(),
        read_timeout: int | None = None,
        upload_timeout: float = 300,
        async_result: bool = False,
        priority: int = 3,
    ) -> SandboxBaseTaskResponse:
        """
        Отправить образец на сканирование в песок с помощью нового метода

        Может быть доступен не во всех песках
        """

        options = options or SandboxOptionsNew()

        upload_name = None
        if name:
            upload_name = name
        elif isinstance(file, str):
            upload_name = file
        elif isinstance(file, PathLike):
            upload_name = str(file)

        uploaded_file = await self.api.upload_file(file=file, upload_timeout=upload_timeout)
        file_uri = uploaded_file.data.file_uri

        if rules is not None:
            uploaded_rules = await self.api.upload_file(data=rules, upload_timeout=upload_timeout)
            options.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxCreateNewScanTaskRequest(
            file_uri=file_uri,
            file_name=upload_name,
            sandbox=options,
            async_result=async_result,
            priority=priority,
        )

        return await self.api.create_scan_new(scan, read_timeout)

    async def new_url_scan(
        self,
        url: str,
        rules: bytes | None = None,
        options: SandboxCreateScanURLTaskRequest.Options | None = None,
        read_timeout: int | None = None,
        async_result: bool = False,
    ) -> SandboxBaseTaskResponse:
        """Отправить ссылку на сканирование в песок"""

        options = options or SandboxCreateScanURLTaskRequest.Options()

        if rules is not None:
            uploaded_rules = await self.api.upload_file(data=rules)
            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxCreateScanURLTaskRequest(url=url, options=options, async_result=async_result)

        return await self.api.create_scan_url(scan, read_timeout)

    async def wait_for_report(
        self,
        base_time: float,
        base_report: SandboxBaseTaskResponse,
        error_limit: int = 3,
    ) -> SandboxBaseTaskResponse | None:
        """Ожидание ответа от песка"""

        short_report = base_report.get_short_report()
        if not short_report:
            logger.warning(f"WTF??: {base_report}")
            return None

        if base_report.get_long_report() is not None:
            return base_report

        elapsed_time: float = 0
        wait_time = base_time / 64

        error_counter: int = 0
        while elapsed_time <= base_time:
            try:
                check = await self.get_report(short_report.scan_id)
            except Exception as ex:
                error_counter += 1
                logger.warning(f"Maybe dead sandbox {ex!r}, {self=}, {short_report.scan_id=}")

                if error_counter >= error_limit:
                    return None

                continue

            full_report = check.get_long_report()
            if full_report:
                return check

            await asyncio.sleep(wait_time)
            elapsed_time += wait_time
            if elapsed_time >= base_time / 2:
                logger.trace(f"{short_report.scan_id=} SO SLOW {elapsed_time}s / estimated {base_time}s")

        return None

    async def check_task(self, task_id: str | UUID) -> SandboxCheckTaskResponse:
        """
        Проверить состояние, задание завершено или нет
        """

        scan_id = UUID(task_id) if isinstance(task_id, str) else task_id

        return await self.api.check_task(SandboxCheckTaskRequest(scan_id=scan_id))

    async def get_report(self, task_id: str | UUID) -> SandboxBaseTaskResponse:
        """
        Забрать полноценный репорт
        """

        scan_id = UUID(task_id) if isinstance(task_id, str) else task_id

        return await self.api.get_report(SandboxReportRequest(scan_id=scan_id))

    async def get_file(self, sha256: str) -> bytes:
        data = SandboxDownloadArtifactRequest(file_uri=f"sha256:{sha256}")
        return (await self.api.download_artifact(data)).read()

    async def get_file_iter(self, sha256: str) -> AsyncIterator[bytes]:
        data = SandboxDownloadArtifactRequest(file_uri=f"sha256:{sha256}")

        async for result in self.api.download_artifact_iter(data):
            yield result
