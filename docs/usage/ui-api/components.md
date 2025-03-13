Get information about system components

```py title="Code example" hl_lines="12-14"
import asyncio

from ptsandbox import Sandbox
from ptsandbox.models import SandboxKey


async def main():
    sandbox = Sandbox(SandboxKey(...))

    await sandbox.ui.authorize()

    data = await sandbox.ui.get_system_components_status()
    for component in data.components:
        print(component.name, component.status, ",".join(x.name for x in component.pods))


asyncio.run(main())
```

??? quote "Response model in `ptsandbox/models/ui/components.py`"

    ```py
    class SandboxComponentsResponse(BaseModel):
        """
        Information about system components
        """

        class Component(BaseModel):
            class Pod(BaseModel):
                name: str

                component_name: str = Field(alias="componentName")
                """
                Which component does it belong to
                """

                ready: bool
                """
                Ready status
                """

                node: str
                """
                The name of the node it is running on
                """

                restarts: int

                error_reason: str = Field(alias="errorReason")
                """
                The type of error, if any
                """

                error_message: str = Field(alias="errorMessage")
                """
                Error message, if any
                """

                uptime: int
                """
                Time elapsed since the container was launched (in seconds)
                """

                containers_running: int = Field(alias="containersRunning")
                """
                The number of working containers for a given hearth
                """

                containers_total: int = Field(alias="containersTotal")
                """
                The total number of containers specified in the pod specification (excluding init containers)
                """

            name: str

            total_pods: int = Field(alias="totalPods")
            """
            How many pods are there in total
            """

            ready_pods: int = Field(alias="readyPods")
            """
            How many are running
            """

            nodes: list[str]
            """
            The list of nodes running the component's pods
            """

            status: ComponentStatus
            """
            Component status
            """

            type: ComponentType
            """
            Component type
            """

            pods: list[Pod] = []
            """
            Список подов
            """

        components: list[Component] = []
    ```
