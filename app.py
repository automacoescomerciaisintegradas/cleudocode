import requests
import json
import os
import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5:14b")

# Histórico da conversa em memória
conversation_history = []

def chat_with_ollama(messages):
    """
    Envia o histórico completo de mensagens para o Ollama (Padrão Open Responses)
    """
    url = f"{OLLAMA_HOST}/v1/chat/completions"
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    
    try:
        # print(f"DEBUG: Enviando {len(messages)} mensagens...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Erro: Formato inesperado: {json.dumps(data, indent=2)}"
            
    except requests.exceptions.ConnectionError:
        return "Erro: Falha na conexão com o servidor Ollama."
    except requests.exceptions.HTTPError as e:
        return f"Erro HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Erro: {str(e)}"

def save_history():
    """Salva o histórico atual em um arquivo JSON com timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, indent=2, ensure_ascii=False)
        return f"Histórico salvo em: {filename}"
    except Exception as e:
        return f"Erro ao salvar: {e}"

def load_text_file(filepath):
    """Lê um arquivo de texto e retorna seu conteúdo"""
    try:
        if not os.path.exists(filepath):
            return None, "Arquivo não encontrado."
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, f"Arquivo '{filepath}' carregado ({len(content)} caracteres)."
    except Exception as e:
        return None, f"Erro ao ler arquivo: {e}"

def print_help():
    print("\n--- Comandos Disponíveis ---")
    print(" /load <arquivo> : Lê um arquivo de texto e envia como contexto.")
    print(" /save           : Salva o histórico da conversa atual em JSON.")
    print(" /clear          : Limpa o histórico da memória.")
    print(" /history        : Mostra o histórico atual.")
    print(" sair / exit     : Encerra o programa.")
    print("----------------------------\n")

if __name__ == "__main__":
    print(f"=== LLM P2P Chat ===")
    print(f"Modelo: {MODEL}")
    print(f"Servidor: {OLLAMA_HOST}")
    print("Digite '/help' para ver os comandos.")
    
    while True:
        try:
            user_input = input("\nVocê: ").strip()
            
            if not user_input:
                continue
                
            # Comandos do Sistema
            if user_input.lower() in ['sair', 'exit', 'quit', '/stop']:
                print("\nEncerrando...")
                print(save_history())
                break
                
            elif user_input.lower() == '/help':
                print_help()
                continue
                
            elif user_input.lower() == '/save':
                print(save_history())
                continue
                
            elif user_input.lower() == '/clear':
                conversation_history = []
                print("Histórico limpo!")
                continue

            elif user_input.lower() == '/history':
                print(json.dumps(conversation_history, indent=2, ensure_ascii=False))
                continue
                
            elif user_input.lower().startswith('/load '):
                filepath = user_input[6:].strip()
                content, msg = load_text_file(filepath)
                print(msg)
                
                if content:
                    # Adiciona o conteúdo do arquivo como uma mensagem do usuário, mas não envia imediatamente para o LLM responder
                    # ou podemos enviar pedindo um resumo. Vamos apenas adicionar ao contexto.
                    conversation_history.append({"role": "user", "content": f"Conteúdo do arquivo '{filepath}':\n\n{content}"})
                    print("Conteúdo adicionado ao contexto. Você pode fazer perguntas sobre ele agora.")
                continue

            # Fluxo Normal de Chat
            conversation_history.append({"role": "user", "content": user_input})
            
            print("Processando...")
            response_content = chat_with_ollama(conversation_history)
            
            print(f"Assistente: {response_content}")
            
            # Adiciona resposta ao histórico
            conversation_history.append({"role": "assistant", "content": response_content})
            
        except KeyboardInterrupt:
            print("\nEncerrando...")
            print(save_history()) # Salva automatico ao fechar forçado e exibe mensagem
            break
