import pyautogui
import time
import pygetwindow as gw
import os
import pyperclip  # pip install pyperclip

# Save directory: C:\Users\hp\Desktop\tjm-project
SAVE_DIR = r"C:\Users\hp\Desktop\tjm-project"


def ensure_notepad_focus():
    """Ensure Notepad window has focus before performing actions."""
    windows = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower()]
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
    """Open Notepad and ensure it has focus."""
    attempt = 0
    while attempt < max_attempts:
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.doubleClick()
        time.sleep(2)  # Increased wait time for Notepad to open
        
        # Find Notepad window
        windows = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower() and 'untitled' in w.title.lower()]
        if not windows:
            windows = [w for w in gw.getWindowsWithTitle("Notepad")]
        
        if windows:
            win = windows[0]
            try:
                win.activate()
                time.sleep(1)  # Wait for activation
                win.maximize()  # Maximize for better visibility
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

def type_text_in_notepad(text):
    """Type text into Notepad using clipboard (more reliable than typing)."""
    print(f"📝 Text to type ({len(text)} chars):")
    print(f"   {text[:100]}..." if len(text) > 100 else f"   {text}")
    
    # Ensure Notepad has focus
    if not ensure_notepad_focus():
        raise Exception("Notepad window not found or cannot be activated")
    
    # Click in the CENTER of the Notepad window's text area to ensure focus
    windows = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower()]
    if windows:
        win = windows[0]
        # Click in the center of the Notepad window (text area)
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
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.press('delete')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.5)  # Wait for paste to complete
    
    # Verify text was pasted (check clipboard still has it)
    pasted = pyperclip.paste()
    if pasted == text:
        print(f"✓ Text pasted successfully ({len(text)} chars)")
    else:
        print(f"⚠️  Warning: Clipboard content may have changed, retrying paste...")
        # Retry paste
        pyperclip.copy(text)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)
        print(f"✓ Retry paste completed")
    
    time.sleep(0.5)

def save_notepad_file(filename):
    """Save Notepad file to C:\\Users\\hp\\Desktop\\tjm-project with handling of existing files."""
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
        if counter > 100:  # Safety limit
            print(f"⚠️  Too many existing files, overwriting {filename}")
            full_path = os.path.join(SAVE_DIR, filename)
            break
    
    if counter > 1:
        print(f"ℹ️  File exists, saving as: {os.path.basename(full_path)}")
    
    full_path = os.path.abspath(full_path)
    print(f"💾 Saving to: {full_path}")
    
    # Ensure Notepad has focus
    if not ensure_notepad_focus():
        raise Exception("Notepad window not found or cannot be activated")
    
    # Open Save As dialog with Ctrl+Shift+S (ensures Save As even if file was saved before)
    pyautogui.hotkey('ctrl', 'shift', 's')
    time.sleep(3)  # Wait for Save As dialog to fully open
    
    # Navigate to the filename field - paste the full path
    pyperclip.copy(full_path)
    time.sleep(0.3)
    
    # In the filename field: select all and paste the full path
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.0)
    
    # Press Enter to save
    pyautogui.press('enter')
    time.sleep(2.0)  # Wait for file to save
    
    # Handle "file already exists - replace?" dialog (if it appears)
    try:
        pyautogui.press('left')   # Select 'Yes' button
        time.sleep(0.2)
        pyautogui.press('enter')  # Confirm overwrite
        time.sleep(1.0)
    except:
        pass
    
    # Verify file was saved
    for attempt in range(20):  # Check for 10 seconds
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✓ File saved successfully: {os.path.basename(full_path)} ({file_size} bytes)")
            print(f"   Location: {full_path}")
            return full_path
        time.sleep(0.5)
    
    print(f"❌ Warning: File not found after save attempt!")
    print(f"   Expected location: {full_path}")
    raise Exception(f"File save verification failed for: {filename}")

def close_notepad():
    """Close Notepad window. If unsaved changes prompt appears, click Save."""
    windows = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower()]
    if windows:
        win = windows[0]
        try:
            win.activate()
            time.sleep(0.5)
        except:
            pass
        
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1.5)
        
        # Check if Notepad is still open (unsaved changes dialog may have appeared)
        remaining = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower()]
        if remaining:
            # "Do you want to save?" dialog is showing - press Save (Enter)
            # The "Save" button is already focused by default, just press Enter
            pyautogui.press('enter')
            time.sleep(2.0)
            
            # If a Save As dialog appeared (first-time save), handle it
            still_open = [w for w in gw.getAllWindows() if 'notepad' in w.title.lower()]
            if still_open:
                # May be a Save As dialog - press Enter to confirm
                pyautogui.press('enter')
                time.sleep(1.0)
        
        print("✓ Notepad closed")
    else:
        print("ℹ️  No Notepad window found to close")


