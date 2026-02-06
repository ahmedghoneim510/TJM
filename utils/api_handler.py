import requests
import time
def fetch_posts(limit=10, retries=3, delay=1):
    url = "https://jsonplaceholder.typicode.com/posts"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Success on attempt {attempt}!")
            return response.json()[:limit]

        except requests.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print("\nNetwork request failed. Returning MOCK data.")
                # رجع بيانات وهمية عشان المشروع يشتغل
                return [{"id": i+1, "title": f"Mock Title {i+1}", "body": f"Mock Body {i+1}"} for i in range(limit)]
