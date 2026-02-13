"""Save Notepad files via the Save As dialog."""

import os
import time

import pyautogui
import pyperclip

from .window_manager import ensure_notepad_focus

# Save directory
SAVE_DIR = r"C:\Users\hp\Desktop\tjm-project"


def save_notepad_file(filename):
    """Save Notepad file to SAVE_DIR with handling of existing files."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Build the full path
    full_path = os.path.join(SAVE_DIR, filename)

    # Handle existing filename by adding number suffix
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(full_path):
        new_filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(SAVE_DIR, new_filename)
        counter += 1
        if counter > 100:
            print(f"⚠️  Too many existing files, overwriting {filename}")
            full_path = os.path.join(SAVE_DIR, filename)
            break

    if counter > 1:
        print(f"ℹ️  File exists, saving as: {os.path.basename(full_path)}")

    full_path = os.path.abspath(full_path)
    print(f"💾 Saving to: {full_path}")

    if not ensure_notepad_focus():
        raise Exception("Notepad window not found or cannot be activated")

    # Open Save As dialog
    pyautogui.hotkey("ctrl", "shift", "s")
    time.sleep(1)

    # Paste the full path into the filename field
    pyperclip.copy(full_path)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)

    # Press Enter to save
    pyautogui.press("enter")
    time.sleep(2.0)

    # Handle "file already exists - replace?" dialog
    try:
        pyautogui.press("left")
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(1.0)
    except Exception:
        pass

    # Verify file was saved
    for _ in range(20):
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(
                f"✓ File saved successfully: {os.path.basename(full_path)} "
                f"({file_size} bytes)"
            )
            print(f"   Location: {full_path}")
            return full_path
        time.sleep(0.5)

    print("❌ Warning: File not found after save attempt!")
    print(f"   Expected location: {full_path}")
    raise Exception(f"File save verification failed for: {filename}")
