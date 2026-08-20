## Default scan

Regular scanning sends files to the sandbox without fine-tuning the settings.

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

    This is useful when you need to send a file for analysis with a minimum number of options.

::: ptsandbox.sandbox.sandbox.Sandbox.create_scan

### Low-level API

Under the hood, `Sandbox.create_scan` uploads the file via `upload_file` and then calls `create_scan` on the API. You can use these methods directly for more control:

```py title="Direct API usage"
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey
from ptsandbox.models import SandboxScanTaskRequest, SandboxOptions

sandbox = Sandbox(SandboxKey(...))

# Step 1: upload the file
uploaded = await sandbox.api.upload_file(Path("./example.py"))

# Step 2: create the scan task
scan = SandboxScanTaskRequest(
    file_uri=uploaded.data.file_uri,
    file_name="example.py",
    short_result=False,
    async_result=True,
    priority=3,
)
task = await sandbox.api.create_scan(scan)
```

::: ptsandbox.sandbox.api._storage.StorageMixin.upload_file

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.create_scan

### Options

Options for configuring analysis parameters. You can set the scan image, custom run command, etc.

::: ptsandbox.models.api.analysis.SandboxOptions

## URL

You can also scan URLs. The sandbox downloads the file from the URL and analyzes it.

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

::: ptsandbox.sandbox.sandbox.Sandbox.create_url_scan

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.create_url_scan

## Advanced scan

Use advanced scanning when you need to fine-tune launch parameters or upload additional files alongside the sample.

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
    from ptsandbox.models import VNCMode

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

::: ptsandbox.sandbox.sandbox.Sandbox.create_advanced_scan

::: ptsandbox.sandbox.api._analysis.AnalysisMixin.create_advanced_scan

### Options

Options for configuring analysis parameters. You can set the scan image, custom run command, etc.

::: ptsandbox.models.api.analysis.SandboxOptionsAdvanced

## Waiting for the report

When using `async_result=True` (the default), the sandbox returns a short report immediately. To get the full report, use `wait_for_report` which polls the sandbox until the analysis is complete.

```py title="Code example"
task = await sandbox.create_scan(Path("./example.py"))

result = await sandbox.wait_for_report(
    task,
    wait_time=120,
    error_limit=3,
)
if (report := result.get_long_report()) is not None:
    print(report.result.verdict)
```

!!! note "A scan may finish without a full report"

    `wait_for_report` stops polling as soon as the scan reaches a terminal state
    (`FULL`, `PARTIAL`, `UNSCANNED` or `UNKNOWN`), and it polls more often nearer
    the deadline so a just-finished scan is noticed quickly.

    A `PARTIAL` result is still returned as long as behavioral analysis ran
    (the SANDBOX engine finished with `FULL` or `PARTIAL`), or when behavioral
    analysis was never requested (a static-only scan) — the partial state usually
    comes from unpack depth or static checks being exceeded.

    If the scan finished but behavioral analysis did not complete (the SANDBOX
    engine ended `UNSCANNED`/`UNKNOWN`, or no full report exists at all), waiting
    any longer is pointless: instead of burning the whole `wait_time`,
    `wait_for_report` raises `SandboxScanNotFullException` with the terminal
    `scan_state` and the scan/BA error codes attached for you to react to.

!!! tip "Calculating wait_time"

    A good formula for `wait_time`:

    ```python
    wait_time = options.sandbox.analysis_duration * 4 + (
        300 if options.sandbox.analysis_duration < 80 else 120
    )
    ```

::: ptsandbox.sandbox.sandbox.Sandbox.wait_for_report
