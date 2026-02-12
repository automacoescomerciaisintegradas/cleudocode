
import sys
import os
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import Orchestrator

def main():
    print("Initializing Orchestrator...")
    try:
        orch = Orchestrator()
        print("Orchestrator initialized.")
        
        msg = {"text": "Hello! Are you online?", "from": "debug_script"}
        print(f"Sending message: {msg}")
        
        response = orch.receive_message(msg)
        print("Response received:")
        print(response)
        
    except Exception as e:
        print("ERROR:")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
