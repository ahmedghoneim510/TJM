import pyautogui
import time
import pygetwindow as gw

def open_notepad(x, y, max_attempts=5):
    """
    Double-click the given coordinates to open Notepad.
    Retry if Notepad window not detected.
    """
    attempt = 0
    while attempt < max_attempts:
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.doubleClick()
        print(f"Attempt {attempt+1}: Notepad launch clicked.")
        time.sleep(1)  # give time to open

        # Check if Notepad window exists
        notepad_windows = [w for w in gw.getWindowsWithTitle("Untitled - Notepad")]
        if notepad_windows:
            print("Notepad successfully opened!")
            return notepad_windows[0]  # return the window object if needed
        else:
            print("Notepad not detected yet. Retrying...")
            attempt += 1
            time.sleep(0.5)

    raise Exception("Failed to open Notepad after multiple attempts.")
