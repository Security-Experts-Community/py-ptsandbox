import asyncio
import datetime
import logging
import secrets
from http import HTTPStatus
from urllib.parse import urlparse

import aiohttp

from ptsandbox.exceptions import SandboxException
from ptsandbox.models import SandboxKey
from ptsandbox.sandbox.ui._artifacts import ArtifactsMixin
from ptsandbox.sandbox.ui._entry_points import EntryPointsMixin
from ptsandbox.sandbox.ui._system import SystemMixin
from ptsandbox.sandbox.ui._tasks import TasksMixin
from ptsandbox.sandbox.ui._tokens import TokensMixin

logger = logging.getLogger(__name__)


class SandboxUI(
    SystemMixin,
    EntryPointsMixin,
    TasksMixin,
    ArtifactsMixin,
    TokensMixin,
):
    """
    Using raw queries to sandbox UI API
    """

    const_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Unique/96.7.6401.61",  # noqa
        "Content-Type": "application/json",
    }

    update_token_lock: asyncio.Lock
    last_updated_token: datetime.datetime | None

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: aiohttp.ClientTimeout,
        proxy: str | None = None,
        token_lifetime: datetime.timedelta = datetime.timedelta(minutes=8),
        connection_retries: int = 3,
    ) -> None:
        super().__init__(
            key,
            default_timeout=default_timeout,
            proxy=proxy,
            connection_retries=connection_retries,
            headers=self.const_headers,
            cookie_jar=aiohttp.CookieJar(unsafe=True),
        )

        self.token_lifetime = token_lifetime
        self.is_authorized = False
        self.last_updated_token = None
        self.fingerprint = secrets.token_hex(16)
        self.update_token_lock = asyncio.Lock()

    async def _ensure_token(self) -> None:
        if not self.is_authorized:
            raise SandboxException("Can't use the UI API without logging in first")

        async with self.update_token_lock:
            if not self.last_updated_token or (datetime.datetime.now() > self.last_updated_token + self.token_lifetime):
                await self._update_token()

    async def _update_token(self) -> None:
        response = await self.http_client.post(
            f"{self.key.ui_url}/auth/token",
            json={"fingerprint": self.fingerprint},
        )

        token = await response.json()

        try:
            self.session.headers["Authorization"] = "Bearer " + token["data"]["accessToken"]
        except (KeyError, TypeError) as e:
            raise SandboxException("Can't get accessToken from response") from e

        self.last_updated_token = datetime.datetime.now()

    async def authorize(self) -> None:
        """
        Authorization in the UI using the passed parameters in the key

        Raises:
            SandboxException: if the authorization location cannot be retrieved or login fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status during login
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        parameters = {"fingerprint": self.fingerprint}

        response = await self.http_client.get(f"{self.key.ui_url}/auth/authorize", params=parameters)
        try:
            location: str = (await response.json())["data"]["location"]
        except KeyError as e:
            raise SandboxException("Can't get location from authorization url") from e

        url = urlparse(location)

        assert self.key.ui is not None

        data: dict[str, str | bool | SandboxKey.UI.AuthType] = {
            "username": self.key.ui.login,
            "password": self.key.ui.password.get_secret_value(),
            "authType": self.key.ui.auth_type,
            "rememberLogin": True,
        }

        response = await self.http_client.post(f"{url.scheme}://{url.netloc}/ui/login", json=data)
        if response.status != HTTPStatus.OK:
            await self.close()
            response.raise_for_status()

        # get refresh token
        await self.http_client.get(location)

        self.is_authorized = True

        # get access token
        await self._update_token()
