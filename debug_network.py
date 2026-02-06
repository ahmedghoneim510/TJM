import requests
import sys
import os

print(f"Requests version: {requests.__version__}")
print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")

print("\nTesting HTTP (not HTTPS) connection to jsonplaceholder...")
try:
    response = requests.get("http://jsonplaceholder.typicode.com/posts", timeout=10)
    print(f"Status Code: {response.status_code}")
except Exception as e:
    print(f"HTTP request failed: {e}")

print("\nTesting connection to google.com...")
try:
    response = requests.get("https://www.google.com", timeout=10)
    print(f"Status Code: {response.status_code}")
except Exception as e:
    print(f"Google request failed: {e}")
