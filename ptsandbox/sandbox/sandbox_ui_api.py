import asyncio
import datetime
import random
import zipfile
from http import HTTPStatus
from io import BytesIO
from uuid import UUID

import aiohttp
from aiohttp_socks import ProxyConnector
from loguru import logger

from ptsandbox import config
from ptsandbox.models import (
    SandboxUIFilesResponse,
    SandboxUILogsRequest,
    SandboxUIScansResponse,
    SandboxUITasksRequest,
    SandboxUITasksResponse,
    SandboxUITaskSummaryResponse,
    SandboxUITreeDownloadRequest,
    SandboxUITreeRequest,
    SandboxUITreeResponse,
)
from ptsandbox.utils.async_http_client import AsyncHTTPClient


class SandboxUIApi:
    const_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",  # noqa
        "Content-Type": "application/json",
    }

    name: str
    host: str
    login: str
    password: str
    auth_type: int

    update_token_lock: asyncio.Lock
    last_updated_token: datetime.datetime | None

    session: aiohttp.ClientSession
    default_timeout: aiohttp.ClientTimeout

    def __init__(
        self,
        name: str,
        host: str,
        login: str,
        password: str,
        default_timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(
            total=None,
            connect=None,
            sock_read=120.0,
            sock_connect=40.0,
        ),
        auth_type: int = 0,
        proxy: str | None = None,
    ) -> None:
        self.name = name
        self.host = host
        self.login = login
        self.password = password
        self.auth_type = auth_type

        self.last_updated_token = None
        self.fingerprint = "".join(random.choice("0123456789abcdef") for _ in range(32))
        self.update_token_lock = asyncio.Lock()

        self.api_base_url = f"https://{self.host}/api/ui"
        self.default_timeout = default_timeout

        self.session = aiohttp.ClientSession(
            timeout=self.default_timeout,
            headers=self.const_headers,
            cookie_jar=aiohttp.CookieJar(unsafe=True),
            connector=ProxyConnector.from_url(proxy, ssl=False) if proxy else aiohttp.TCPConnector(ssl=False),
        )
        self.http_client = AsyncHTTPClient(self.session, logger=logger)

    async def do_ldap_auth(self) -> None:
        self.auth_type = 1
        await self.do_auth()

    async def do_auth(self) -> None:
        parameters = {"fingerprint": self.fingerprint}

        url_auth = f"{self.api_base_url}/auth/authorize"
        response = await self.http_client.get(url_auth, params=parameters)
        logger.trace(f"asked {url_auth} for auth, got {response.status}, {await response.text()}")

        url = (await response.json())["data"]["location"]
        location_ip = url.split("https://")[1].split(":3334")[0]
        logger.trace(f"redirecting to {location_ip} for auth")

        data: dict[str, str | bool | int] = {
            "username": self.login,
            "password": self.password,
            "authType": self.auth_type,
            "rememberLogin": True,
        }

        response = await self.http_client.post(f"https://{location_ip}:3334/ui/login", json=data)
        if response.status != HTTPStatus.OK:
            await self.end_session()
            response.raise_for_status()

        logger.trace(f"asked for login, {response.status}, {await response.text()} - {response.cookies}")

        response = await self.http_client.get(url)
        await self.update_token()

    async def __update_token(self) -> None:
        url_token = f"{self.api_base_url}/auth/token"
        response = await self.http_client.post(url_token, json={"fingerprint": self.fingerprint})
        logger.trace(f"asked {url_token} for token, got {response.status}, {await response.text()}")
        token = await response.json()
        try:
            self.session.headers["Authorization"] = "Bearer " + token["data"]["accessToken"]
        except Exception:
            try:
                self.session.headers["Authorization"] = "Bearer " + token["accessToken"]
            except Exception:
                pass

        self.last_updated_token = datetime.datetime.now()

    async def update_token(self, force_update: bool = False) -> None:
        async with self.update_token_lock:
            if (
                force_update
                or not self.last_updated_token
                or datetime.datetime.now() > self.last_updated_token + config.settings.UI_TOKEN_LIFETIME
            ):
                return await self.__update_token()

    async def end_session(self) -> None:
        if not self.session.closed:
            await self.session.close()

    async def get_tasks(self, params: SandboxUITasksRequest) -> SandboxUITasksResponse:
        """Листинг заданий"""
        await self.update_token()

        prepared_params = params.dict()
        response = await self.http_client.get(f"{self.api_base_url}/v2/tasks", params=prepared_params)

        response.raise_for_status()

        return await SandboxUITasksResponse.build_with_debug(
            response, "ui_v2_get_tasks", prepared_params=prepared_params, content_type=None
        )

    async def get_summary(self, scan_id: UUID) -> SandboxUITaskSummaryResponse:
        """Получить информацию о конректном задании"""

        await self.update_token()

        response = await self.http_client.get(f"{self.api_base_url}/v2/tasks/{scan_id}/summary")
        # TODO: probably need make normal handling with update_token etc
        if response.status == HTTPStatus.UNAUTHORIZED:
            await self.update_token(force_update=True)
            response = await self.session.get(f"{self.api_base_url}/v2/tasks/{scan_id}/summary")
        response.raise_for_status()

        return await SandboxUITaskSummaryResponse.build_with_debug(response, "ui_v2_get_summary", scan_id=scan_id)

    async def get_tree(self, event_uuid: UUID, params: SandboxUITreeRequest) -> SandboxUITreeResponse:
        await self.update_token()

        prepared_params = params.dict(by_alias=True)
        response = await self.http_client.get(f"{self.api_base_url}/v2/tasks/{event_uuid}/tree", params=prepared_params)
        response.raise_for_status()

        return await SandboxUITreeResponse.build_with_debug(response, "ui_v2_get_tree", event_uuid=event_uuid)

    async def get_artifacts_scans(self, scan_id: UUID, node_id: int) -> SandboxUIScansResponse:
        """Получение результатов сканирования конкретного артефакта"""

        await self.update_token()
        response = await self.http_client.get(f"{self.api_base_url}/v2/tasks/{scan_id}/artifacts/{node_id}/scans")
        response.raise_for_status()

        return await SandboxUIScansResponse.build_with_debug(
            response,
            "ui_get_scans",
            scan_id=scan_id,
            id=id,
            content_type=None,
        )

    async def download_logs(self, events: SandboxUILogsRequest) -> SandboxUIFilesResponse | None:
        """Скачать логи поведенческого анализа"""

        await self.update_token()

        response = await self.http_client.post(
            f"{self.api_base_url}/sandbox/logs", headers={"Content-Type": "application/json"}, data=events.json()
        )
        response.raise_for_status()  # todo: make normal exception handling

        ret = SandboxUIFilesResponse(
            files=[],
            archive=await response.read(),
        )
        try:
            with zipfile.ZipFile(BytesIO(ret.archive)) as zip:
                for name in zip.namelist():
                    ret.files.append(SandboxUIFilesResponse.File(name=name, file=zip.read(name)))
            return ret
        except Exception as e:
            logger.warning(e)
            return None

    async def download_artifacts(self, scan_id: UUID, params: SandboxUITreeDownloadRequest) -> BytesIO:
        """
        Скачать все артефакты задания

        Песок возвращает зашифрованный zip архив (пароль - infected), поэтому просто экспортируем набор байт.
        В случае необходимости можно использовать pyzipper для распаковки
        """

        await self.update_token()

        prepared_params = params.dict(by_alias=True)
        response = await self.http_client.get(
            f"{self.api_base_url}/v2/tasks/{scan_id}/tree/download", params=prepared_params
        )
        response.raise_for_status()

        return BytesIO(await response.read())

    def __del__(self) -> None:
        if not self.session.closed:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            if loop.is_running():
                loop.create_task(self.end_session())
            else:
                loop.run_until_complete(self.end_session())
