import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_ollama():
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
    print(f"Testing Ollama at {host}...")
    try:
        resp = requests.get(f"{host}/api/tags", timeout=5)
        print(f"Ollama tags: {resp.status_code}")
        return True
    except Exception as e:
        print(f"Ollama failed: {e}")
        return False

def test_anthropic():
    key = os.getenv("ANTHROPIC_API_KEY")
    print(f"Testing Anthropic Key (exists: {bool(key)})...")
    if not key: return False
    # Just a small metadata check or similar would be better, but let's just check if we can reach the API
    try:
        # We won't do a full query to save tokens, but we can check the URL
        resp = requests.get("https://api.anthropic.com/v1/messages", headers={"x-api-key": key}, timeout=5)
        print(f"Anthropic response status: {resp.status_code} (expect 405/401 since it's GET)")
        return resp.status_code != 404
    except Exception as e:
        print(f"Anthropic reachability failed: {e}")
        return False

if __name__ == "__main__":
    test_ollama()
    test_anthropic()
