The sandbox can re-scan collected logs without the original sample (retro tasks). In the web interface, these appear as analysis results.

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
        Path("./drakvuf-trace.log.zst"),
        Path("./tcpdump.pcap"),
    )

    result = await sandbox.wait_for_report(task)
    if (report := result.get_long_report()) is not None:
        print(report.artifacts)


asyncio.run(main())
```

!!! tip "Getting a report without additional waiting"

    To get the scan result immediately without waiting, set `async_result=False`. The sandbox returns the finished result in the same request.

    ```py hl_lines="4"
    task = await sandbox.create_rescan(
        Path("./drakvuf-trace.log.zst"),
        Path("./tcpdump.pcap"),
        async_result=False
    )
    print(task.get_long_report())
    ```

::: ptsandbox.sandbox.sandbox.Sandbox.create_rescan

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.create_rescan
