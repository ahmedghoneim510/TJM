import pyautogui
import time
import pygetwindow as gw
import os
import pyperclip  # pip install pyperclip
from utils.locate_notepad_utils import locate_notepad_icon
from utils.api_handler import fetch_posts

def open_notepad(x, y, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.doubleClick()
        time.sleep(1)
        windows = [w for w in gw.getWindowsWithTitle("Notepad")]
        if windows:
            win = windows[0]
            win.activate()
            return win
        attempt += 1
        time.sleep(0.5)
    raise Exception("فشل فتح Notepad بعد عدة محاولات")

def type_text_in_notepad(text):

    pyperclip.copy(text)
    print(text)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')  
    pyautogui.press('backspace')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v') 
    time.sleep(0.5)

def save_notepad_file(filename):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    save_dir = os.path.join(desktop, "tjm-project")
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.abspath(os.path.join(save_dir, filename))


    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            print(f"Removed existing file: {full_path}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Warning: Could not remove existing file {filename}: {e}")

    pyautogui.hotkey('ctrl', 's')
    time.sleep(2.0) 

    pyperclip.copy(full_path)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.0)
    pyautogui.press('enter')
    
    time.sleep(1.5)

    for _ in range(10):
        if os.path.exists(full_path):
            print(f"Verified: File saved successfully at {full_path}")
            return full_path
        time.sleep(0.5)
    
    print(f"Warning: File {filename} was not found after saving!")
    return full_path

def close_notepad():
    windows = [w for w in gw.getWindowsWithTitle("Notepad")]
    if windows:
        win = windows[0]
        win.activate()
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1)


