import asyncio
import logging

import aiohttp

from ptsandbox.models import SandboxKey
from ptsandbox.sandbox.api._analysis import AnalysisMixin
from ptsandbox.sandbox.api._maintenance import MaintenanceMixin
from ptsandbox.sandbox.api._scan import ScanMixin
from ptsandbox.sandbox.api._storage import StorageMixin

logger = logging.getLogger(__name__)


class SandboxApi(
    StorageMixin,
    AnalysisMixin,
    ScanMixin,
    MaintenanceMixin,
):
    """
    Using raw queries to sandbox API
    """

    upload_semaphore: asyncio.Semaphore

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: aiohttp.ClientTimeout,
        upload_semaphore_size: int | None = None,
        proxy: str | None = None,
        connection_retries: int = 3,
    ) -> None:
        super().__init__(
            key,
            default_timeout=default_timeout,
            proxy=proxy,
            connection_retries=connection_retries,
            headers={"X-Api-Key": key.key.get_secret_value()},
        )

        self.upload_semaphore = asyncio.Semaphore(
            upload_semaphore_size if upload_semaphore_size else self.key.max_workers
        )
