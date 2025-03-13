from typing import Any, Literal

from pydantic import BaseModel, Field

from ptsandbox.models.core.base import BaseRequest
from ptsandbox.models.core.enum import (
    EOSStatus,
    SystemCode,
    SystemGroup,
    UploadStrategy,
)
from ptsandbox.models.ui.common import SMTPDefaultRecord


class SandboxSystemStatusResponse(BaseModel):
    """
    System events are returned here with information about the current state of the system, i.e. a slice of the current state.

    The event may relate to a specific object, in this case the ObjectId field is filled in. Basically, the event codes indicate a specific problem.
    Some events may contain additional parameters. For example `AV_ENGINE_IN_NOT_GENERAL_AVAILABILITY`

    Description of current errors:

    * `AV_ENGINE_IN_NOT_GENERAL_AVAILABILITY` - the engine is approaching or becoming unavailable. The ObjectId specifies the name of the engine.
    Example of parameters
    ```
    {
        "engineCodeName": "clamav",
        "distributionPack": "...",
        "distributionVersion": "1.1.1",
        "maintenanceStatus": "END_OF_SUPPORT"
    }
    ```

    * `STORAGE_CAPACITY_EXCEEDED_COMPONENTS_MAX_SIZE_BYTES` - Exceeding limits for a specific component

    * `STORAGE_CAPACITY_EXCEEDED_MINIMUM` - Exceeding the total minimum required free space

    * `COMPONENT_CAPACITY_EXCEEDED_THRESHOLD` - Exceeding the threshold for free space for a specific component (ObjectId)

    * `COMPONENT_CAPACITY_EXCEEDED_MAX_SIZE` - Exceeding the limit for a specific component (ObjectId)
    A list of possible components, similar to the Settings API: `['incubator', 'quarantine', 'system', 'sandbox_images']`

    * `SANDBOX_RECONFIGURING` - The configuration is being performed.

    * `NODE_IS_NOT_READY` - The node is unavailable (with the not ready status). The ObjectId contains the node name.
    The parameters indicate the time from which the status changed.
    ```
    {
        "since": 1111111.0
    }
    ```

    * `COMPONENT_ERROR` - An error in specific components of the group. The ObjectId specifies a group of components. Example:
    ```
    {
        "code": "COMPONENT_ERROR",
        "group": "SANDBOX",
        "level": "ERROR",
        "objectId": "SANDBOX",
        "params": {
            "sb-worker-1": {
                "error_codes": [
                    "OFFLINE"
                ]
            },
            "traps-resource-plugin": {
                "error_codes": [
                    "OFFLINE"
                ]
            }
        }
        ...
    }
    ```
    This error should be interpreted roughly as: An error of the "SANDBOX" subsystem. Affected components: `"sb-worker-1", "traps-resource-plugin"`

    * `COMPONENT_PARTIALLY_AVAILABLE` - Similar to COMPONENT_ERROR, only it's about the unavailability of a part of the pod, or a decrease in performance

    * `NEW_VERSION_AVAILABLE` - A new version is available. The ObjectId specifies the version

    * `NEW_VERSION_INSTALLATION_SCHEDULED` - A new version is available and it is scheduled for installation. The ObjectId specifies the version. In the settings, the scheduled installation time is
    ```
    {
        "time": 1111111
    }
    ```

    * `END_OF_SUPPORT_SOON` - Support for the `END_OF_SUPPORT` version will end soon - Support for the version has been discontinued in params
    ```
    {
        "eosTs": 1111111
    }
    ```

    * `IMAGE_INSTALL_ERROR` - Error when installing the image, the name of the image is entered in the ObjectId.

    * `NODE_HAVE_ERROR` - There are errors on the node. The ObjectId contains the node name. The error types are specified in the parameters.
    ```
    {
        "error_types": ["NetworkUnavailable", "MemoryPressure", "DiskPressure"]
    }
    ```
    """

    class Event(BaseModel):
        group: SystemGroup
        """
        Group (subsystem)
        """

        code: SystemCode
        """
        Event/Error code
        """

        object_id: str = Field(alias="objectId")
        """
        The object's ID. It can be an empty string for general events.
        """

        level: Literal["INFO", "WARNING", "ERROR"]
        """
        Event/Error level
        """

        created_ts: int = Field(alias="createdTs")
        """
        Time when the event was created
        """

        updated_ts: int = Field(alias="updatedTs")
        """
        Event update Time
        """

        params: dict[Any, Any] = {}
        """
        Additional event parameters
        """

    events: list[Event]


class SandboxSystemSettingsResponse(BaseModel):
    """
    System Settings
    """

    class Data(BaseModel):
        class Telemetry(BaseModel):
            enabled: bool
            """
            Telemetry status
            """

            send_events: bool = Field(alias="sendEvents")

        class SIEMNotifier(BaseModel):
            enabled: bool
            """
            Status of event collection and analysis
            """

            host: str
            """
            Syslog Server
            """

            port: int
            """
            Port syslog server
            """

            transport_protocol: Literal["tcp", "udp"] = Field(alias="transportProtocol")
            """
            Transmission protocol
            """

            audit_enabled: bool = Field(alias="auditEnabled")
            """
            Send audit events to the system log
            """

        class CybsiNotifier(BaseModel):
            enabled: bool
            """
            Enabling/disabling sending reports to Cybsi
            """

            api_url: str = Field(alias="apiUrl")
            """
            Cybsi URL API
            """

            api_key: str = Field(alias="apiKey")
            """
            Key for the Cybsi API
            """

            share_level: Literal["White", "Green", "Amber", "Red"] = Field(alias="shareLevel")
            """
            The access level applied to all artifacts
            """

            upload_strategy: UploadStrategy = Field(alias="uploadStrategy")
            """
            The rule for uploading artifacts
            """

        class EmailNotifier(BaseModel):
            enabled: bool
            """
            Enabling/disabling the sending of notifications by mail
            """

            notify_unwanted: bool = Field(alias="notifyUnwanted")
            """
            Notification of unwanted objects
            """

            locale: str
            """
            Locale for generated messages
            """

            sender_address: str = Field(alias="senderAddress")
            """
            Sender's address
            """

            recipients: list[str]
            """
            List of recipient addresses
            """

            smtp_default_records: list[SMTPDefaultRecord] = Field(alias="smtpDefaultRecords")
            """
            List of mail servers
            """

        class Authentication(BaseModel):
            anonymous_deny: bool = Field(alias="anonymousDeny")
            """
            Anonymous analysis is prohibited
            """

        class Unpacker(BaseModel):
            passwords: list[str]
            """
            List of passwords for unpacking password-protected archives
            """

        class EventCombiner(BaseModel):
            events_eviction_days: int = Field(alias="eventsEvictionDays")
            """
            Retention period of the verification history
            """

        class Storage(BaseModel):
            class Settings(BaseModel):
                bytes: int
                """
                Size in bytes
                """

                items: int
                """
                Number of files
                """

            class Components(BaseModel):
                class Component(BaseModel):
                    class Settings(BaseModel):
                        bytes: int
                        """
                        Size in bytes
                        """

                        items: int
                        """
                        Number of files
                        """

                    class Threshold(BaseModel):
                        bytes_percent: int = Field(alias="bytesPercent")
                        """
                        Percentage of threshold in bytes
                        """

                        items_percent: int = Field(alias="itemsPercent")
                        """
                        The percentage of the threshold in the number of files
                        """

                    current_limit: Settings = Field(alias="currentLimit")

                    current_size: Settings = Field(alias="currentSize")

                    min_size: Settings = Field(alias="minSize")

                    threshold: Threshold

                sandbox_images: Component = Field(alias="sandboxImages")

                quarantine: Component

                system: Component

                incubator: Component

            capacity: Settings

            current_size: Settings = Field(alias="currentSize")

            components: Components

        class Quarantine(BaseModel):
            retention_period: int = Field(alias="retentionPeriod")
            """
            Storage period in quarantine
            """

            use_smtp: bool = Field(alias="useSMTP")
            """
            Use a backup mail server to forward emails
            """

            smtp_default_records: list[SMTPDefaultRecord] = Field(alias="smtpDefaultRecords")
            """
            List of mail servers
            """

        class Retro(BaseModel):
            enabled: bool
            """
            The status of the retro check
            """

        telemetry: Telemetry

        siem_notifier: SIEMNotifier = Field(alias="siemNotifier")

        cybsi_notifier: CybsiNotifier = Field(alias="cybsiNotifier")

        email_notifier: EmailNotifier = Field(alias="emailNotifier")

        authentication: Authentication

        unpacker: Unpacker

        event_combiner: EventCombiner = Field(alias="eventCombiner")

        storage: Storage

        quarantine: Quarantine

        retro: Retro

    data: Data


class SandboxUpdateSystemSettingsRequest(BaseRequest):
    class SIEMNotifier(BaseModel):
        enabled: bool | None = None
        """
        Status of event collection and analysis
        """

        host: str | None = None
        """
        Syslog Server
        """

        port: int | None = None
        """
        Port syslog server
        """

        transport_protocol: Literal["tcp", "udp"] | None = Field(default=None, serialization_alias="transportProtocol")
        """
        Transmission protocol
        """

        audit_enabled: bool | None = Field(default=None, serialization_alias="auditEnabled")
        """
        Send audit events to the system log
        """

    class CybsiNotifier(BaseModel):
        enabled: bool | None = None
        """
        Enabling/disabling sending reports to Cybsi
        """

        api_url: str | None = Field(default=None, serialization_alias="apiUrl")
        """
        Cybsi URL API
        """

        api_key: str | None = Field(default=None, serialization_alias="apiKey")
        """
        Key for the Cybsi API
        """

        share_level: Literal["White", "Green", "Amber", "Red"] | None = Field(
            default=None, serialization_alias="shareLevel"
        )
        """
        The access level applied to all artifacts
        """

        upload_strategy: UploadStrategy | None = Field(default=None, serialization_alias="uploadStrategy")
        """
        The rule for uploading artifacts
        """

    class EmailNotifier(BaseModel):
        enabled: bool
        """
        Enabling/disabling the sending of notifications by mail
        """

        notify_unwanted: bool = Field(serialization_alias="notifyUnwanted")
        """
        Notification of unwanted objects
        """

        locale: str
        """
        Locale for generated messages
        """

        sender_address: str = Field(serialization_alias="senderAddress")
        """
        Sender's address
        """

        recipients: list[str]
        """
        List of recipient addresses
        """

        smtp_default_records: list[SMTPDefaultRecord] = Field(serialization_alias="smtpDefaultRecords")
        """
        List of mail servers
        """

    class Authentication(BaseModel):
        anonymous_deny: bool = Field(serialization_alias="anonymousDeny")
        """
        Anonymous analysis is prohibited
        """

    class Unpacker(BaseModel):
        passwords: list[str]
        """
        List of passwords for unpacking password-protected archives
        """

    class EventCombiner(BaseModel):
        events_eviction_days: int = Field(serialization_alias="eventsEvictionDays")
        """
        Retention period of the verification history
        """

    class Storage(BaseModel):
        class Components(BaseModel):
            class Component(BaseModel):
                class Settings(BaseModel):
                    bytes: int | None = None
                    """
                    Size in bytes
                    """

                    items: int | None = None
                    """
                    Number of files
                    """

                current_limit: Settings = Field(serialization_alias="currentLimit")

            quarantine: Component | None = None

            incubator: Component | None = None

        components: Components

    class Quarantine(BaseModel):
        retention_period: int | None = Field(default=None, serialization_alias="retentionPeriod")
        """
        Storage period in quarantine
        """

        use_smtp: bool | None = Field(default=None, serialization_alias="useSMTP")
        """
        Use a backup mail server to forward emails
        """

        smtp_default_records: list[SMTPDefaultRecord] | None = Field(
            default=None, serialization_alias="smtpDefaultRecords"
        )
        """
        List of mail servers
        """

    class Retro(BaseModel):
        enabled: bool
        """
        The status of the retro check
        """

    authentication: Authentication | None = None

    event_combiner: EventCombiner | None = Field(default=None, serialization_alias="eventCombiner")

    quarantine: Quarantine | None = None

    retro: Retro | None = None

    unpacker: Unpacker | None = None

    siem_notifier: SIEMNotifier | None = Field(default=None, serialization_alias="siemNotifier")

    cybsi_notifier: CybsiNotifier | None = Field(default=None, serialization_alias="cybsiNotifier")

    storage: Storage | None = None

    email_notifier: EmailNotifier | None = Field(default=None, serialization_alias="emailNotifier")


class SandboxSystemVersionResponse(BaseModel):
    class Data(BaseModel):
        version: str

        eos_ts: int = Field(alias="eosTs")

        eos_status: EOSStatus = Field(alias="eosStatus")

    data: Data
