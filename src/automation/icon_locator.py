import os
from time import sleep

import config
from ..ai.detector import detect_notepad_with_ai
from .screenshot import take_screenshot
from .template_matcher import find_icon_by_template, IconNotFoundError


def locate_notepad_icon(
    max_attempts: int = config.MAX_LOCATION_ATTEMPTS,
    wait_time: float = 1.0,
    debug: bool = True,
    save_visualization: bool = config.ENABLE_VISUALIZATION,
) -> tuple[int, int]:
    """
    Locate the Notepad icon using AI visual grounding with template-matching fallback.

    Takes a fresh screenshot each call so the icon's current position is always used —
    important when the icon may have been moved between iterations.

    Returns (x, y) center coordinates ready for clicking.
    Raises RuntimeError if all attempts fail.
    """
    for attempt in range(1, max_attempts + 1):
        screenshot_path = None
        try:
            screenshot_path = take_screenshot()

            # viz_path=None → visualize_grounding auto-generates a timestamped filename,
            # preserving every annotated screenshot across the whole run.
            x, y = detect_notepad_with_ai(
                screenshot_path,
                debug=debug,
                save_visualization=save_visualization,
            )

            print(f"  Icon found at ({x}, {y}) — attempt {attempt}/{max_attempts}")
            return x, y

        except Exception as e:
            print(f"  Attempt {attempt}/{max_attempts} failed: {e}")

            if attempt == max_attempts and screenshot_path:
                result = _try_template_fallback(screenshot_path, debug)
                if result is not None:
                    return result

            if attempt < max_attempts:
                sleep(wait_time)

    raise RuntimeError(
        f"Notepad icon could not be located after {max_attempts} attempts. "
        "Ensure the Notepad icon is visible on the desktop."
    )


def _try_template_fallback(
    screenshot_path: str,
    debug: bool,
) -> tuple[int, int] | None:
    if debug:
        print("\n  Attempting template-matching fallback...")

    for template_path in config.ICON_TEMPLATE_PATHS:
        if not os.path.exists(template_path):
            continue
        try:
            x, y = find_icon_by_template(screenshot_path, template_path, threshold=0.7)
            print(f"  Found via template matching at ({x}, {y})")
            return x, y
        except IconNotFoundError as e:
            if debug:
                print(f"    {template_path}: {e}")
        except Exception as e:
            if debug:
                print(f"    Template error: {e}")

    if debug:
        print("  Template matching also failed.")
        print("\n  Tips:")
        print("    1. Ensure Notepad icon is visible on the desktop")
        print("    2. Check your internet connection (AI requires it)")
        print("    3. Add a Notepad icon template to assets/notepad_icon.png")

    return None
