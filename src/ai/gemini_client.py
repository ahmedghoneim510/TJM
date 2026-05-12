from google import genai
import config

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found — set it in your .env file")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client
