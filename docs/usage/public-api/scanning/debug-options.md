!!! warning "Warning"

    Full support for debugging options is **not guaranteed.**

    They can constantly change both on the library side and on the product side.

    **Don't use them in production code.**

When creating any scan task, you can specify `DebugOptions`, which allow you to additionally configure the sample launch parameters.

??? quote "Source code in `ptsandbox/models/api/analysis.py`"

    ```py
    class DebugOptions(TypedDict):
        """
        Description of all available debugging options for very detailed scan configuration
        """

        keep_sandbox: NotRequired[bool]
        """
        Don't destroy the sandbox after scanning
        """

        skip_work: NotRequired[bool]
        """
        Perform a scan, skipping the data collection stage for analysis
        """

        extract_crashdumps: NotRequired[bool]
        """
        Extract crashdumps from the sandbox
        """

        save_debug_files: NotRequired[bool]
        """
        Save files necessary for debugging (error logs, tcpdump logs, etc)
        """

        rules_url: NotRequired[str]
        """
        Use the specified normalization and correlation rules
        The rules are specified as a link to the archive containing the compiled rules
        """

        sleep_work: NotRequired[bool]
        """
        Perform a scan, replacing the data collection stage for analysis with an equivalent waiting time
        """

        disable_syscall_hooks: NotRequired[bool]
        """
        Disable syscall hooks functionality

        Read more about these hooks in documentation
        """

        disable_dll_hooks: NotRequired[bool]
        """
        Disable dll hooks functionality

        Read more about these hooks in documentation
        """

        custom_syscall_hooks: NotRequired[str]
        """
        Use the specified list of system calls to intercept

        The list is transmitted as an http link to a file with the names of system calls

        Read more about this file in documentation
        """

        custom_dll_hooks: NotRequired[str]
        """
        Use the specified list of system calls to intercept

        The list is transmitted as an http link to a file with the names of dll hooks for apimon plugin

        Read more about this file in documentation
        """

        disable_retries: NotRequired[bool]
        """
        Disable task re-execution in case of a scan error
        """

        enable_sanitizers: NotRequired[bool]
        """
        Enable the debugging mechanisms of the sanitizers group
        """

        allowed_outbound_connections: NotRequired[list[str]]
        """
        Whitelist of IP addresses to which connections from a VM are allowed (backconnect)
        """

        payload_completion_event: NotRequired[str]
        """
        A regular expression for the raw DRAKVUF event, signaling the end of the useful work of the sample.

        If this option is specified, sandbox-worker will calculate and log the PAYLOAD_SCAN_TIME metric.
        """

        disable_procdump_on_finish: NotRequired[bool]
        """
        Disable the functionality of removing the memory dump from the sample at the end of the observation
        """

        skip_update_time: NotRequired[bool]
        """
        Do not synchronize the time in the VM with the host
        """

        disable_manual_scan_events: NotRequired[bool]
        """
        Do not send lifecycle notifications for manual behavioral analysis (console is ready, console is closed, etc.)
        """

        bootkitmon_boot_timeout: NotRequired[int]
        """
        The maximum waiting time for VM loading in seconds (90 seconds by default)
        """

        custom_procdump_exclude: NotRequired[str]
        """
        A file with a list of processes for which memory dumps should not be removed.

        Each line in the file is a regular expression of the path to the process file on disk.

        Read more about this file in documentation
        """

        custom_fileextractor_exclude: NotRequired[str]
        """
        A file with a list of files that should not be extracted

        Each line in the file is a regular expression of the path to the file on disk.

        Read more about this file in documentation
        """

        validate_plugins: NotRequired[bool]
        """
        Check plugins for at least one event during the entire behavioral analysis
        """

        extra_vm_init_url: NotRequired[str]
        """
        Run this script in the VM immediately before launching the behavioral analysis.

        It is useful, for example, to check the network during analysis.
        """
    ```

## custom_syscall_hooks

Allows you to set your own list of system calls to intercept.

Be careful, hooking a frequently used syscall can significantly slow down the analysis.

=== "Linux"

    ```
    cachestat
    chdir
    fstat
    open
    read
    write
    ```

=== "Windows"

    ```
    NtQueryKey
    NtQueryLicenseValue
    NtQueryObject
    NtQueryValueKey
    NtRaiseException
    NtReadFile
    NtSetValueKey
    NtShutdownSystem
    NtSuspendThread
    ```

The full list of system calls:

- Linux - [syscalls.mebeim.net](https://syscalls.mebeim.net/?table=x86/64/x64/latest)
- Windows - [j00ru.vexillium.org](https://j00ru.vexillium.org/syscalls/nt/64/)

!!! example "Usecase"

    It is necessary to check some unique sample, and the sandbox doesn't track the function of interest.

## custom_dll_hooks

It's not a well-documented thing, so use it carefully.

format:

```
<FunctionName>,log,<PARAM1>:<TYPE1>,<PARAM2>:<TYPE2>
```

=== "Windows"

    ```text
    AbortSystemShutdownA,log,lpMachineName:lpstr
    AbortSystemShutdownW,log,lpMachineName:lpwstr
    InitiateShutdownA,log,lpMachineName:lpstr,lpMessage:lpstr,dwGracePeriod:dword,dwShutdownFlags:shutdown_flags,dwReason:shutdown_reason
    waveInOpen,log,phwi:lpvoid,uDeviceID:int,pwfx:lpvoid,dwCallback:lpvoid,dwInstance:lpvoid,fdwOpen:dword
    ```

!!! example "Usecase"

    It is necessary to check some unique sample, and the sandbox doesn't track the function of interest.

## custom_procdump_exclude

Allows you to use regular expressions to specify a list of processes that will be ignored during a memory dump.

To check that a regular expression is exactly right, use [regex101.com](https://regex101.com/) and **Golang** flavor.

=== "Linux"

    ```
    ^kworker\/\d:\d$
    ^\/usr\/bin\/.*$
    ```

=== "Windows"

    ```
    ^\\device\\harddiskvolume\d+\\windows\\system32\\csrss\.exe$
    ```

!!! example "Usecase"

    It allows you to significantly speed up the analysis if you need to ignore any flooding processes.

## custom_fileextractor_exclude

Allows you to use regular expressions to specify a list of files that will be ignored during extraction.

=== "Linux"

    ```sh
    ^\/etc\/(nsswitch|host|resolv)\.conf$
    ^\/lib32\/ld-.*\.so$
    ```

=== "Windows"

    ```sh
    ^.*\\users\\.*\\appdata\\local\\google\\chrome\\user data\\default\\favicons-journal$
    ^.*\\windows\\prefetch\\.*$
    ```

!!! example "Usecase"

    It allows you to significantly speed up the analysis if you need to ignore any flooding files.
