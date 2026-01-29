import os
import json
import re

SOURCE_DIR = r".agent\skills"
OUTPUT_DIR = r".agent\embeddings"
COMBINED_FILE = os.path.join(SOURCE_DIR, "_combined.md")
JSONL_FILE = os.path.join(OUTPUT_DIR, "skills.jsonl")

def ensure_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def sanitize_content(content):
    # Remove code blocks (non-greedy)
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # Remove inline code backticks
    content = content.replace('`', '')
    # Remove images
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    # Remove multiple newlines/spaces
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def create_combined_md():
    print(f"Generating {COMBINED_FILE}...")
    with open(COMBINED_FILE, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(SOURCE_DIR):
            for file in files:
                if file.endswith(".md") and file != "_combined.md":
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(f"\n\n--- FILE: {filepath} ---\n\n")
                            outfile.write(content)
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")

def create_jsonl():
    print(f"Generating {JSONL_FILE}...")
    with open(JSONL_FILE, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(SOURCE_DIR):
            for file in files:
                if file.endswith(".md") and file != "_combined.md":
                    filepath = os.path.join(root, file)
                    filename = os.path.splitext(file)[0]
                    category = os.path.basename(root)
                    
                    # If file is in the root of skills, category is 'root' or similar
                    if os.path.abspath(root) == os.path.abspath(SOURCE_DIR):
                        category = "core"
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            raw_content = infile.read()
                        
                        sanitized_text = sanitize_content(raw_content)
                        
                        # ID creation
                        id_str = f"skill_{category}_{filename}".lower()
                        id_str = re.sub(r'[^a-z0-9_]', '', id_str)
                        
                        record = {
                            "id": id_str,
                            "text": sanitized_text,
                            "metadata": {
                                "source": "antigravity-awesome-skills",
                                "type": "skill",
                                "category": category,
                                "path": filepath,
                                "title": filename
                            }
                        }
                        
                        outfile.write(json.dumps(record) + '\n')
                        
                    except Exception as e:
                        print(f"Error filtering {filepath}: {e}")

if __name__ == "__main__":
    ensure_dirs()
    create_combined_md()
    create_jsonl()
    print("Done processing skills.")
