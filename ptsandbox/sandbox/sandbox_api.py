import asyncio
import io
from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import PurePath
from typing import BinaryIO

import aiohttp
import attr
from aiohttp_socks import ProxyConnector
from loguru import logger

from ptsandbox.models import (
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
    SandboxCreateScanTaskRequest,
    SandboxCreateScanURLTaskRequest,
    SandboxDownloadArtifactRequest,
    SandboxGetImagesResponse,
    SandboxKey,
    SandboxReportRequest,
    SandboxUploadScanFileResponse,
)
from ptsandbox.models.api.analysis import SandboxCreateNewScanTaskRequest
from ptsandbox.models.core.base import SandboxException
from ptsandbox.utils.async_http_client import AsyncHTTPClient


class SandboxApi:
    key: SandboxKey

    session: aiohttp.ClientSession

    default_timeout: aiohttp.ClientTimeout

    upload_semaphore: asyncio.Semaphore

    def __init__(
        self,
        key: SandboxKey,
        default_timeout: aiohttp.ClientTimeout,
        upload_semaphore_size: int = 4,
        proxy: str | None = None,
    ) -> None:
        self.key = key
        self.default_timeout = default_timeout
        self.session = aiohttp.ClientSession(
            timeout=self.default_timeout,
            connector=(
                ProxyConnector.from_url(proxy, ssl=False)
                if proxy
                else aiohttp.TCPConnector(
                    ssl=False,
                    # i know this is strange, but aiodns => c-ares can't resolve dns names
                    # https://github.com/c-ares/c-ares/issues/642
                    resolver=aiohttp.ThreadedResolver(),
                )
            ),
            headers={"X-Api-Key": key.key},
        )
        self.http_client = AsyncHTTPClient(self.session, logger=logger)

        self.upload_semaphore = asyncio.Semaphore(upload_semaphore_size)

    async def _upload_bytes(self, file: BinaryIO) -> AsyncIterator[bytes]:
        while chunk := file.read(1024 * 1024):
            yield chunk

    async def upload_file(
        self,
        file: str | PurePath | BinaryIO | None = None,
        data: bytes | None = None,
        upload_timeout: float = 300,
    ) -> SandboxUploadScanFileResponse:
        """
        Загружает файл в песок.
        Возвращается ссылка на файл во временном хранилище и время жизни этого файла, либо кидается исключение

        file: path to file or file-like object
        data: bytes to upload
        read_size: when specified "file", describes read size
        """

        timeout = attr.evolve(self.default_timeout, total=upload_timeout)

        match file, data:
            case None, None:
                raise SandboxException("file and data are None")
            case None, _:
                async with self.upload_semaphore:
                    response = await self.http_client.post(
                        f"{self.key.url}/storage/uploadScanFile",
                        data=data,
                        timeout=timeout,
                    )
            case _, None:
                # we can't use aiofiles here, because aiohttp try use chunked encoding
                # sandbox (or maybe aiohttp) can't correctly handle chunked encoding (i have no idea why, don't ask me)
                # so we need this clunky code
                async with self.upload_semaphore:
                    if isinstance(file, str | PurePath):
                        with open(file, "rb") as fd:
                            response = await self.http_client.post(
                                f"{self.key.url}/storage/uploadScanFile",
                                data=fd,
                                timeout=timeout,
                            )
                    elif isinstance(file, io.IOBase):
                        response = await self.http_client.post(
                            f"{self.key.url}/storage/uploadScanFile",
                            data=self._upload_bytes(file),
                            timeout=timeout,
                        )
                    else:
                        raise SandboxException(f"file type {type(file)} is not supported")
            case _, _:
                raise SandboxException("file and data are not None, specify only one")

        response.raise_for_status()

        return await SandboxUploadScanFileResponse.build_with_debug(
            response=response, report_suffix="api_upload_scan_file"
        )

    async def download_artifact(
        self,
        data: SandboxDownloadArtifactRequest,
        read_timeout: int = 120,
    ) -> BinaryIO:
        """Скачать файл"""

        timeout = attr.evolve(self.default_timeout, sock_read=read_timeout)

        response = await self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            headers={"Content-Type": "application/json"},
            data=data.json(),
            timeout=timeout,
        )
        response.raise_for_status()

        return BytesIO(await response.read())

    async def download_artifact_iter(
        self, data: SandboxDownloadArtifactRequest, read_timeout: int = 120
    ) -> AsyncIterator[bytes]:
        """Тоже самое, что download_artifact, но возвращает итератор"""

        timeout = attr.evolve(self.default_timeout, sock_read=read_timeout)

        response = await self.http_client.post(
            f"{self.key.url}/storage/downloadArtifact",
            headers={"Content-Type": "application/json"},
            data=data.json(),
            timeout=timeout,
        )
        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    async def create_scan(
        self,
        data: SandboxCreateScanTaskRequest,
        read_timeout: int | None = None,
    ) -> SandboxBaseTaskResponse:
        """Запустить проверку загруженного файла."""

        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + (read_timeout if read_timeout else 0),
        )

        response = await self.http_client.post(
            f"{self.key.url}/analysis/createScanTask", json=data.dict(), timeout=timeout
        )
        response.raise_for_status()

        return await SandboxBaseTaskResponse.build_with_debug(response, "api_create_scan", req=data)

    async def create_scan_new(
        self,
        data: SandboxCreateNewScanTaskRequest,
        read_timeout: int | None = None,
    ) -> SandboxBaseTaskResponse:
        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.sandbox.analysis_duration * 4
            + (300 if data.sandbox.analysis_duration < 80 else 120)
            + (read_timeout if read_timeout else 0),
        )

        response = await self.http_client.post(
            f"{self.key.debug_url}/analysis/createBAScanTask", json=data.dict(), timeout=timeout
        )
        response.raise_for_status()

        return await SandboxBaseTaskResponse.build_with_debug(response, "api_create_scan", req=data)

    async def create_scan_url(
        self, data: SandboxCreateScanURLTaskRequest, read_timeout: int | None = None
    ) -> SandboxBaseTaskResponse:
        """Проверить URL (Скачать файл по данному URL и проверить его) переданными настройками."""

        timeout = attr.evolve(
            self.default_timeout,
            sock_read=data.options.sandbox.analysis_duration * 4
            + (300 if data.options.sandbox.analysis_duration < 80 else 120)
            + (read_timeout if read_timeout else 0),
        )

        response = await self.http_client.post(
            f"{self.key.url}/analysis/createScanURLTask", json=data.dict(), timeout=timeout
        )
        response.raise_for_status()

        return await SandboxBaseTaskResponse.build_with_debug(response, "api_create_scan", req=data)

    async def check_task(self, data: SandboxCheckTaskRequest) -> SandboxCheckTaskResponse:
        """Проверка результата сканирования запущенного с флагом async_result"""

        response = await self.http_client.post(
            f"{self.key.url}/analysis/checkTask", headers={"Content-Type": "application/json"}, data=data.json()
        )
        response.raise_for_status()

        return await SandboxCheckTaskResponse.build_with_debug(response, "api_check_scan", req=data)

    async def get_report(self, data: SandboxReportRequest) -> SandboxBaseTaskResponse:
        """
        Получение полного отчета о сканировании задания

        Проверка выполнена успешно. Результаты — в теле сообщения. Если результат сканирования еще не готов - ключи result, artifacts отсутствуют.

        WARNING: вернутся результаты только для того ключа, с которым был запущен анализ. Ограничения песка.
        """

        response = await self.http_client.post(
            f"{self.key.url}/analysis/report", headers={"Content-Type": "application/json"}, data=data.json()
        )
        response.raise_for_status()

        return await SandboxBaseTaskResponse.build_with_debug(response, "api_report", req=data)

    async def create_rescan(
        self,
        data: SandboxCreateScanTaskRequest,
        read_timeout: int | None = None,
    ) -> SandboxBaseTaskResponse:
        """Отправить на рескан"""

        timeout = attr.evolve(
            self.default_timeout,
            sock_read=(
                round(data.options.sandbox.analysis_duration * 1.5)
                if data.options.sandbox.analysis_duration > 70
                else 70
            )
            + (read_timeout if read_timeout else 0),
        )
        response = await self.http_client.post(
            f"{self.key.url}/analysis/createRetroTask",
            headers={"Content-Type": "application/json"},
            data=data.json(),
            timeout=timeout,
        )

        response.raise_for_status()

        return await SandboxBaseTaskResponse.build_with_debug(response, "api_create_rescan", req=data)

    async def get_email_headers(
        self,
        file: str | PurePath | BinaryIO | None = None,
        data: bytes | None = None,
    ) -> bytes:
        """
        Загрузить письмо для получения заголовков
        """

        match file, data:
            case None, None:
                raise SandboxException("file and data are None")
            case None, _:
                async with self.upload_semaphore:
                    response = await self.http_client.post(
                        f"{self.key.url}/analysis/getHeaders",
                        data=data,
                    )
            case _, None:
                # we can't use aiofiles here, because aiohttp try use chunked encoding
                # sandbox (or maybe aiohttp) can't correctly handle chunked encoding (i have no idea why, don't ask me)
                # so we need this clunky code
                async with self.upload_semaphore:
                    if isinstance(file, str | PurePath):
                        with open(file, "rb") as fd:
                            response = await self.http_client.post(
                                f"{self.key.url}/analysis/getHeaders",
                                data=fd,
                            )
                    elif isinstance(file, io.IOBase):
                        response = await self.http_client.post(
                            f"{self.key.url}/analysis/getHeaders",
                            data=self._upload_bytes(file),
                        )
                    else:
                        raise SandboxException(f"file type {type(file)} is not supported")
            case _, _:
                raise SandboxException("file and data are not None, specify only one")

        response.raise_for_status()

        return await response.read()  # type: ignore

    async def get_images(self) -> SandboxGetImagesResponse:
        response = await self.http_client.post(
            f"{self.key.url}/engines/sandbox/getImages",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

        return await SandboxGetImagesResponse.build_with_debug(response, "api_get_images")

    def __del__(self) -> None:
        if not self.session.closed:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            if loop.is_running():
                loop.create_task(self.session.close())
            else:
                loop.run_until_complete(self.session.close())
