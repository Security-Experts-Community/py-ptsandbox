from __future__ import annotations

import json

from pydantic import Field, field_serializer

from ptsandbox.models.core import BaseRequest


class SandboxScanWithSource(BaseRequest):
    """
    Internal model for creating request
    """

    short_result: bool = True

    async_result: bool = False

    priority: int = Field(default=3, ge=1, le=4)

    passwords_for_unpack: list[str] | None = None

    product: str | None = Field(default=None, exclude=True)

    metadata: dict[str, str] | None = Field(default=None, exclude=True)

    def get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}

        if self.product is not None:
            headers["X-Source-Product"] = self.product

        if self.metadata is not None:
            headers["X-Source-Metadata"] = ",".join(f"{k},{v}" for k, v in self.metadata.items())

        return headers


class SandboxScanWithSourceFileRequest(SandboxScanWithSource):
    """
    Internal model for creating request
    """

    file_name: str | None = None

    @field_serializer("short_result", "async_result")
    def serialize_boolean(self, v: bool) -> str:
        return str(v).lower()

    @field_serializer("passwords_for_unpack")
    def serialize_passwords(self, v: list[str] | None) -> str | None:
        # /scan/checkFile sends passwords_for_unpack as a query parameter
        # where the API expects a JSON-encoded string, e.g. '["pass1", "pass2"]'
        if v is None:
            return None
        return json.dumps(v)


class SandboxScanWithSourceURLRequest(SandboxScanWithSource):
    """
    Internal model for creating request
    """

    url: str | None = None
