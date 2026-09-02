import os
import requests
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("chromadb não encontrado ou incompatível. RAG estará desativado.")

from pypdf import PdfReader
import uuid

# Configurações Defaults (serão sobrescritas pelo .env se carregadas lá fora, mas garantimos aqui)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b") # Usamos o mesmo modelo para chat e embedding se possível, ou um específico
COLLECTION_NAME = "llmp2p_memory"

class RAGBrain:
    def __init__(self):
        if not HAS_CHROMADB:
            self.collection = None
            print("RAGBrain em modo STUB (chromadb ausente).")
            return

        # Auto-correção de host
        global OLLAMA_HOST
        if os.path.exists('/.dockerenv'):
            if "localhost" in OLLAMA_HOST or "127.0.0.1" in OLLAMA_HOST:
                OLLAMA_HOST = OLLAMA_HOST.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
        else:
            if "host.docker.internal" in OLLAMA_HOST:
                OLLAMA_HOST = OLLAMA_HOST.replace("host.docker.internal", "localhost")

        # ChromaDB Persistente na pasta 'memory_db'
        self.client = chromadb.PersistentClient(path="memory_db")
        # ... rest of init logic (omitted for brevity in replacement, but I will include it)
        try:
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            test_embedding = self._generate_embedding("test")
            if test_embedding:
                try:
                    query_result = self.collection.query(
                        query_embeddings=[test_embedding],
                        n_results=1
                    )
                except Exception as e:
                    if "dimension" in str(e).lower():
                        print(f"Dimensão de embedding incompatível detectada: {str(e)}")
                        print("Recriando collection...")
                        self.client.delete_collection(COLLECTION_NAME)
                        self.collection = self.client.get_or_create_collection(
                            name=COLLECTION_NAME,
                            metadata={"hnsw:space": "cosine"}
                        )
                    else:
                        raise e
        except:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        
    def _generate_embedding(self, text):
        """Gera embedding usando Fallback Local (ChromaDB Default)"""
        # Removido suporte a Ollama Embeddings para estabilidade
        
        # Fallback Local (Usando a função padrão do ChromaDB)
        try:
            if not hasattr(self, 'local_ef'):
                from chromadb.utils import embedding_functions
                self.local_ef = embedding_functions.DefaultEmbeddingFunction()
            
            # Converte para lista de floats nativos: o DefaultEmbeddingFunction
            # retorna numpy array de np.float32, que o chromadb rejeita dentro
            # de listas e cujo truthiness check em array >1 elemento levanta
            # "truth value of an array is ambiguous" (verificações em search/add/init).
            return [float(x) for x in self.local_ef([text])[0]]
        except Exception as e:
            print(f"Falha crítica em embedding local: {e}")
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
        if not HAS_CHROMADB or not self.collection:
            return []
            
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

_brain_instance = None


def get_brain():
    """Retorna a instância única da memória semântica (uma por processo).

    Evita múltiplos PersistentClient do ChromaDB apontando para o mesmo
    diretório quando várias camadas (ex.: cognição e web) precisam da memória.
    """
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = RAGBrain()
    return _brain_instance


def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)

import os
import datetime

def export_memory_for_notebooklm(rag_brain):
    """
    Exporta todo o conteúdo do RAG (ChromaDB) para um único arquivo Markdown/Texto
    otimizado para importação no Google NotebookLM.
    """
    output_dir = "exports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/NotebookLM_Sync_{timestamp}.txt"
    
    try:
        # Pega todos os documentos da coleção
        # Nota: ChromaDB permite pegar via .get()
        data = rag_brain.collection.get()
        
        documents = data['documents']
        metadatas = data['metadatas']
        
        if not documents:
            return False, "Nenhum documento encontrado na memória para sincronizar."
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Sincronização LLM P2P Chat -> NotebookLM\n")
            f.write(f"Data: {timestamp}\n")
            f.write(f"Total de Fragmentos: {len(documents)}\n\n")
            
            # Agrupa por Fonte para ficar organizado
            sources = {}
            for doc, meta in zip(documents, metadatas):
                source_name = meta.get('source', 'Desconhecido')
                if source_name not in sources:
                    sources[source_name] = []
                sources[source_name].append(doc)
            
            for source, docs in sources.items():
                f.write(f"--- INICIO FONTE: {source} ---\n")
                # Junta os chunks e escreve
                full_text = "\n".join(docs)
                f.write(full_text)
                f.write(f"\n--- FIM FONTE: {source} ---\n\n")
                
        return True, f"Arquivo de Sincronização gerado: {os.path.abspath(filename)}"
        
    except Exception as e:
        return False, f"Erro na exportação: {str(e)}"

