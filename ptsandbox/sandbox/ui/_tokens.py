from ptsandbox.models import (
    SandboxCreateTokenResponse,
    SandboxTokensResponse,
    TokenPermissions,
)
from ptsandbox.sandbox.base import BaseSandboxClient
from ptsandbox.sandbox.ui._token import token_required


class TokensMixin(BaseSandboxClient):
    @token_required
    async def get_api_tokens(self) -> SandboxTokensResponse:
        """
        Get listing of current Public API tokens

        Returns:
            A model with information about all tokens

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "GET",
            f"{self.key.ui_url}/public-api/tokens",
            response_model=SandboxTokensResponse,
        )

    @token_required
    async def create_api_token(
        self,
        name: str,
        permissions: list[TokenPermissions],
        comment: str = "",
    ) -> SandboxCreateTokenResponse:
        """
        Create a new Public API token

        Args:
            name: token name
            permissions: permissions for the token
            comment: additional information about the token

        Returns:
            A model with information about the created token

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
            pydantic.ValidationError: if the response body does not match the expected model
        """

        return await self._request(
            "POST",
            f"{self.key.ui_url}/public-api/tokens",
            response_model=SandboxCreateTokenResponse,
            json={
                "name": name,
                "permissions": permissions,
                "comment": comment,
            },
        )

    @token_required
    async def delete_api_token(self, token_id: int) -> None:
        """
        Delete the Public API token

        Args:
            token_id: id of the PublicAPI token in the database

        Raises:
            SandboxException: if not authorized or token refresh fails
            aiohttp.client_exceptions.ClientResponseError: if the server returns an error status
            aiohttp.client_exceptions.ClientError: on connection or transport errors
        """

        response = await self._request(
            "DELETE",
            f"{self.key.ui_url}/public-api/tokens/{token_id}",
        )
        response.raise_for_status()
