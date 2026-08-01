from ptsandbox.models import (
    SandboxGetHealthStatusResponse,
    SandboxGetImagesResponse,
    SandboxGetVersionResponse,
)
from ptsandbox.sandbox.base import BaseSandboxClient


class MaintenanceMixin(BaseSandboxClient):
    async def get_images(self) -> SandboxGetImagesResponse:
        """
        Get a list of available images in the sandbox

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.url}/engines/sandbox/getImages",
            response_model=SandboxGetImagesResponse,
        )

    async def get_health_status(self) -> SandboxGetHealthStatusResponse:
        """
        Checking the API status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.url}/maintenance/checkHealth",
            response_model=SandboxGetHealthStatusResponse,
        )

    async def get_version(self) -> SandboxGetVersionResponse:
        """
        Get information about product

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.url}/maintenance/getVersion",
            response_model=SandboxGetVersionResponse,
        )
