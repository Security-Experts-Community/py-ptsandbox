# ptsandbox

The package exports `Sandbox` and `SandboxKey`:

```py
from ptsandbox import Sandbox, SandboxKey
```

Use `Sandbox` as an async context manager to close its HTTP sessions automatically.
Its `api` attribute provides access to the Public API; its `ui` attribute provides
access to the UI API after authorization.

- [Sandbox client](sandbox.md)
- [Request and response models](models.md)
- [Exceptions](exceptions.md)
- [Detection utilities](utils.md)

::: ptsandbox
    options:
      members: []
