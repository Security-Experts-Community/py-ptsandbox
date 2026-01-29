import asyncio
import math
from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, TypeAlias
from uuid import UUID

import aiohttp
import aiohttp.client_exceptions
from aiohttp import ClientTimeout
from loguru import logger

from ptsandbox import config
from ptsandbox.models import (
    CheckHealthResponse,
    GetVersionResponse,
    SandboxAdvancedScanTaskRequest,
    SandboxBaseScanTaskRequest,
    SandboxBaseTaskResponse,
    SandboxCheckTaskRequest,
    SandboxCheckTaskResponse,
    SandboxException,
    SandboxImageInfo,
    SandboxKey,
    SandboxOptionsAdvanced,
    SandboxRescanTaskRequest,
    SandboxScanTaskRequest,
    SandboxScanURLTaskRequest,
    SandboxTooManyErrorsException,
    SandboxUploadException,
    SandboxWaitTimeoutException,
)
from ptsandbox.models.api.analysis import SandboxTasksResponse
from ptsandbox.models.api.scan import (
    SandboxScanWithSourceFileRequest,
    SandboxScanWithSourceURLRequest,
)
from ptsandbox.sandbox.sandbox_api import SandboxApi
from ptsandbox.sandbox.sandbox_ui import SandboxUI


class Sandbox:
    """
    The main class describing interaction with the sandbox via the API
    """

    api: SandboxApi
    ui: SandboxUI

    def __init__(
        self,
        key: SandboxKey,
        *,
        default_timeout: ClientTimeout = ClientTimeout(
            total=None,
            connect=None,
            sock_read=120.0,
            sock_connect=40.0,
        ),
        upload_semaphore_size: int | None = None,
        proxy: str | None = None,
    ) -> None:
        self.api = SandboxApi(
            key,
            default_timeout=default_timeout,
            upload_semaphore_size=upload_semaphore_size,
            proxy=proxy,
        )

        if key.ui is not None:
            self.ui = SandboxUI(key, default_timeout=default_timeout, proxy=proxy)

    async def create_rescan(
        self,
        trace: str | Path | bytes | BytesIO,
        network: str | Path | bytes | BytesIO,
        /,
        *,
        rules: str | Path | bytes | BytesIO | None = None,
        priority: int = 3,
        short_result: bool = False,
        async_result: bool = True,
        read_timeout: int = 300,
        options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options(),
    ) -> SandboxBaseTaskResponse:
        """
        Run a retro scan to check for detects without running a behavioral analysis.

        It is useful if there is a trace from a malware that can't connect to C2C.

        Or is it necessary to check the new correlation rules on the same trace.

        Args:
            trace: path to drakvuf-trace.log.zst or just bytes
            network: path to tcpdump.pcap or just bytes
            rules: if you have compiled the rules, then you can rescan with them, rather than using the sandbox embedded inside
            priority: the priority of the task, between 1 and 4. The higher it is, the faster it will get to work
            short_result:
                Return only the overall result of the check.

                The parameter value is ignored (true is used) if the value of the `async_result` parameter is also `true`.
            async_result:
                Return only the scan_id.

                Enabling this option may be usefull to send async requests for file checking.

                You can receive full report in a separate request.
            read_timeout: response waiting time in seconds
            options: additional sandbox options

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            SandboxUploadException: if an error occurred when uploading files to the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        try:
            async with asyncio.TaskGroup() as tg:
                task_dummy = tg.create_task(self.api.upload_file(file=config.FAKE_PDF))
                task_trace = tg.create_task(self.api.upload_file(file=trace))
                task_network = tg.create_task(self.api.upload_file(file=network))

                if rules is not None:
                    task_rules = tg.create_task(self.api.upload_file(file=rules))
                else:
                    task_rules = None
        except ExceptionGroup as e:
            raise SandboxUploadException("Can't upload files to server") from e

        uploaded_dummy = task_dummy.result()
        uploaded_trace = task_trace.result()
        uploaded_network = task_network.result()

        if task_rules is not None:
            uploaded_rules = task_rules.result()
            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxRescanTaskRequest(
            file_uri=uploaded_dummy.data.file_uri,
            file_name=config.FAKE_NAME,
            raw_events_uri=uploaded_trace.data.file_uri,
            raw_network_uri=uploaded_network.data.file_uri,
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            options=options,
        )

        return await self.api.create_rescan(scan, read_timeout)

    async def create_scan(
        self,
        file: str | Path | bytes | BinaryIO,
        /,
        *,
        file_name: str | None = None,
        rules: str | Path | bytes | BytesIO | None = None,
        priority: int = 3,
        short_result: bool = False,
        async_result: bool = True,
        read_timeout: int = 300,
        upload_timeout: float = 300,
        options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options(),
    ) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis

        Args:
            file: the file to be sent for analysis
            file_name:
                The name of the file to be checked, which will be displayed in the sandbox web interface.

                If possible, the name of the uploaded file will be taken as the default value.

                If not specified, the hash value of the file is calculated using the SHA—256 algorithm.
            rules: if you have compiled the rules, then you can scan with them, rather than using the sandbox embedded inside
            priority: the priority of the task, between 1 and 4. The higher it is, the faster it will get to work
            short_result:
                Return only the overall result of the check.

                The parameter value is ignored (true is used) if the value of the `async_result` parameter is also `true`.
            async_result:
                Return only the scan_id.

                Enabling this option may be usefull to send async requests for file checking.

                You can receive full report in a separate request.
            read_timeout: response waiting time in seconds
            upload_timeout: if a large enough file is being uploaded, increase timeout (in seconds).
            options: additional sandbox options

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            SandboxUploadException: if an error occurred when uploading files to the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        upload_name: str | None = file_name
        if not upload_name:
            match file:
                case str() | Path():
                    upload_name = str(file)
                case _:
                    upload_name = None

        try:
            async with asyncio.TaskGroup() as tg:
                task_file = tg.create_task(self.api.upload_file(file=file, upload_timeout=upload_timeout))
                if rules is not None:
                    task_rules = tg.create_task(self.api.upload_file(file=rules, upload_timeout=upload_timeout))
                else:
                    task_rules = None
        except ExceptionGroup as e:
            raise SandboxUploadException("Can't upload files to server") from e

        uploaded_file = task_file.result()

        if task_rules is not None:
            uploaded_rules = task_rules.result()
            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxScanTaskRequest(
            file_uri=uploaded_file.data.file_uri,
            file_name=upload_name,
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            options=options,
        )

        return await self.api.create_scan(scan, read_timeout)

    FileName: TypeAlias = str

    async def create_advanced_scan(
        self,
        file: str | Path | bytes | BinaryIO,
        /,
        *,
        file_name: str | None = None,
        rules: str | Path | bytes | BytesIO | None = None,
        extra_files: list[Path] | list[tuple[BinaryIO, FileName]] | None = None,
        short_result: bool = False,
        async_result: bool = True,
        read_timeout: int = 300,
        upload_timeout: float = 300,
        priority: int = 3,
        sandbox: SandboxOptionsAdvanced = SandboxOptionsAdvanced(),
    ) -> SandboxBaseTaskResponse:
        """
        Send the specified file to the sandbox for analysis using advanced API

        :warning: It may not be available in older versions of the sandbox.

        Args:
            file: the file to be sent for analysis
            file_name:
                The name of the file to be checked, which will be displayed in the sandbox web interface.

                If possible, the name of the uploaded file will be taken as the default value.

                If not specified, the hash value of the file is calculated using the SHA—256 algorithm.
            rules: if you have compiled the rules, then you can scan with them, rather than using the sandbox embedded inside
            priority: the priority of the task, between 1 and 4. The higher it is, the faster it will get to work
            short_result:
                Return only the overall result of the check.

                The parameter value is ignored (true is used) if the value of the `async_result` parameter is also `true`.
            async_result:
                Return only the scan_id.

                Enabling this option may be usefull to send async requests for file checking.

                You can receive full report in a separate request.
            read_timeout: response waiting time in seconds
            upload_timeout: if a large enough file is being uploaded, increase timeout (in seconds).
            sandbox: additional sandbox options

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            SandboxUploadException: if an error occurred when uploading files to the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        upload_name: str | None = file_name
        if not upload_name:
            match file:
                case str() | Path():
                    upload_name = str(file)
                case _:
                    upload_name = None

        try:
            async with asyncio.TaskGroup() as tg:
                task_file = tg.create_task(self.api.upload_file(file=file, upload_timeout=upload_timeout))
                if rules is not None:
                    task_rules = tg.create_task(self.api.upload_file(file=rules, upload_timeout=upload_timeout))
                else:
                    task_rules = None

                if extra_files is not None:
                    def _get_filename(item: Path | tuple[BinaryIO, str]):
                        if isinstance(item, tuple):
                            return item[1]
                        return str(item)

                    tasks_extra_files = {_get_filename(file): tg.create_task(self.api.upload_file(file[0] if isinstance(file, tuple) else file)) for file in extra_files}
                else:
                    tasks_extra_files = None
        except ExceptionGroup as e:
            raise SandboxUploadException("Can't upload files to server") from e

        uploaded_file = task_file.result()

        if tasks_extra_files is not None:
            for name, task in tasks_extra_files.items():
                uri = task.result().data.file_uri
                sandbox.extra_files.append(SandboxOptionsAdvanced.ExtraFile(name=name, uri=uri))

        if task_rules is not None:
            uploaded_rules = task_rules.result()
            sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxAdvancedScanTaskRequest(
            file_uri=uploaded_file.data.file_uri,
            file_name=upload_name,
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            sandbox=sandbox,
        )

        return await self.api.create_advanced_scan(scan, read_timeout)

    async def create_url_scan(
        self,
        url: str,
        /,
        *,
        rules: str | Path | bytes | BytesIO | None = None,
        priority: int = 3,
        short_result: bool = False,
        async_result: bool = True,
        read_timeout: int = 300,
        options: SandboxBaseScanTaskRequest.Options = SandboxBaseScanTaskRequest.Options(),
    ) -> SandboxBaseTaskResponse:
        """
        Send the url to the sandbox

        Args:
            url: the url to be sent for analysis
            rules: if you have compiled the rules, then you can scan with them, rather than using the sandbox embedded inside
            priority: the priority of the task, between 1 and 4. The higher it is, the faster it will get to work
            short_result:
                Return only the overall result of the check.

                The parameter value is ignored (true is used) if the value of the `async_result` parameter is also `true`.
            async_result:
                Return only the scan_id.

                Enabling this option may be usefull to send async requests for file checking.

                You can receive full report in a separate request.
            read_timeout: response waiting time in seconds
            options: additional sandbox options

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            SandboxUploadException: if an error occurred when uploading files to the server
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        if rules is not None:
            try:
                uploaded_rules = await self.api.upload_file(file=rules)
            except aiohttp.client_exceptions.ClientResponseError as e:
                raise SandboxUploadException("Can't upload rules to server") from e

            options.sandbox.debug_options["rules_url"] = uploaded_rules.data.file_uri

        scan = SandboxScanURLTaskRequest(
            url=url,
            file_name=None,  # will be excluded
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            options=options,
        )

        return await self.api.creat_url_scan(scan, read_timeout)

    async def wait_for_report(
        self,
        base_report: SandboxBaseTaskResponse,
        wait_time: float = 120,
        *,
        error_limit: int = 3,
        scan_with_source: bool = False,
    ) -> SandboxBaseTaskResponse:
        """
        Waiting for a full response from the sandbox if the request was with the `async_result=True` flag

        Args:
            base_time:
                how many seconds should I wait?

                Example of a formula for calculating a parameter:

                ```python
                wait_time = options.sandbox.analysis_duration * 4 + (
                    300 if sandbox_options.sandbox.analysis_duration < 80 else 120
                )
                ```

        Returns:
            The response from the sandbox with full information.

        Raises:
            SandboxException: there is nothing to wait, because there is not even a short report
            SandboxTooManyErrorsException: if there are too many errors while waiting for the report
            SandboxWaitTimeoutException: if the time is exceeded, the specified waiting time is
        """

        short_report = base_report.get_short_report()
        if not short_report:
            raise SandboxException("There is nothing to wait, because there is not even a short report")

        # if already have long report, just return it
        if base_report.get_long_report() is not None:
            return base_report

        elapsed_time: float = 0

        # calculate the sleep time, because for tasks with a long waiting time,
        # it makes no sense to poll the sandbox frequently
        sleep_time = math.ceil(wait_time / 64)

        error_counter = 0
        while elapsed_time <= wait_time:
            try:
                if scan_with_source:
                    check = await self.api.source_get_report(short_report.scan_id)
                else:
                    check = await self.get_report(short_report.scan_id)
            except Exception as ex:
                error_counter += 1

                logger.warning(f"Maybe dead sandbox {ex!r}, {self=}, {short_report.scan_id=}")

                if error_counter >= error_limit:
                    raise SandboxTooManyErrorsException("Too many errors while waiting report") from ex

                continue

            # full report is available?
            if check.get_long_report():
                return check

            await asyncio.sleep(sleep_time)

            elapsed_time += sleep_time

        raise SandboxWaitTimeoutException("Waiting time exceeded")

    async def check_task(self, task_id: str | UUID, allow_preflight: bool = True) -> SandboxCheckTaskResponse:
        """
        Checking the result of a scan running with the async_result flag

        Args:
            task_id: task id :)
            allow_preflight:
                If this flag is set, an intermediate result with the `is_preflight` attribute
                will be returned for scanning with multiple stages (for example, static + BA).

        Returns:
            Information about the analysis status

        Raises:
            SandboxException: if the passed task_id is not in UUID format
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        try:
            scan_id = UUID(task_id) if isinstance(task_id, str) else task_id
        except ValueError as e:
            raise SandboxException(f"Incorrect value={task_id} for task_id, expected UUID") from e

        return await self.api.check_task(
            SandboxCheckTaskRequest(
                scan_id=scan_id,
                allow_preflight=allow_preflight,
            )
        )

    async def get_report(self, task_id: str | UUID) -> SandboxBaseTaskResponse:
        """
        Getting the full task scan report

        The check was completed successfully. The results are in the message body. If the scan result is not ready yet, the result and artifacts keys are missing.

        :warning: The results will be returned only for the key that the analysis was started with. Sandbox restrictions for now.

        Args:
            task_id: task id :)

        Returns:
            The response from the sandbox is either with partial information (when using async_result), or with full information.

        Raises:
            SandboxException: if the passed task_id is not in UUID format
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        try:
            scan_id = UUID(task_id) if isinstance(task_id, str) else task_id
        except ValueError as e:
            raise SandboxException(f"Incorrect value={task_id} for task_id, expected UUID") from e

        return await self.api.get_report(scan_id=scan_id)

    def _get_hash_type(self, hash: str) -> str:
        """
        The simplest algorithm for determining the hash type
        """

        match len(hash):
            case 64:
                return "sha256"
            case _:
                raise SandboxException(f"Unknown hash type: {hash}")

    async def get_file(self, hash: str, read_timeout: int = 120) -> bytes:
        """
        Download file from the sandbox by hash

        Args:
            hash: sha256 hash of the file
            stream: download the entire file or give the result in chunks

        Returns:
            file data or throw exception SandboxFileNotFoundException

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        file_uri = f"{self._get_hash_type(hash)}:{hash}"
        return await self.api.download_artifact(file_uri=file_uri, read_timeout=read_timeout)

    async def get_file_stream(self, hash: str, read_timeout: int = 120) -> AsyncIterator[bytes]:
        """
        Download file from the sandbox by hash

        Args:
            hash: sha256 hash of the file
            stream: download the entire file or give the result in chunks

        Returns:
            file data or throw exception SandboxFileNotFoundException

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        file_uri = f"{self._get_hash_type(hash)}:{hash}"

        async for chunk in self.api.download_artifact_stream(file_uri=file_uri, read_timeout=read_timeout):
            yield chunk

    async def get_images(self) -> list[SandboxImageInfo]:
        """
        Get a list of available images in the sandbox

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        data = await self.api.get_images()
        return data.data

    async def get_email_headers(self, file: str | Path | bytes | BinaryIO) -> AsyncIterator[bytes]:
        """
        Upload an email to receive headers

        Args:
            file: path to .eml file or just binary data

        Returns:
            The header file

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        match file:
            case str() | Path():
                with open(file, "rb") as fd:
                    data = BytesIO(fd.read())
                iterator = self.api.get_email_headers(data)
            case bytes():
                iterator = self.api.get_email_headers(BytesIO(file))
            case BinaryIO():
                iterator = self.api.get_email_headers(file)
            case _:
                raise SandboxException(f"Unsupported type: {type(file)}")

        async for chunk in iterator:
            yield chunk

    async def check_health(self) -> CheckHealthResponse:
        """
        Checking the API status

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        return await self.api.check_health()

    async def get_version(self) -> GetVersionResponse:
        """
        Get information about product

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        return await self.api.get_version()

    async def source_check_file(
        self,
        file: str | Path | bytes | BinaryIO,
        /,
        *,
        file_name: str | None = None,
        short_result: bool = True,
        async_result: bool = False,
        priority: int = 3,
        passwords_for_unpack: list[str] | None = None,
        product: str | None = None,
        metadata: dict[str, str] | None = None,
        read_timeout: int = 240,
    ) -> SandboxBaseTaskResponse:
        """
        Your application can run a file check with predefined parameters
        and in response receive the results of the check and/or the ID of the task.

        Args:
            file:
                The file to be sent for analysis
            file_name:
                The name of the file to be checked, which will be displayed in the sandbox web interface.

                If possible, the name of the uploaded file will be taken as the default value.

                If not specified, the hash value of the file is calculated using the SHA—256 algorithm.
            short_result:
                Return only the overall result of the check.

                Attention. When using a query with the full result (short_result=false), the response waiting time can be increased by 2 seconds.

                For example, scanning a file without BA takes an average of hundreds of milliseconds,
                and you will have to wait seconds to get the full result, which is much longer.
            async_result:
                Return only the scan_id without waiting for the scan to finish.

                The "result" key is missing in the response.
            priority:
                The priority of the task is from 1 to 4. The higher it is, the faster it will get to work.
            passwords_for_unpack:
                A list of passwords for unpacking encrypted archives
            product:
                The source ID string is "EDR" or "CS" ("PT_EDR" or "PT_CS").

                You only need to fill it out during integration
            metadata:
                Source metadata for special scanning

                ```python
                {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                }
                ```
            read_timeout:
                Response waiting time in seconds

        Raises:
            ValueError: if passed values incorrect
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        if priority < 1 or priority > 4:
            raise ValueError(f"Incorrect value for priority: {priority}")

        upload_name = file_name
        if not upload_name:
            match file:
                case str() | Path():
                    upload_name = str(file)
                case _:
                    upload_name = None

        data = SandboxScanWithSourceFileRequest(
            file_name=upload_name,
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            passwords_for_unpack=passwords_for_unpack,
            product=product,
            metadata=metadata,
        )

        return await self.api.source_check_file(file, data, read_timeout)

    async def source_check_url(
        self,
        url: str,
        /,
        *,
        short_result: bool = True,
        async_result: bool = False,
        priority: int = 3,
        passwords_for_unpack: list[str] | None = None,
        product: str | None = None,
        metadata: dict[str, str] | None = None,
        read_timeout: int = 240,
    ) -> SandboxBaseTaskResponse:
        """
        Your application can run a URL scan and receive the scan results and/or the ID of the task.

        Args:
            url:
                The file to be sent for analysis
            short_result:
                Return only the overall result of the check.

                Attention. When using a query with the full result (short_result=false), the response waiting time can be increased by 2 seconds.

                For example, scanning a file without BA takes an average of hundreds of milliseconds,
                and you will have to wait seconds to get the full result, which is much longer.
            async_result:
                Return only the scan_id without waiting for the scan to finish.

                The "result" key is missing in the response.
            priority:
                The priority of the task is from 1 to 4. The higher it is, the faster it will get to work.
            passwords_for_unpack:
                A list of passwords for unpacking encrypted archives
            product:
                The source ID string is "EDR" or "CS" ("PT_EDR" or "PT_CS").

                You only need to fill it out during integration
            metadata:
                Source metadata for special scanning

                ```python
                {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                }
                ```
            read_timeout:
                Response waiting time in seconds

        Raises:
            ValueError: if passed values incorrect
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        if priority < 1 or priority > 4:
            raise ValueError(f"Incorrect value for priority: {priority}")

        data = SandboxScanWithSourceURLRequest(
            url=url,
            short_result=short_result,
            async_result=async_result,
            priority=priority,
            passwords_for_unpack=passwords_for_unpack,
            product=product,
            metadata=metadata,
        )

        return await self.api.source_check_url(data, read_timeout)

    async def get_tasks(
        self,
        query: str = "",
        limit: int = 20,
        offset: int = 0,
        utc_offset_seconds: int = 0,
        next_cursor: str | None = None,
    ) -> SandboxTasksResponse:
        """
        Get tasks listing

        Warning: Unstable API (can be changed in future release)

        Args:
            query:
                filtering using the query language. For the syntax, see the user documentation.

                ```
                age < 30d AND (task.correlated.state != UNKNOWN ) ORDER BY start desc
                ```
            limit: limit on the number of records to be returned
            utc_offset_seconds: the offset of the user's time from UTC, which will be used for the time in QL queries
            next_cursor: the value from the previous request

        Returns:
            Information about requested tasks

        Raises:
            aiohttp.client_exceptions.ClientResponseError: if the response from the server is not ok
        """

        data: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "utc_offset_seconds": utc_offset_seconds,
        }

        if next_cursor is not None:
            data.update({"next_cursor": next_cursor})

        return await self.api.get_tasks(data)
