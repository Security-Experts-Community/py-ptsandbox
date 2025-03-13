from pydantic import BaseModel, Field


class SandboxClusterStatusResponse(BaseModel):
    """
    Cluster information
    """

    class Node(BaseModel):
        class Condition(BaseModel):
            type: str
            message: str

        class Info(BaseModel):
            """
            System Information: Component versions
            """

            kubernetes: str
            """
            Kubernetes version
            """

            container_runtime: str = Field(alias="containerRuntime")
            """
            Containerd version
            """

            os: str

            os_image: str = Field(alias="osImage")

            os_kernel: str = Field(alias="osKernel")

            xen_version: str = Field(alias="xenVersion")

            vm_cpu: int = Field(alias="vmCpu")
            """
            The number of cores allocated for the BA
            """

            vm_ram: int = Field(alias="vmRam")
            """
            The amount of RAM allocated for the BA in Bytes
            """

        class IPs(BaseModel):
            class IP(BaseModel):
                type: str
                ip: str

            internal: IP
            cluster: IP

        name: str

        hostname: str = Field(alias="hostName")

        ready: bool
        """
        Node status
        """

        cpu: int
        """
        Number of cores
        """

        ram: int
        """
        The amount of RAM in Bytes
        """

        vm_capacity: int = Field(alias="vmCapacity")
        """
        The number of traps per node. Total capacity.
        """

        vm_allocatable: int = Field(alias="vmAllocatable")
        """
        The number of traps per node. Currently in use.
        """

        conditions: list[Condition]
        """
        Problematic conditions on the node Problematic conditions on the node will be shown here.

        Examples of conditions:

        ```
        [
            { "message": "Calico is not running on this node", "type": "NetworkUnavailable" },
            { "message": "kubelet has unsufficient memory available", "type": "MemoryPressure" },
            { "message": "kubelet has disk pressure", "type": "DiskPressure" },
            { "message": "Kubelet stopped posting node status.", "type": "Ready" }
        ]
        ```
        """

        total_pods: int = Field(alias="totalPods")
        """
        The total number of pods per node
        """

        ready_pods: int = Field(alias="readyPods")

        running_pods: int | None = Field(default=None, alias="runningPods")
        """
        The number of working pods on the node
        """

        roles: list[str]
        """
        Node labels
        """

        info: Info

        ips: IPs

    high_availability: bool = Field(alias="highAvailability")
    """
    High availability mode
    """

    cluster_ip: str = Field(alias="clusterIp")

    sb_nodes: int = Field(alias="sbNodes")
    """
    Number of nodes
    """

    sb_nodes_available: int = Field(alias="sbNodesAvailable")
    """
    Number of available BA nodes
    """

    vms_count: int = Field(alias="vmsCount")
    """
    Number of VMs
    """

    vms_count_available: int = Field(alias="vmsCountAvailable")
    """
    Number of available VMs
    """

    nodes: list[Node] = []
    """
    List of nodes
    """
