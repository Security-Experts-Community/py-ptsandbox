You can download files from the sandbox using a `sha256` hash.

```py title="Code example" hl_lines="6"
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    data = await sandbox.get_file("...")
    with open("./file", "wb") as fd:
        fd.write(data)
```

Streaming is also supported if you don't need to download the entire file into memory:

```py title="Code example" hl_lines="8"
import aiofiles
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    async with aiofiles.open("./file", "wb") as fd:
        async for chunk in sandbox.get_file_stream("..."):
            await fd.write(chunk)

```

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

    The sandbox currently has a restriction that **doesn't allow** you to view the task report if it was created with **another token**, so you can download only your own files.
