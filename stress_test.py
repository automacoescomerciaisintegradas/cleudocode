import requests
import threading
import time
import json

BASE_URL = "http://127.0.0.1:8501"
CONCURRENT_REQUESTS = 5
TOTAL_TESTS = 10

def send_chat_request(request_id):
    payload = {
        "message": f"Stress test message {request_id}. Please respond with a short verification code."
    }
    start_time = time.time()
    try:
        print(f"[Req {request_id}] Sending...")
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"[Req {request_id}] Success in {end_time - start_time:.2f}s: {data.get('response')[:50]}...")
        else:
            print(f"[Req {request_id}] Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Req {request_id}] Error: {e}")

def run_stress_test():
    print(f"Starting Stress Test: {CONCURRENT_REQUESTS} concurrent requests, totaling {TOTAL_TESTS}")
    threads = []
    for i in range(TOTAL_TESTS):
        t = threading.Thread(target=send_chat_request, args=(i+1,))
        threads.append(t)
        t.start()
        
        # Small delay to prevent instant saturation of the Flask dev server
        if (i+1) % CONCURRENT_REQUESTS == 0:
            time.sleep(2)

    for t in threads:
        t.join()
    print("Stress Test Completed.")

if __name__ == "__main__":
    run_stress_test()
