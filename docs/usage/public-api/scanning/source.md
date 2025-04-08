## Overview

The sandbox allows you to create scan sources for which you can pre-configure the scan settings.

![Sources](../../../assets/sources.png)

To do this, create a source as shown in the example below and select the appropriate API key for it. In our case - `example-source-token`.

![New Source](../../../assets/new-source.png)

!!! note

    The API key must have at least the `Check with source settings` permission.

Additional details can be found in the sandbox documentation.

## Scan files

```py title="Code example (sync scanning)" hl_lines="16"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FOR_SOURCE>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    report = await sandbox.source_check_file("./malware.exe") # (1)!
    print(report)

asyncio.run(main())
```

1. By default, a short report is returned. For a full report, add the option `short_report=False`

```py title="Code example (async scanning)" hl_lines="16-19 24"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FOR_SOURCE>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.source_check_file(
        "./malware.elf",
        async_result=True,
    )

    report = await sandbox.wait_for_report(
        response,
        wait_time=100,
        scan_with_sources=True, # (1)!
    )


asyncio.run(main())
```

1. When using asynchronous requests with a source, you **must pass the option `scan_with_sources=True`**, otherwise you will get a 401 error.

More parameters can be found below 👇

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
    ```

## Scan URLs

```py title="Code example (sync scanning)" hl_lines="16"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FOR_SOURCE>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    report = await sandbox.source_check_url("http://malware.com/file.elf") # (1)!
    print(report)

asyncio.run(main())
```

1. By default, a short report is returned. For a full report, add the option `short_report=False`

```py title="Code example (async scanning)" hl_lines="16-19 24"
import asyncio
from pathlib import Path

from ptsandbox import Sandbox, SandboxKey


async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FOR_SOURCE>",
        host="10.10.10.10",
    )

    sandbox = Sandbox(key)

    task = await sandbox.source_check_url(
        "http://malware.com/file.elf",
        async_result=True,
    )

    report = await sandbox.wait_for_report(
        response,
        wait_time=100,
        scan_with_sources=True, # (1)!
    )


asyncio.run(main())
```

1. When using asynchronous requests with a source, you **must pass the option `scan_with_sources=True`**, otherwise you will get a 401 error.

More parameters can be found below 👇

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
    ```
