You can download files from the sandbox using a `sha256` hash.

```py title="Code example" hl_lines="6"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    data = await sandbox.get_file("...")
    with open("./file", "wb") as fd:
        fd.write(data)
```

Use streaming if you don't want to load the entire file into memory:

```py title="Code example" hl_lines="8"
import aiofiles
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    async with aiofiles.open("./file", "wb") as fd:
        async for chunk in sandbox.get_file_stream("..."):
            await fd.write(chunk)

```

::: ptsandbox.sandbox.sandbox.Sandbox.get_file

::: ptsandbox.sandbox.sandbox.Sandbox.get_file_stream

### Low-level API

Under the hood, `Sandbox.get_file` uses `download_artifact` with a `sha256:<hash>` file URI. You can use these methods directly to download by any file URI (e.g. from a task report):

```py title="Direct API usage"
from ptsandbox import Sandbox, SandboxKey

sandbox = Sandbox(SandboxKey(...))

# Download as bytes
data = await sandbox.api.download_artifact("sha256:abc123...")

# Or stream to avoid loading into memory
async for chunk in sandbox.api.download_artifact_stream("sha256:abc123..."):
    ...
```

::: ptsandbox.sandbox.api._storage.StorageMixin.download_artifact

::: ptsandbox.sandbox.api._storage.StorageMixin.download_artifact_stream

??? example "Download all files from a task"

    ```py
    import asyncio
    import sys
    from pathlib import Path
    from typing import Any, Coroutine
    from uuid import UUID

    import aiofiles

    from ptsandbox import Sandbox, SandboxKey
    from ptsandbox.models import ArtifactType

    semaphore = asyncio.Semaphore(12)


    async def save_file(sandbox: Sandbox, file: Path, hash: str) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)

        async with semaphore:
            async with aiofiles.open(f"{file}.{hash}", "wb") as fd:
                async for chunk in sandbox.get_file_stream(hash):
                    await fd.write(chunk)

        print(f"saved {file}")


    async def main(task_id: UUID) -> None:
        sandbox = Sandbox(
            key=SandboxKey(
                name="test-key-1",
                key="<TOKEN_FROM_SANDBOX>",
                host="10.10.10.10",
            ),
        )

        result = await sandbox.get_report(task_id)
        if (report := result.get_long_report()) is None:
            print("Can't get full report")
            return

        tasks: list[Coroutine[Any, Any, None]] = []
        for artifact in report.artifacts:
            if not (sandbox_result := artifact.find_sandbox_result()):
                continue

            if not sandbox_result.details:
                continue

            if not sandbox_result.details.sandbox:
                continue

            if not sandbox_result.details.sandbox.artifacts:
                continue

            for file in sandbox_result.details.sandbox.artifacts:
                if not file.file_info:
                    continue

                if file.type != ArtifactType.FILE:
                    continue

                tasks.append(
                    save_file(
                        sandbox,
                        Path("artifacts") / Path(file.file_info.file_path.removeprefix("/")),
                        file.file_info.sha256,
                    )
                )

        await asyncio.gather(*tasks)


    if __name__ == "__main__":
        asyncio.run(main(UUID(sys.argv[1])))
    ```

!!! warning "Restrictions"

    The sandbox doesn't let you view a task report created with a different token, so you can only download your own files.

## Get task report

To download all files from a task, you first need the full report which contains the list of artifacts:

```py title="Code example"
from uuid import UUID
from ptsandbox import Sandbox, SandboxKey

sandbox = Sandbox(SandboxKey(...))

report = await sandbox.get_report(UUID("..."))
if (long_report := report.get_long_report()) is not None:
    for artifact in long_report.artifacts:
        print(artifact)
```

::: ptsandbox.sandbox.sandbox.Sandbox.get_report
