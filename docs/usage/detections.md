The library ships a small helper for parsing detects from a raw drakvuf trace (JSON lines).

It is useful when comparing traces: for example, to see which detects appear or disappear after updating correlation rules and running a rescan on the same trace.

```py title="Code example"
from pathlib import Path

from ptsandbox.utils import Detections

detections = Detections(Path("./drakvuf-trace.log").read_bytes())

print(detections.malware)    # only malware detects
print(detections.suspicious) # only suspicious detects
print(detections.silent)     # only silent detects
```

!!! example "Example output"

    ```python
    {
        'malware': {Detect(name='Detect.Carbon.StopBatch', weight=100)},
        'silent': {Detect(name='Detect.Carbon.SysMonLogOff', weight=30)},
        'suspicious': set()
    }
    ```

`Detect` objects are frozen and hashable, so you can diff detections between two traces with plain set operations:

```py title="Comparing traces"
from pathlib import Path

from ptsandbox.utils import Detections

old = Detections(Path("./drakvuf-trace.log").read_bytes())
new = Detections(Path("./drakvuf-trace.new.log").read_bytes())

# detects that appeared in the new trace
appeared = new.malware - old.malware

# detects that are no longer produced
disappeared = old.malware - new.malware

print(appeared, disappeared)
```

::: ptsandbox.utils.diff.Detections

::: ptsandbox.utils.diff.Detect

::: ptsandbox.utils.diff.DetectionType
