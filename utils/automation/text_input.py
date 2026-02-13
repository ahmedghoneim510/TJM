"""Text input into Notepad using clipboard paste."""

import time

import pyautogui
import pygetwindow as gw
import pyperclip

from .window_manager import ensure_notepad_focus


def type_text_in_notepad(text):
    """Type text into Notepad using clipboard (more reliable than typing)."""
    print(f"📝 Text to type ({len(text)} chars):")
    print(f"   {text[:100]}..." if len(text) > 100 else f"   {text}")

    if not ensure_notepad_focus():
        raise Exception("Notepad window not found or cannot be activated")

    # Click in the center of the Notepad window's text area
    windows = [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]
    if windows:
        win = windows[0]
        center_x = win.left + win.width // 2
        center_y = win.top + win.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
    else:
        pyautogui.click()
        time.sleep(0.5)

    # Copy text to clipboard
    pyperclip.copy(text)
    time.sleep(0.5)

    # Clear existing text and paste
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.press("delete")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.5)

    # Verify text was pasted
    pasted = pyperclip.paste()
    if pasted == text:
        print(f"✓ Text pasted successfully ({len(text)} chars)")
    else:
        print("⚠️  Warning: Clipboard content may have changed, retrying paste...")
        pyperclip.copy(text)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.0)
        print("✓ Retry paste completed")

    time.sleep(0.5)
