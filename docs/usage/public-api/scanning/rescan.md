In the sandbox, it is possible to re-scan the collected logs without using the sample used (retro tasks). In the interface, they are indicated as the results of the analysis.

The following files are required for rescan:

- `drakvuf-trace.log.zst` - events collected from the analysis system;
- `tcpdump.pcap` - information about network interaction;

```py title="Code example" hl_lines="16-19"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.create_rescan(
        trace=Path("./drakvuf-trace.log.zst"),
        network=Path("./tcpdump.pcap"),
    )

    result = await sandbox.wait_for_report(task)
    if (report := result.get_long_report()) is not None:
        print(report.artifacts)


asyncio.run(main())
```

!!! tip "Getting a report without additional waiting"

    If you need to send and receive the scan result immediately, you can set the `async_result=False` parameter and the sandbox will immediately send the finished result.

    ```py hl_lines="4"
    task = await sandbox.create_rescan(
        trace=Path("./drakvuf-trace.log.zst"),
        network=Path("./tcpdump.pcap"),
        async_result=False
    )
    print(task.get_long_report())
    ```

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
        except* aiohttp.client_exceptions.ClientResponseError as e:
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
    ```
