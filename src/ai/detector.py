from .candidate_verifier import verify_and_rank_candidates
from .models import GroundingCandidate
from .proposal_generator import generate_proposals
from .visualization import visualize_grounding


def detect_notepad_with_ai(
    screenshot_path: str,
    debug: bool = True,
    save_visualization: bool = False,
    viz_path: str | None = None,
) -> tuple[int, int]:
    """
    Two-stage visual grounding: propose candidates then verify the best match.

    Args:
        screenshot_path:    Path to the desktop screenshot.
        debug:              Print stage-by-stage progress.
        save_visualization: Save an annotated screenshot of the grounding result.
        viz_path:           Where to save the visualization (auto-generated if None).

    Returns:
        (x, y) center pixel coordinates for clicking.

    Raises:
        ValueError: if the icon cannot be found or verified.
    """
    if debug:
        print("\n" + "=" * 60)
        print("TWO-STAGE VISUAL GROUNDING SYSTEM")
        print("=" * 60)

    candidates = generate_proposals(screenshot_path, debug=debug)
    if not candidates:
        raise ValueError("No proposals generated — Notepad icon not detected")

    best = verify_and_rank_candidates(screenshot_path, candidates, debug=debug)
    if best is None:
        raise ValueError("All candidates rejected — Notepad icon not verified")

    if save_visualization:
        visualize_grounding(screenshot_path, candidates, best, viz_path)

    x, y = best.center

    if debug:
        _log_result(best, x, y)

    return x, y


def _log_result(candidate: GroundingCandidate, x: int, y: int) -> None:
    print("\n" + "=" * 60)
    print(f"GROUNDING COMPLETE: Click at ({x}, {y})")
    print(
        f"  BBox: top-left=({candidate.x},{candidate.y}), "
        f"size=({candidate.w}x{candidate.h})"
    )
    print(f"  Confidence: {candidate.confidence:.2f}")
    print(f"  Source:     {candidate.source}")
    print("=" * 60 + "\n")
