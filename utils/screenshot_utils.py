import os
import pyautogui

def take_screenshot(save_path=None):
    """
    Take a screenshot of the entire desktop.
    Saves to Desktop if save_path not provided.
    """
    screenshot = pyautogui.screenshot()

    if not save_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop, "desktop_screenshot.png")

    screenshot.save(save_path)
    print(f"Screenshot saved at {save_path}")
    return save_path
