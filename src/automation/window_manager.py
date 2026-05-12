import time

import pyautogui
import pygetwindow as gw


# ── helpers ──────────────────────────────────────────────────────────────────

def _notepad_windows() -> list:
    return [w for w in gw.getAllWindows() if "notepad" in w.title.lower()]


def ensure_notepad_focus() -> bool:
    windows = _notepad_windows()
    if not windows:
        print("  No Notepad window found!")
        return False
    try:
        windows[0].activate()
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"  Could not activate Notepad: {e}")
        return False


# ── public API ────────────────────────────────────────────────────────────────

def open_notepad(x: int, y: int, max_attempts: int = 5):
    """
    Double-click (x, y) to launch Notepad, then verify the window title appears.
    Raises RuntimeError if Notepad does not open within max_attempts tries.
    """
    for attempt in range(1, max_attempts + 1):
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.doubleClick()
        time.sleep(2)

        # Accept any window that has "notepad" in its title
        windows = _notepad_windows()

        if windows:
            win = windows[0]
            try:
                win.activate()
                time.sleep(0.8)
                win.maximize()
                time.sleep(0.5)
                print(f"  Notepad launched: '{win.title}'")
            except Exception as e:
                print(f"  Window activation warning: {e}")
            return win

        print(f"  Waiting for Notepad to open… (attempt {attempt}/{max_attempts})")
        time.sleep(1)

    raise RuntimeError(
        "Notepad did not open after multiple attempts. "
        "Verify the icon was double-clicked correctly."
    )


def close_notepad() -> None:
    """
    Close Notepad.

    After a successful Save-As there should be no unsaved-changes dialog.
    We still handle it gracefully in case something went wrong during saving.
    """
    windows = _notepad_windows()
    if not windows:
        print("  No Notepad window to close")
        return

    try:
        windows[0].activate()
        time.sleep(0.3)
    except Exception:
        pass

    pyautogui.hotkey("alt", "F4")
    time.sleep(1.5)

    # If a "save changes?" dialog appeared (shouldn't happen after a successful save)
    # the default-focused button is "Save" — pressing Enter confirms it.
    if _notepad_windows():
        pyautogui.press("enter")
        time.sleep(2.0)

        # Handle any follow-up Save-As dialog
        if _notepad_windows():
            pyautogui.press("enter")
            time.sleep(1.0)

    print("  Notepad closed")
