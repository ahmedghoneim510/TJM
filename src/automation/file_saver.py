import os
import time

import pyautogui
import pyperclip

import config
from .window_manager import ensure_notepad_focus


def save_notepad_file(filename: str, save_dir: str = config.SAVE_DIR) -> str:
    """Open Ctrl+Shift+S, type the full path, and verify the file exists."""
    os.makedirs(save_dir, exist_ok=True)

    full_path = _unique_path(save_dir, filename)
    print(f"  Saving to: {full_path}")

    if not ensure_notepad_focus():
        raise RuntimeError("Notepad window not found or cannot be activated")

    pyautogui.hotkey("ctrl", "shift", "s")
    time.sleep(1)

    pyperclip.copy(full_path)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)
    pyautogui.press("enter")
    time.sleep(2.0)

    # Handle "replace file?" dialog
    try:
        pyautogui.press("left")
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(1.0)
    except Exception:
        pass

    # Wait for file to appear on disk (max 10 s)
    for _ in range(20):
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"  Saved: {os.path.basename(full_path)} ({size} bytes)")
            return full_path
        time.sleep(0.5)

    raise RuntimeError(f"File save verification failed — expected: {full_path}")


def _unique_path(directory: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(candidate) and counter <= 100:
        candidate = os.path.join(directory, f"{base}_{counter}{ext}")
        counter += 1
    return os.path.abspath(candidate)
