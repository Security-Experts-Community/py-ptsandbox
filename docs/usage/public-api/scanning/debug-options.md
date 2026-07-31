!!! warning "Warning"

    Full support for debugging options is **not guaranteed.**

    They may change on both the library side and the product side.

    **Don't use them in production code.**

When creating any scan task, you can specify `DebugOptions` to configure the sample launch parameters.

::: ptsandbox.models.api.analysis.DebugOptions

## custom_syscall_hooks

Set a custom list of system calls to intercept.

Be careful: hooking a frequently used syscall can slow down the analysis.

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

    You need to check a unique sample, and the sandbox doesn't track the function of interest.

## custom_dll_hooks

This is not well-documented, so use it with caution.

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

    You need to check a unique sample, and the sandbox doesn't track the function of interest.

## custom_procdump_exclude

Use regular expressions to specify processes that will be ignored during a memory dump.

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

    Speeds up analysis when you need to ignore flooding processes.

## custom_fileextractor_exclude

Use regular expressions to specify files that will be ignored during extraction.

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

    Speeds up analysis when you need to ignore flooding files.
