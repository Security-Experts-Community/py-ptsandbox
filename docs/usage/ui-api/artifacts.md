## Export in csv

```py title="Code example" hl_lines="9-11"
import asyncio
import aiofiles
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    async with aiofiles.open("./tasks.csv", "wb") as fd:
        async for chunk in sandbox.ui.get_artifacts_csv():
            await fd.write(chunk)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_artifacts_csv(
        self,
        query: str = "",
        columns: (
            list[
                Literal[
                    "behavioralAnalysis",
                    "bwListStatus",
                    "createProcess",
                    "detects.avast",
                    "detects.clamav",
                    "detects.drweb",
                    "detects.eset",
                    "detects.kaspersky",
                    "detects.nano",
                    "detects.ptesc",
                    "detects.vba",
                    "detects.yara",
                    "detects.yara.test",
                    "emlBcc",
                    "emlCC",
                    "emlFrom",
                    "emlTo",
                    "fileExtensionTypeGroup",
                    "fileLabels",
                    "fileMd5",
                    "fileName",
                    "fileSha1",
                    "fileSha256",
                    "fileSize",
                    "fileType",
                    "fromTo",
                    "imageDuration",
                    "imageName",
                    "mimeType",
                    "nodeType",
                    "priority",
                    "receivedFrom",
                    "ruleEngineDetects",
                    "ruleEngineVerdict",
                    "sandboxBehavioral",
                    "sandboxBootkitmon",
                    "sandboxDetects",
                    "sandboxVerdict",
                    "smtpFrom",
                    "smtpTo",
                    "source",
                    "ssdeep",
                    "status",
                    "subject",
                    "taskId",
                    "time",
                    "verdict",
                    "verdict.avast",
                    "verdict.clamav",
                    "verdict.drweb",
                    "verdict.eset",
                    "verdict.kaspersky",
                    "verdict.nano",
                    "verdict.ptesc",
                    "verdict.vba",
                    "verdict.yara",
                    "verdict.yara.test",
                    "verdictPriority",
                    "verdictReason",
                ]
            ]
            | None
        ) = None,
        utc_offset_seconds: int = 0,
    ) -> AsyncIterator[bytes]:
        """
        Export an artifacts listing to CSV

        Args:
            query: filtering using the query language. For the syntax, see the user documentation.
            columns: the list of csv columns to be exported.
            utc_offset_seconds: the offset of the user's time from UTC, which will be used for the time in QL queries

        Returns:
            AsyncIterator with chunks of CSV file
        """

        if columns is None:
            columns = []

        data: dict[str, Any] = {
            "format": "CSV",  # only csv supported by now
            "query": query,
            "columns": ",".join(columns),
            "utcOffsetSeconds": utc_offset_seconds,
        }

        response = await self.http_client.get(f"{self.key.ui_url}/v2/artifacts/export", params=data)

        response.raise_for_status()

        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk
    ```

## Get filter values

```py title="Code example" hl_lines="8"
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    sandbox = Sandbox(...)
    await sandbox.ui.authorize()

    values = await sandbox.ui.get_artifacts_filter_values()
    print(values)

asyncio.run(main())
```

??? quote "Source code in `ptsandbox/sandbox/sandbox_ui.py`"

    ```py
    @_token_required
    async def get_artifacts_filter_values(
        self,
        from_: str = "",
        to: str = "",
        scan_id: UUID | None = None,
    ) -> SandboxArtifactsFilterValuesResponse:
        """
        Get possible values for filters based on sources and validation results

        Args:
            from_: for which period possible values are being searched: minimum time
            to: for which period possible values are being searched: maximum time
            scan_id: filter by task ID

        Returns:
            Possible filter values
        """

        data: dict[str, Any] = {}
        if scan_id is not None:
            data.update({"scanId": scan_id})

        if from_:
            data.update({"from": from_})

        if to:
            data.update({"to": to})

        response = await self.http_client.get(f"{self.key.ui_url}/v2/artifacts/filter-values", params=data)

        response.raise_for_status()

        return SandboxArtifactsFilterValuesResponse.model_validate(await response.json())
    ```
