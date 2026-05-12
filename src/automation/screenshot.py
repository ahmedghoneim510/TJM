import os
import time

import pyautogui

import config


def take_screenshot(save_path: str = config.SCREENSHOT_PATH) -> str:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    pyautogui.hotkey("win", "d")
    time.sleep(0.5)
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)
    return save_path
