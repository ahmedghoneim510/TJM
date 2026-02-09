from utils.screenshot_utils import take_screenshot
from utils.ai_vision_detector import detect_notepad_with_ai
from time import sleep


def locate_notepad_icon(max_attempts=3, wait_time=1, debug=True):
    """
    Try to locate the Notepad icon on Desktop using AI vision with retry logic.
    Returns: (x, y) center coordinates if found.
    Raises: Exception if not found after retries.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            screenshot_path = take_screenshot()
            x, y = detect_notepad_with_ai(screenshot_path, debug=debug)
            print(f"Notepad icon found at ({x}, {y}) on attempt {attempt}")
            return x, y
        except ValueError as e:
            print(f"Attempt {attempt}: {e}")
            sleep(wait_time)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            break

    raise Exception("Notepad icon could not be located after multiple attempts.")