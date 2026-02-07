import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_zai():
    api_key = os.getenv("ZAI_API_KEY")
    base_url = os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/anthropic").rstrip('/')
    url = f"{base_url}/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": os.getenv("ZAI_MODEL", "glm-4-32b-0414-128k"),
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "hi"}]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"ZAI Status: {resp.status_code}")
        print(f"ZAI Body: {resp.text}")
    except Exception as e:
        print(f"ZAI Exception: {e}")

if __name__ == "__main__":
    query_zai()
