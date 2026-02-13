"""Main entry point: Two-stage visual grounding system for Notepad icon detection."""

import os

import cv2

from .models import GroundingCandidate
from .proposal_generator import generate_proposals
from .candidate_verifier import verify_and_rank_candidates


def detect_notepad_with_ai(screenshot_path: str, debug: bool = True) -> tuple:
    """
    Two-stage visual grounding system for robust Notepad icon detection.

    Stage 1: Generate candidate regions (proposals) with bounding boxes
    Stage 2: Verify and rank candidates, select best match

    Returns: (x, y) center coordinates for clicking
    Raises: ValueError if icon not found
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    if debug:
        print("\n" + "=" * 60)
        print("TWO-STAGE VISUAL GROUNDING SYSTEM")
        print("=" * 60)

    try:
        # STAGE 1: Generate candidate proposals
        candidates = generate_proposals(screenshot_path, api_key, debug)

        if not candidates:
            if debug:
                print("\n❌ No candidates generated in Stage 1")
            raise ValueError("Notepad icon not detected - no proposals generated")

        # STAGE 2: Verify and select best candidate
        best_candidate = verify_and_rank_candidates(
            screenshot_path, candidates, api_key, debug
        )

        if best_candidate is None:
            if debug:
                print("\n❌ No candidates verified in Stage 2")
            raise ValueError("Notepad icon not verified - all candidates rejected")

        # Return center coordinates for clicking
        x, y = best_candidate.center

        if debug:
            _print_result(best_candidate, x, y, screenshot_path)

        return x, y

    except Exception as e:
        if debug:
            print(f"\n❌ Grounding failed: {e}")
        raise ValueError(f"Visual grounding failed: {e}")


def _print_result(
    candidate: GroundingCandidate, x: int, y: int, screenshot_path: str
) -> None:
    """Print grounding result and save debug visualization."""
    print("\n" + "=" * 60)
    print(f"✓ GROUNDING COMPLETE: Click at ({x}, {y})")
    print(
        f"  BBox: top-left=({candidate.x},{candidate.y}), "
        f"size=({candidate.w}x{candidate.h})"
    )
    print(f"  Confidence: {candidate.confidence:.2f}")
    print(f"  Source: {candidate.source}")

    # Save a quick debug marker on screenshot
    try:
        debug_img = cv2.imread(screenshot_path)
        if debug_img is not None:
            cv2.drawMarker(
                debug_img, (x, y), (0, 0, 255), cv2.MARKER_CROSS, 40, 3
            )
            cv2.rectangle(
                debug_img,
                (candidate.x, candidate.y),
                (candidate.x + candidate.w, candidate.y + candidate.h),
                (0, 255, 0),
                2,
            )
            debug_path = screenshot_path.replace(".png", "_debug_click.png")
            cv2.imwrite(debug_path, debug_img)
            print(f"  📸 Debug click preview saved: {debug_path}")
    except Exception:
        pass

    print("=" * 60 + "\n")
