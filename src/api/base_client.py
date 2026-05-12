import time
import requests


class BaseAPIClient:
    base_url: str = ""
    timeout: int = 10
    retries: int = 3
    retry_delay: float = 1.0

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    def _get(self, path: str = "", params: dict | None = None):
        url = self.base_url.rstrip("/")
        if path:
            url = f"{url}/{path.lstrip('/')}"

        for attempt in range(1, self.retries + 1):
            try:
                response = requests.get(
                    url,
                    headers=self._headers,
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                print(f"  Request succeeded on attempt {attempt}")
                return response.json()
            except requests.RequestException as e:
                print(f"  Attempt {attempt}/{self.retries} failed: {e}")
                if attempt < self.retries:
                    time.sleep(self.retry_delay)
                else:
                    raise
