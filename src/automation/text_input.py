import time

import pyautogui
import pygetwindow as gw
import pyperclip

from .window_manager import ensure_notepad_focus


def type_text_in_notepad(text: str) -> None:
    """Paste text into Notepad via clipboard (more reliable than key-by-key typing)."""
    if not ensure_notepad_focus():
        raise RuntimeError("Notepad window not found or cannot be activated")

    windows = [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]
    if windows:
        win = windows[0]
        pyautogui.click(win.left + win.width // 2, win.top + win.height // 2)
    else:
        pyautogui.click()
    time.sleep(0.5)

    pyperclip.copy(text)
    time.sleep(0.3)

    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("delete")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.5)

    # Verify paste and retry once if clipboard changed
    if pyperclip.paste() != text:
        print("  Clipboard changed during paste — retrying...")
        pyperclip.copy(text)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.0)

    print(f"  Text pasted ({len(text)} chars)")
    time.sleep(0.5)
