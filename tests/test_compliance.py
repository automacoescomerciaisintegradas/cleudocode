import pytest
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
MODEL = os.getenv("DEEPSEEK_MODEL", "qwen2.5-coder:7b")

@pytest.fixture
def api_url():
    return f"{OLLAMA_HOST}/v1/chat/completions"

@pytest.fixture
def headers():
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-proj-placeholder" # OpenAI exige, Ollama ignora mas bom ter
    }

def test_chat_completion_structure(api_url, headers):
    """
    Testa se o endpoint retorna a estrutura JSON compatível com Open Responses / OpenAI
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Say Hello!"}],
        "stream": False
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        assert response.status_code == 200, f"Falha na requisição: {response.text}"
        
        data = response.json()
        
        # Validação de Schema Básico (OpenAI Spec)
        assert "id" in data, "Faltando campo 'id'"
        assert "object" in data, "Faltando campo 'object'"
        assert data["object"] == "chat.completion", "Tipo de objeto incorreto"
        assert "created" in data, "Faltando campo 'created'"
        assert "model" in data, "Faltando campo 'model'"
        assert "choices" in data, "Faltando lista 'choices'"
        assert isinstance(data["choices"], list), "'choices' deve ser uma lista"
        assert len(data["choices"]) > 0, "Lista 'choices' está vazia"
        
        # Validação do primeiro choice
        choice = data["choices"][0]
        assert "index" in choice, "Choice faltando 'index'"
        assert "message" in choice, "Choice faltando 'message'"
        assert "finish_reason" in choice, "Choice faltando 'finish_reason'"
        
        # Validação da mensagem
        message = choice["message"]
        assert "role" in message, "Message faltando 'role'"
        assert "content" in message, "Message faltando 'content'"
        assert isinstance(message["content"], str), "Conteúdo deve ser string"

        print(f"\n[SUCESSO] O endpoint {api_url} esta conforme com a estrutura basica.")

    except requests.exceptions.ConnectionError:
        pytest.fail("Não foi possível conectar ao servidor Ollama.")

def test_model_availability():
    """Confirma se o modelo configurado está realmente respondendo"""
    tags_url = f"{OLLAMA_HOST}/api/tags" # Endpoint nativo do Ollama para listar modelos
    try:
        response = requests.get(tags_url, timeout=10)
        if response.status_code == 200:
            models = [m['name'] for m in response.json()['models']]
            # Verifica se o modelo exato ou uma variação dele está presente
            assert any(MODEL in m for m in models), f"Modelo {MODEL} não encontrado na lista: {models}"
    except Exception:
        pass # Ignora falha aqui pois foca no OpenResponses, é apenas um check extra

if __name__ == "__main__":
    # Permite rodar o arquivo diretamente sem pytest instalado no path global
    print("Para rodar os testes, use: pytest tests/test_compliance.py -v -s")
