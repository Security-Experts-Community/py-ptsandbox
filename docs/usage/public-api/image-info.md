Getting a list of installed images in the sandbox:

```py title="Code example" hl_lines="7"
from ptsandbox import Sandbox, SandboxKey

async def example() -> None:
    key = SandboxKey(...)
    sandbox = Sandbox(key)

    images = await sandbox.get_images()
    print(images)
```

!!! example "Example output"

    ```json
    [
        SandboxImageInfo(image_id='ubuntu-jammy-x64', ...),
        SandboxImageInfo(image_id='win10-1803-x64', ...),
        ...
    ]
    ```

::: ptsandbox.sandbox.sandbox.Sandbox.get_images

::: ptsandbox.sandbox.api._maintenance.MaintenanceMixin.get_images
