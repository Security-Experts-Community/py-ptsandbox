from dataclasses import dataclass
from enum import Enum
from typing import Any

import orjson
from loguru import logger


class DetectionType(str, Enum):
    SILENT = "silent"
    SUSPICIOUS = "suspicious"
    MALWARE = "malware"


@dataclass(frozen=True)
class Detect:
    name: str
    weight: int | None

    def __key(self) -> tuple[str]:
        return (self.name,)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Detect):
            return self.__key() == other.__key()  # noqa: W0212

        raise NotImplementedError()


class Detections:
    detections: dict[DetectionType, set[Detect]]

    _real_name: str

    def __init__(self, trace: bytes, ctx: str = "") -> None:
        self.detections = {
            DetectionType.SILENT: set(),
            DetectionType.SUSPICIOUS: set(),
            DetectionType.MALWARE: set(),
        }

        for line in trace.splitlines(keepends=False):
            try:
                event: dict[str, Any] = orjson.loads(line)
                if event.get("auxiliary.type", None) == "init":
                    self._real_name = event.get("object.name", "")

                detect_type: str = event.get("detect.type", "").upper()
                if detect_type in DetectionType._member_names_:
                    self.detections[DetectionType[detect_type]].add(
                        Detect(
                            name=event.get("detect.name", ""),
                            weight=event.get("weight", None),
                        )
                    )
            except Exception as ex:
                logger.error(f"Parsing trace exception: {ex!r} ({ctx = })")

    def __repr__(self) -> str:
        return repr(self.detections)

    @property
    def silent(self) -> set[Detect]:
        """Только silent-детекты"""
        return self.detections[DetectionType.SILENT]

    @property
    def suspicious(self) -> set[Detect]:
        """Только suspicious-детекты"""
        return self.detections[DetectionType.SUSPICIOUS]

    @property
    def malware(self) -> set[Detect]:
        """Только malware-детекты"""
        return self.detections[DetectionType.MALWARE]
