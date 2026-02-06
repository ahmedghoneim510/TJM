from utils.screenshot_utils import take_screenshot
from utils.icon_detection import find_icon_by_template, IconNotFoundError
import os
import time
def locate_notepad_icon(max_attempts=3, wait_time=1, debug=True):
    """
    Try to locate the Notepad icon on Desktop with retry logic.
    Returns: (x, y) center coordinates if found.
    Raises: Exception if not found after retries.
    """
    template_path = os.path.join("assets", "notepad_icon.png")

    for attempt in range(1, max_attempts + 1):
        try:
            screenshot_path = take_screenshot()
            x, y = find_icon_by_template(screenshot_path, template_path, threshold=0.8, debug=debug)
            print(f"Notepad icon found at ({x}, {y}) on attempt {attempt}")
            return x, y
        except IconNotFoundError as e:
            print(f"Attempt {attempt}: {e}")
            time.sleep(wait_time)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            break

    raise Exception("Notepad icon could not be located after multiple attempts.")