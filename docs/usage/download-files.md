You can download files from the sandbox using a hash - `md5`, `sha1`, `sha256`:

```python
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))
    file_uri = "sha256:b7ad567477c83756aab9a542b2be04f77dbae25115d85f22070d74d8cc4779dc"
    data: BinaryIO = await sandbox.api.download_artifact(
        SandboxDownloadArtifactRequest(file_uri)
    )
```

Streaming is also supported if you do not need to download the entire file into memory:

```python
import aiofiles
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))
    file_uri = "sha256:b7ad567477c83756aab9a542b2be04f77dbae25115d85f22070d74d8cc4779dc"

    async with aiofiles.open("test.bin", "wb") as fd:
        async for chunk in (await sandbox.api.download_artifact_iter(SandboxDownloadArtifactRequst(file_uri))):
            await fd.write(chunk)

```
