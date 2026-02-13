"""
Notepad automation - window management, text input, file saving.

Modules:
    window_manager  - Open, close, and focus Notepad windows
    text_input      - Type/paste text into Notepad
    file_saver      - Save files via Save As dialog
"""

from .window_manager import open_notepad, close_notepad, ensure_notepad_focus
from .text_input import type_text_in_notepad
from .file_saver import save_notepad_file, SAVE_DIR

__all__ = [
    "open_notepad",
    "close_notepad",
    "ensure_notepad_focus",
    "type_text_in_notepad",
    "save_notepad_file",
    "SAVE_DIR",
]
