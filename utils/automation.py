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
    # النسخ واللصق لضمان كتابة صحيحة
    pyperclip.copy(text)
    print(text)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')  # مسح أي نص موجود
    pyautogui.press('backspace')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')  # لصق النص
    time.sleep(0.5)

def save_notepad_file(filename):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    save_dir = os.path.join(desktop, "tjm-project")
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.abspath(os.path.join(save_dir, filename))

    # فتح نافذة الحفظ
    pyautogui.hotkey('ctrl', 's')
    time.sleep(1.5)

    # تنظيف خانة الاسم وكتابة المسار
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    time.sleep(0.3)
    pyautogui.write(full_path, interval=0.01)
    time.sleep(1.5)
    pyautogui.press('enter')

    # تأكيد الاستبدال لو الملف موجود
    time.sleep(1)
    pyautogui.press('left')  # اختيار Yes
    pyautogui.press('enter')
    time.sleep(0.5)

    print(f"Saved file: {full_path}")
    return full_path

def close_notepad():
    windows = [w for w in gw.getWindowsWithTitle("Notepad")]
    if windows:
        win = windows[0]
        win.activate()
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1)

# ---------- Main Script ----------
