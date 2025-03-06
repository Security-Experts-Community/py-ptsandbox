## Basic scan

This is what a typical setup of options for creating scans in a sandbox looks like.

```python
from ptsandbox import SandboxCreateScanTaskRequest, SandboxOptions

sandbox_options = SandboxCreateScanTaskRequest.Options(
    analysis_depth = 2,
    passwords_for_unpack=["infected"],
    sandbox=SandboxOptions(
        image_id="ubuntu-jammy-x64", # or any available image in your license
        analysis_duration=120, # in seconds
        debug_options = {
            "save_debug_files": True,
            "allowed_outbound_connections": ["10.10.10.20"]
        },
    )
)
```

## Advanced scan

If we want to gain more control over the sandbox, we can use other options.

```py
from ptsandbox import SandboxOptionsNew, VNCMode

sandbox_options = SandboxOptionsNew(
    image_id="win11-23H2-x64",
    analysis_duration=600, # 10 minutes to get everything done
    disable_clicker=True, # disable clicker (manual analysis)
    skip_sample_run=False, # disable automatic sample launch
    vnc_mode=VNCMode.FULL, # enable interactive session
    save_video=True, # save video after analysis complete
    extra_files=... # need upload files first
    debug_options={
        "save_debug_files" : False,
        ...
    }
)
```
