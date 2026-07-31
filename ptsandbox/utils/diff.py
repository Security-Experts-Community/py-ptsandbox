import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import orjson

logger = logging.getLogger(__name__)


class DetectionType(StrEnum):
    SILENT = "silent"
    SUSPICIOUS = "suspicious"
    MALWARE = "malware"


@dataclass(frozen=True, slots=True)
class Detect:
    name: str
    weight: int | None

    def __key(self) -> tuple[str]:
        return (self.name,)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Detect):
            return self.__key() == other.__key()

        return NotImplemented


class Detections:
    detections: dict[DetectionType, set[Detect]]

    _real_name: str = ""

    def __init__(self, trace: bytes) -> None:
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
                if detect_type in DetectionType.__members__:
                    self.detections[DetectionType[detect_type]].add(
                        Detect(
                            name=event.get("detect.name", ""),
                            weight=event.get("weight"),
                        )
                    )
            except Exception:
                logger.exception("Got error while parsing traces")

    def __repr__(self) -> str:
        return repr(self.detections)

    @property
    def silent(self) -> set[Detect]:
        """Only silent detects"""
        return self.detections[DetectionType.SILENT]

    @property
    def suspicious(self) -> set[Detect]:
        """Only suspicious detects"""
        return self.detections[DetectionType.SUSPICIOUS]

    @property
    def malware(self) -> set[Detect]:
        """Only malware detects"""
        return self.detections[DetectionType.MALWARE]
