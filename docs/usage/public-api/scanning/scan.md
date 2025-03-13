## Default scan

Regular scanning allows you to send files to the sandbox without super fine-tuning the settings.

```py title="Code example" hl_lines="17-25"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import SandboxBaseScanTaskRequest, SandboxOptions


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.create_scan(
        Path("./example.py"),
        options=SandboxBaseScanTaskRequest.Options(
            sandbox=SandboxOptions(
                image_id="ubuntu-jammy-x64",
                analysis_duration=30,
            )
        ),
    )

    result = await sandbox.wait_for_report(task)
    if (report := result.get_long_report()) is not None:
        print(report.result.verdict)


asyncio.run(main())
```

!!! example "Usecase"

    This is useful when you just need to send a file for analysis with a minimum number of options.

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
                case str() | PathLike():
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
        except* aiohttp.client_exceptions.ClientResponseError as e:
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
    ```

### Options

A set of options that additionally allow you to configure the analysis parameters

In them, you can set the scan image, your command to run, etc.

You can read more details in the model code.

??? quote "Source code in `ptsandbox/models/api/analysis.py`"

    ```py
    class SandboxOptions(BaseRequest):
        """
        Parameters of behavioral analysis.

        In the absence, the source parameters are used for analysis, which are set in the system by default.
        """

        class FilterProperties(BaseModel):
            """
            Filtering a group of files by properties to send to the sandbox for analysis
            """

            pdf: list[FileInfoProperties] = []

            office: list[FileInfoProperties] = []

        enabled: bool = True
        """
        Perform a behavioral analysis
        """

        image_id: str = "win7-sp1-x64"
        """
        ID of the VM image.

        You can view it in the sandbox interface.
        """

        custom_command: str | None = None
        """
        The command to run the file.

        The `{file}` marker in the string is replaced with the path to the file.

        For example: `rundll32.exe {file},#1`
        """

        procdump_new_processes_on_finish: bool = False
        """
        Take dumps for all spawned and non-dead processes
        """

        analysis_duration: int = Field(default=120, ge=10)
        """
        The duration of analysis the file in seconds. minimum: 10
        """

        bootkitmon: bool = False
        """
        Perform bootkitmon analysis
        """

        analysis_duration_bootkitmon: int = Field(default=60, ge=10)
        """
        The duration of analysis at the bootkitmon stage in seconds. minimum: 10
        """

        save_video: bool = True
        """
        Save video capture of the screen
        """

        mitm_enabled: bool = True
        """
        Enable certificates injection with PT Sandbox certificates when decrypting and analyzing secure traffic
        """

        file_types: list[str] | None = None
        """
        A list of the final file types or groups of files that will be sent for behavioral analysis

        For example:
        ["adobe-acrobat/", "databases/", "executable-files/", "presentations/", "spreadsheets/", "word-processor/"]
        """

        filter_by_properties: FilterProperties | None = None
        """
        Filtering a group of files by properties to send to the sandbox for analysis
        """

        debug_options: DebugOptions = {"save_debug_files": False}
        """
        Fine-tuning
        """
    ```

## URL

In addition to checking files, it is possible to check URLs.

It is mainly used to download a file from a link and send it to the sandbox for further analysis.

```py title="Code example" hl_lines="16-24"
import asyncio

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import SandboxOptions, SandboxScanURLTaskRequest


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.create_url_scan(
        "http://malware.com/malicious-file",
        options=SandboxScanURLTaskRequest.Options(
            sandbox=SandboxOptions(
                image_id="ubuntu-jammy-x64",
                analysis_duration=30,
            )
        ),
    )

    result = await sandbox.wait_for_report(task)
    if (report := result.get_long_report()) is not None:
        print(report.result.verdict)


asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
    ```

## Advanced scan

For example, we need to fine-tune the sample launch parameters, put additional files in the sandbox, etc.

This can be done with advanced scanning options.

```py title="Code example" hl_lines="17-25"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import SandboxOptionsAdvanced


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.create_advanced_scan(
        Path("./example.elf"),
        extra_files=[Path("./file.txt"), Path("./file.sh")], # (1)!
        sandbox=SandboxOptionsAdvanced( # (2)!
            image_id="ubuntu-jammy-x64",
            analysis_duration=30,
            disable_clicker=True,
        ),
    )

    result = await sandbox.wait_for_report(task)
    if (report := result.get_long_report()) is not None:
        print(report.result.verdict)


asyncio.run(main())
```

1. The library does not check the existence of files
2. We specify `SandboxOptionsAdvanced` instead of `SandboxOptions`

!!! tip "Tip - enable manual analysis"

    ```py hl_lines="6-7"
    task = await sandbox.create_advanced_scan(
        Path("./example.exe"),
        sandbox=SandboxOptionsAdvanced(
            image_id="win11-23H2-x64",
            analysis_duration=600,
            disable_clicker=True,
            vnc_mode=VNCMode.FULL,
        )
    )
    ```

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
    async def create_advanced_scan(
        self,
        file: str | Path | bytes | BinaryIO,
        /,
        *,
        file_name: str | None = None,
        rules: str | Path | bytes | BytesIO | None = None,
        extra_files: list[Path] | None = None,
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
                case str() | PathLike():
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
                    tasks_extra_files = {str(file): tg.create_task(self.api.upload_file(file)) for file in extra_files}
                else:
                    tasks_extra_files = None
        except* aiohttp.client_exceptions.ClientResponseError as e:
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
    ```

### Options

A set of options that additionally allow you to configure the analysis parameters

In them, you can set the scan image, your command to run, etc.

You can read more details in the model code.

??? quote "Source code in `ptsandbox/models/api/analysis.py`"

    ```py
    class SandboxOptionsAdvanced(BaseRequest):
        """
        Run an advanced analysis of the uploaded file in the VM without unpacking.

        Provides an opportunity to fine-tuning.

        **The options are in beta, so they may change in the future.**
        """

        class ExtraFile(BaseModel):
            """
            An additional file to be placed next to the sample
            """

            uri: str
            """
            Link to the uploaded object
            """

            name: str
            """
            Name in the VM
            """

        image_id: str = "win7-sp1-x64"
        """
        ID of the VM image.

        You can view it in the sandbox interface.
        """

        custom_command: str | None = None
        """
        The command to run the file.

        The `{file}` marker in the string is replaced with the path to the file.

        For example: `rundll32.exe {file},#1`
        """

        procdump_new_processes_on_finish: bool = False
        """
        Take dumps for all spawned and non-dead processes
        """

        analysis_duration: int = Field(default=120, ge=10)
        """
        The duration of analysis the file in seconds. minimum: 10
        """

        bootkitmon: bool = False
        """
        Perform bootkitmon analysis
        """

        analysis_duration_bootkitmon: int = Field(default=60, ge=10)
        """
        The duration of analysis at the bootkitmon stage in seconds. minimum: 10
        """

        save_video: bool = True
        """
        Save video capture of the screen
        """

        mitm_enabled: bool = True
        """
        Enable certificates injection with PT Sandbox certificates when decrypting and analyzing secure traffic
        """

        disable_clicker: bool = False
        """
        Disable auto-clicker startup

        Useful when enabling manual analysis.
        """

        skip_sample_run: bool = False
        """
        Disable sample launch
        """

        vnc_mode: VNCMode = VNCMode.DISABLED
        """
        Manual analysis mode
        """

        extra_files: list[ExtraFile] = []
        """
        A list of additional files that are placed in the VM
        """

        debug_options: DebugOptions = {"save_debug_files": False}
        """
        Fine-tuning
        """
    ```
