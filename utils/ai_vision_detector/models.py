"""Data models for the AI vision grounding system."""

from typing import Tuple


class GroundingCandidate:
    """Represents a grounding proposal with bounding box and confidence."""

    def __init__(self, x: int, y: int, w: int, h: int, confidence: float, source: str = "ai"):
        self.x = x  # Top-left x
        self.y = y  # Top-left y
        self.w = w  # Width
        self.h = h  # Height
        self.confidence = confidence
        self.source = source

    @property
    def center(self) -> Tuple[int, int]:
        """Return center coordinates for clicking."""
        return (self.x + self.w // 2, self.y + self.h // 2)

    @property
    def area(self) -> int:
        return self.w * self.h

    def __repr__(self):
        return (
            f"GroundingCandidate(center={self.center}, "
            f"bbox=({self.x},{self.y},{self.w},{self.h}), "
            f"conf={self.confidence:.2f})"
        )
