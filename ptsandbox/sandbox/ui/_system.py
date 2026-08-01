from collections.abc import AsyncIterator
from typing import Any

from ptsandbox.models import (
    SandboxAVDistributionPacksResponse,
    SandboxAVEngineSettingsResponse,
    SandboxAVEnginesResponse,
    SandboxClusterStatusResponse,
    SandboxComponentsResponse,
    SandboxLicenseResponse,
    SandboxLicenseUpdateResponse,
    SandboxSystemSettingsResponse,
    SandboxSystemStatusResponse,
    SandboxSystemVersionResponse,
    SandboxUpdateSystemSettingsRequest,
)
from ptsandbox.sandbox.base import BaseSandboxClient
from ptsandbox.sandbox.ui._token import token_required


class SystemMixin(BaseSandboxClient):
    @token_required
    async def get_system_status(self) -> SandboxSystemStatusResponse:
        """
        Get information about the system status

        For full information, look at the documentation of the `SandboxSystemStatusResponse` model.

        Returns:
            A model with information about the system

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/system/status",
            response_model=SandboxSystemStatusResponse,
        )

    @token_required
    async def get_system_settings(self) -> SandboxSystemSettingsResponse:
        """
        Get information about the system settings

        Returns:
            A model with system settings

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/system/settings",
            response_model=SandboxSystemSettingsResponse,
        )

    @token_required
    async def update_system_settings(self, settings: SandboxUpdateSystemSettingsRequest) -> None:
        """
        Update system settings

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        async with self.http_client.put(
            f"{self.key.ui_url}/system/settings",
            json=settings.dict(),
        ):
            pass

    @token_required
    async def get_system_version(self) -> SandboxSystemVersionResponse:
        """
        Get the version of the installed product

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/system/version",
            response_model=SandboxSystemVersionResponse,
        )

    @token_required
    async def get_system_logs(
        self,
        since: int | None = None,
        components: list[str] | None = None,
    ) -> AsyncIterator[bytes]:
        """
        Download the archive with system logs

        Args:
            since: the time period for uploading logs in seconds
            components: component names in the format `{namespace}/{component}`, `{namespace}/{component}`, ... If the field is empty, all components will be downloaded

        Returns:
            Archive with logs

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        if components is None:
            components = []

        data: dict[str, Any] = {"components": ",".join(components)}
        if since is not None:
            data["since"] = since

        async with self.http_client.get(
            f"{self.key.ui_url}/system/logs",
            params=data,
        ) as response:
            async for chunk in self._iter_chunks(response):
                yield chunk

    @token_required
    async def get_system_cluster_status(self) -> SandboxClusterStatusResponse:
        """
        Get information about the cluster status

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/system/status/cluster",
            response_model=SandboxClusterStatusResponse,
        )

    @token_required
    async def get_system_components_status(self) -> SandboxComponentsResponse:
        """
        Get information about the components status

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/v2/system/status/components",
            response_model=SandboxComponentsResponse,
        )

    @token_required
    async def get_license(self) -> SandboxLicenseResponse:
        """
        Get the license status and details

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/license",
            response_model=SandboxLicenseResponse,
        )

    @token_required
    async def update_license(self) -> SandboxLicenseUpdateResponse:
        """
        Updating the current license

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "PUT",
            f"{self.key.ui_url}/license",
            response_model=SandboxLicenseUpdateResponse,
        )

    @token_required
    async def get_av_engines(self) -> SandboxAVEnginesResponse:
        """
        Get information about antivirus scanners

        Returns:
            A model with information about all antiviruses

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/av-engines",
            response_model=SandboxAVEnginesResponse,
        )

    @token_required
    async def get_av_engine(self, item_id: str) -> SandboxAVEngineSettingsResponse:
        """
        Get settings of a specific antivirus engine.

        Args:
            item_id: antivirus identifier (engine code name, e.g. ``"clamav"``)

        Returns:
            A model with the antivirus settings

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/av-engines/{item_id}",
            response_model=SandboxAVEngineSettingsResponse,
        )

    @token_required
    async def get_av_distribution_packs(self) -> SandboxAVDistributionPacksResponse:
        """
        Get the list of antivirus distributions available for installation.

        Returns:
            A model with the distribution packs

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/av-distribution-packs",
            response_model=SandboxAVDistributionPacksResponse,
        )
