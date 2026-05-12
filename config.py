import os
from dotenv import load_dotenv

load_dotenv()

# --- Gemini AI ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_PRIMARY_MODEL: str = "gemini-2.0-flash"
GEMINI_FALLBACK_MODEL: str = "gemini-1.5-flash"

# --- Posts API ---
POSTS_API_URL: str = "https://jsonplaceholder.typicode.com/posts"
API_TIMEOUT: int = 10
API_RETRIES: int = 3
API_RETRY_DELAY: float = 1.0

# --- App behaviour ---
MAX_POSTS: int = int(os.getenv("MAX_POSTS", "10"))
ENABLE_VISUALIZATION: bool = os.getenv("ENABLE_VISUALIZATION", "true").lower() == "true"

# --- File saving ---
SAVE_DIR: str = os.getenv(
    "SAVE_DIR",
    os.path.join(os.path.expanduser("~"), "Desktop", "tjm-project"),
)

# --- Paths ---
_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR: str = os.path.join(_ROOT, "output")
SCREENSHOT_PATH: str = os.path.join(OUTPUT_DIR, "screenshot.png")

# --- Icon location ---
ICON_TEMPLATE_PATHS: list = [
    os.path.join(_ROOT, "assets", "notepad_icon.png"),
    os.path.join(_ROOT, "assets", "notepad_template.png"),
    os.path.join(_ROOT, "assets", "notepad.png"),
]
MAX_LOCATION_ATTEMPTS: int = 3
