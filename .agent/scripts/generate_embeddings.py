from ollama import Client
import json
import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

# Configuration
JSONL_FILE = r".agent\embeddings\skills.jsonl"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # Default Ollama host

def generate_embeddings():
    if not os.path.exists(JSONL_FILE):
        print(f"JSONL file not found at {JSONL_FILE}. Please run process_skills.py first.")
        return

    print(f"Connecting to Ollama at {OLLAMA_HOST}...")
    try:
        client = Client(host=OLLAMA_HOST)
    except Exception as e:
        print(f"Failed to create Ollama client: {e}")
        return

    print("Generating embeddings...")
    count = 0
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Example: Just reading and printing one to show it works, 
    # normally you'd save this to a vector DB.
    # For this script, we'll just verify we can generate them.
    
    for line in lines:
        try:
            item = json.loads(line)
            response = client.embeddings(
                model=EMBEDDING_MODEL,
                prompt=item["text"]
            )
            embedding = response.get('embedding')
            if embedding:
                # Upsert into Qdrant collection "skills"
                point = PointStruct(id=item["id"], vector=embedding, payload=item["metadata"])
                qdrant.upsert(collection_name="skills", points=[point])
                print(f"Generated and upserted embedding for {item['id']} (dim: {len(embedding)})")
                count += 1
            else:
                print(f"No embedding returned for {item['id']}")
        except Exception as e:
            print(f"Error processing {item.get('id', 'unknown')}: {e}")
            
    print(f"Successfully generated {count} embeddings.")
    print("Next step: Insert these into your Vector DB (e.g., Qdrant).")

if __name__ == "__main__":
    generate_embeddings()
