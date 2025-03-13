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

??? quote "Response model in `ptsandbox/models/core/common.py`"

    ```python
    class SandboxImageInfo(BaseModel):
        """
        Information about the VM image
        """

        class OS(BaseModel):
            """
            Information about the operating system of the virtual machine
            """

            name: str
            """
            Name of the operating system
            """

            version: str
            """
            Operating system version
            """

            architecture: str
            """
            Processor architecture supported by the operating system
            """

            service_pack: str | None = Field(
                default=None,
                validation_alias=AliasChoices("service_pack", "servicePack"),
            )
            """
            The name of the operating system update package
            """

            locale: str
            """
            Operating system locale
            """

        image_id: str = Field(validation_alias=AliasChoices("image_id", "name", "id"))
        """
        ID of the VM image

        The new UI began to return the name of the image. However, in the form of a name.
        """

        type: SandboxImageType | None = None
        """
        The type of image.
        """

        version: str
        """
        Version of the VM image
        """

        os: OS | None = None
        """
        Information about the operating system of the virtual machine image
        """
    ```
