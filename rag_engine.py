import os
import requests
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import uuid

# Configurações Defaults (serão sobrescritas pelo .env se carregadas lá fora, mas garantimos aqui)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b") # Usamos o mesmo modelo para chat e embedding se possível, ou um específico
COLLECTION_NAME = "llmp2p_memory"

class RAGBrain:
    def __init__(self):
        # ChromaDB Persistente na pasta 'memory_db'
        self.client = chromadb.PersistentClient(path="memory_db")
        
        # Como o Chroma não tem func nativa para Ollama, faremos manual ou usaremos requests simples
        # vamos criar uma collection. Nota: Chroma requer uma embedding function por padrão.
        # Vamos implementar uma classe customizada simples para o Ollama.
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Cosine similarity é bom para texto
        )
        
    def _generate_embedding(self, text):
        """Gera embedding usando a API do Ollama"""
        url = f"{OLLAMA_HOST}/api/embeddings"
        payload = {
            "model": MODEL,
            "prompt": text
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data["embedding"]
            else:
                print(f"Erro no Embedding: {response.text}")
                return None
        except Exception as e:
            print(f"Exceção no Embedding: {e}")
            return None

    def add_document(self, content, filename, doc_type):
        """Processa e adiciona documento à memória"""
        # 1. Chunking simples (por parágrafos ou tamanho fixo)
        # Vamos usar tamanho fixo com overlap para garantir contexto
        CHUNK_SIZE = 1000
        OVERLAP = 100
        
        chunks = []
        for i in range(0, len(content), CHUNK_SIZE - OVERLAP):
            chunk = content[i : i + CHUNK_SIZE]
            chunks.append(chunk)
            
        print(f"Processando {len(chunks)} chunks para {filename}...")
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for idx, chunk in enumerate(chunks):
            vector = self._generate_embedding(chunk)
            if vector:
                ids.append(f"{filename}_{idx}_{uuid.uuid4().hex[:8]}")
                embeddings.append(vector)
                metadatas.append({"source": filename, "type": doc_type, "chunk_id": idx})
                documents.append(chunk)
                
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            return True, f"{len(ids)} fragmentos indexados."
        return False, "Falha ao gerar embeddings."

    def search(self, query, n_results=3):
        """Busca contexto relevante para a query"""
        query_vector = self._generate_embedding(query)
        if not query_vector:
            return []
            
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        # Formata resultado limpo
        context_snippets = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                source = meta.get('source', 'desconhecido')
                context_snippets.append(f"[Fonte: {source}]\n{doc}")
                
        return context_snippets

    def add_url(self, url):
        """Baixa conteúdo da URL e adiciona à memória"""
        try:
            # Reutilizando lógica de scraping simples
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extração simples de texto (poderia usar BeautifulSoup para limpar melhor)
            # Para evitar dependência extra aqui, vou assumir texto bruto ou usar BS4 se disponível
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove scripts e estilos
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                text_content = soup.get_text()
                # Limpa linhas em branco
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            except ImportError:
                clean_text = response.text # Fallback se bs4 não instalado
                
            return self.add_document(clean_text, url, "web_url")
            
        except Exception as e:
            return False, f"Erro ao acessar URL: {str(e)}"

def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)
