from typing import Any

from pydantic import Field, field_serializer

from ptsandbox.models.core import BaseRequest


class SandboxScanWithSource(BaseRequest):
    """
    Internal model for creating request
    """

    short_result: bool = True

    async_result: bool = False

    priority: int = Field(3, ge=1, le=4)

    passwords_for_unpack: list[str] | None = None

    product: str | None = Field(default=None, exclude=True)

    metadata: dict[str, str] | None = Field(default=None, exclude=True)

    def get_headers(self) -> dict[str, str | dict[str, Any]]:
        headers: dict[str, str | dict[str, Any]] = {}

        if self.product is not None:
            headers.update({"X-Source-Product": self.product})

        if self.metadata is not None:
            headers.update({"X-Source-Metadata": ",".join(f"{k},{v}" for k, v in self.metadata.items())})

        return headers


class SandboxScanWithSourceFileRequest(SandboxScanWithSource):
    """
    Internal model for creating request
    """

    file_name: str | None = None

    @field_serializer("short_result", "async_result")
    def serialize_boolean(self, v: bool) -> str:
        return str(v).lower()


class SandboxScanWithSourceURLRequest(SandboxScanWithSource):
    """
    Internal model for creating request
    """

    url: str | None = None
