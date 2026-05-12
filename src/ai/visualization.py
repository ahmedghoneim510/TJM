import datetime
import os
from typing import List, Optional

import cv2

import config
from .models import GroundingCandidate


def visualize_grounding(
    screenshot_path: str,
    candidates: List[GroundingCandidate],
    selected: Optional[GroundingCandidate],
    output_path: str | None = None,
) -> str:
    screenshot = cv2.imread(screenshot_path)
    overlay = screenshot.copy()

    for i, c in enumerate(candidates, 1):
        color = (0, 165, 255)
        cv2.rectangle(overlay, (c.x, c.y), (c.x + c.w, c.y + c.h), color, 2)
        cx, cy = c.center
        cv2.circle(overlay, (cx, cy), 5, color, -1)
        cv2.putText(
            overlay,
            f"#{i} {c.confidence:.2f}",
            (c.x, c.y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

    if selected:
        color = (0, 255, 0)
        cv2.rectangle(
            overlay,
            (selected.x, selected.y),
            (selected.x + selected.w, selected.y + selected.h),
            color,
            4,
        )
        cx, cy = selected.center
        cv2.circle(overlay, (cx, cy), 8, color, -1)
        cv2.putText(
            overlay,
            f"SELECTED: ({cx},{cy})",
            (selected.x, selected.y - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    result = cv2.addWeighted(screenshot, 0.7, overlay, 0.3, 0)

    if output_path is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(config.OUTPUT_DIR, f"grounding_viz_{ts}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, result)
    print(f"  Grounding visualization saved: {output_path}")
    return output_path
