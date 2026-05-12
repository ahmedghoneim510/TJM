from .icon_locator import locate_notepad_icon
from .window_manager import open_notepad, close_notepad, ensure_notepad_focus
from .text_input import type_text_in_notepad
from .file_saver import save_notepad_file
from .screenshot import take_screenshot

__all__ = [
    "locate_notepad_icon",
    "open_notepad",
    "close_notepad",
    "ensure_notepad_focus",
    "type_text_in_notepad",
    "save_notepad_file",
    "take_screenshot",
]
