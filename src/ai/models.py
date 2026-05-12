from dataclasses import dataclass
from typing import Tuple


@dataclass
class GroundingCandidate:
    x: int
    y: int
    w: int
    h: int
    confidence: float
    source: str = "ai"

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    @property
    def area(self) -> int:
        return self.w * self.h

    def __repr__(self) -> str:
        return (
            f"GroundingCandidate(center={self.center}, "
            f"bbox=({self.x},{self.y},{self.w},{self.h}), "
            f"conf={self.confidence:.2f}, source={self.source!r})"
        )
