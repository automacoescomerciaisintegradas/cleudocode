import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_anthropic():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "hi"}]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Anthropic Status: {resp.status_code}")
        print(f"Anthropic Body: {resp.text}")
    except Exception as e:
        print(f"Anthropic Exception: {e}")

if __name__ == "__main__":
    query_anthropic()
