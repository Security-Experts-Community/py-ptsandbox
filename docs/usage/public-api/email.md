Upload an email and get its headers.

```py title="Code example" hl_lines="8"
import aiofiles
from ptsandbox import Sandbox, SandboxKey, SandboxDownloadArtifactRequst

async def example() -> None:
    sandbox = Sandbox(key=SandboxKey(...))

    async with aiofiles.open("./email-headers", "wb") as fd:
        async for chunk in sandbox.get_email_headers(Path("./email.bin")):
            fd.write(chunk)
```

??? quote "Source code in `ptsandbox/sandbox/sandbox.py`"

    ```py
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
            case BytesIO():
                iterator = self.api.get_email_headers(file)
            case _:
                raise SandboxException(f"Unsupported type: {type(file)}")

        async for chunk in iterator:
            yield chunk
    ```
