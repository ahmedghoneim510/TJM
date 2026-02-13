"""Notepad window management: open, close, focus."""

import time

import pyautogui
import pygetwindow as gw


def ensure_notepad_focus():
    """Ensure Notepad window has focus before performing actions."""
    windows = [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]
    if windows:
        try:
            windows[0].activate()
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"⚠️  Could not activate Notepad: {e}")
            return False
    print("⚠️  No Notepad window found!")
    return False


def open_notepad(x, y, max_attempts=5):
    """Open Notepad by double-clicking at (x, y) and ensure it has focus."""
    attempt = 0
    while attempt < max_attempts:
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.doubleClick()
        time.sleep(2)

        # Find Notepad window
        windows = [
            w
            for w in gw.getAllWindows()
            if "notepad" in w.title.lower() and "untitled" in w.title.lower()
        ]
        if not windows:
            windows = [w for w in gw.getWindowsWithTitle("Notepad")]

        if windows:
            win = windows[0]
            try:
                win.activate()
                time.sleep(1)
                win.maximize()
                time.sleep(0.5)
                print(f"✓ Notepad window activated: {win.title}")
                return win
            except Exception as e:
                print(f"⚠️  Window activation warning: {e}")
                return win

        attempt += 1
        print(f"⏳ Waiting for Notepad to open... (attempt {attempt}/{max_attempts})")
        time.sleep(1)

    raise Exception("Failed to open Notepad after multiple attempts")


def close_notepad():
    """Close Notepad window. If unsaved changes prompt appears, click Save."""
    windows = [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]
    if windows:
        win = windows[0]
        try:
            win.activate()
            time.sleep(0.5)
        except Exception:
            pass

        pyautogui.hotkey("alt", "F4")
        time.sleep(1.5)

        # Check if Notepad is still open (unsaved changes dialog)
        remaining = [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]
        if remaining:
            # "Save" button is focused by default — press Enter
            pyautogui.press("enter")
            time.sleep(2.0)

            # If a Save As dialog appeared, confirm it
            still_open = [
                w for w in gw.getAllWindows() if "notepad" in w.title.lower()
            ]
            if still_open:
                pyautogui.press("enter")
                time.sleep(1.0)

        print("✓ Notepad closed")
    else:
        print("ℹ️  No Notepad window found to close")
