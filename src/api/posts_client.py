import config
from .base_client import BaseAPIClient


class PostsClient(BaseAPIClient):
    base_url = config.POSTS_API_URL
    timeout = config.API_TIMEOUT
    retries = config.API_RETRIES
    retry_delay = config.API_RETRY_DELAY

    def get_posts(self, limit: int = config.MAX_POSTS) -> list[dict]:
        try:
            posts = self._get()
            return posts[:limit]
        except Exception as e:
            print(f"\n  Network request failed: {e}")
            print("  Returning mock data to ensure continuity.")
            return [
                {
                    "id": i + 1,
                    "title": f"Mock Title {i + 1}",
                    "body": f"Mock body content for post {i + 1}.",
                }
                for i in range(limit)
            ]
