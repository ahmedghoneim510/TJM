"""Debug visualization for grounding results."""

import os
import datetime
from typing import List, Optional

import cv2

from .models import GroundingCandidate


def visualize_grounding(
    screenshot_path: str,
    candidates: List[GroundingCandidate],
    selected: Optional[GroundingCandidate],
    output_path: str = None,
) -> str:
    """
    Create annotated screenshot showing grounding proposals and final selection.
    Useful for debugging and demonstration.

    Returns: path to saved visualization
    """
    screenshot = cv2.imread(screenshot_path)
    overlay = screenshot.copy()

    # Draw all candidates
    for i, candidate in enumerate(candidates, 1):
        color = (0, 165, 255)  # Orange for proposals
        thickness = 2

        cv2.rectangle(
            overlay,
            (candidate.x, candidate.y),
            (candidate.x + candidate.w, candidate.y + candidate.h),
            color,
            thickness,
        )

        cx, cy = candidate.center
        cv2.circle(overlay, (cx, cy), 5, color, -1)

        label = f"#{i} {candidate.confidence:.2f}"
        label_pos = (candidate.x, candidate.y - 10)
        cv2.putText(
            overlay, label, label_pos,
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2,
        )

    # Highlight selected candidate
    if selected:
        color = (0, 255, 0)  # Green for selection
        thickness = 4

        cv2.rectangle(
            overlay,
            (selected.x, selected.y),
            (selected.x + selected.w, selected.y + selected.h),
            color,
            thickness,
        )

        cx, cy = selected.center
        cv2.circle(overlay, (cx, cy), 8, color, -1)

        label = f"SELECTED: ({cx},{cy})"
        label_pos = (selected.x, selected.y - 30)
        cv2.putText(
            overlay, label, label_pos,
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2,
        )

    # Blend overlay
    result = cv2.addWeighted(screenshot, 0.7, overlay, 0.3, 0)

    # Save visualization
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Get project root (2 levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(project_root, "output")
        output_path = os.path.join(output_dir, f"grounding_viz_{timestamp}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, result)

    print(f"📸 Grounding visualization saved to: {output_path}")
    return output_path
