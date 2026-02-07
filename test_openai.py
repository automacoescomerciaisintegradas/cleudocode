import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: 
        print("No OpenAI Key")
        return
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "hi"}]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"OpenAI Status: {resp.status_code}")
        print(f"OpenAI Body: {resp.text}")
    except Exception as e:
        print(f"OpenAI Exception: {e}")

if __name__ == "__main__":
    query_openai()
