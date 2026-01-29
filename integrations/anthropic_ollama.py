"""
Integração Anthropic com Ollama local.

Fornece uma classe wrapper para comunicação com Ollama usando a API Anthropic,
permitindo usar qualquer modelo disponível no Ollama.
"""

import anthropic
from typing import Optional, List


class OllamaAnthropicClient:
    """
    Cliente Anthropic configurado para usar Ollama localmente como backend.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        api_key: str = "ollama",  # Ignorado pelo Ollama, mas obrigatório pela API
        model: str = "qwen2.5-coder:7b"
    ):
        """
        Inicializa o cliente Anthropic com Ollama.
        
        Args:
            base_url: URL do servidor Ollama
            api_key: Chave de API (ignorada, apenas para compatibilidade)
            model: Modelo a usar no Ollama
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        
        self.client = anthropic.Anthropic(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    def send_message(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Envia mensagens para o Ollama e retorna a resposta.
        
        Args:
            messages: Lista de dicts com 'role' e 'content'
            temperature: Criatividade da resposta (0.0-2.0)
            max_tokens: Limite de tokens na resposta
            
        Returns:
            Conteúdo da resposta como string
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if response.content:
                return response.content[0].text
            return "Erro: Resposta vazia do modelo"
            
        except Exception as e:
            return f"Erro ao comunicar com Ollama: {str(e)}"
    
    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Interface simplificada para um chat de turno único.
        
        Args:
            prompt: Mensagem do usuário
            system: Mensagem de sistema opcional
            temperature: Criatividade da resposta
            max_tokens: Limite de tokens
            
        Returns:
            Resposta do modelo
        """
        messages = []
        
        if system:
            messages.append({"role": "user", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.send_message(messages, temperature, max_tokens)
    
    def stream_message(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Envia mensagens e recebe a resposta em stream (yield).
        
        Args:
            messages: Lista de dicts com 'role' e 'content'
            temperature: Criatividade da resposta
            max_tokens: Limite de tokens
            
        Yields:
            Fragments de texto da resposta
        """
        try:
            with self.client.messages.stream(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            yield f"Erro ao comunicar com Ollama: {str(e)}"


# Função helper para uso rápido
def quick_chat(prompt: str, model: str = "qwen2.5-coder:7b") -> str:
    """
    Chat rápido com um modelo Ollama sem configuração.
    
    Args:
        prompt: Mensagem do usuário
        model: Modelo a usar
        
    Returns:
        Resposta do modelo
    """
    client = OllamaAnthropicClient(model=model)
    return client.chat(prompt)


if __name__ == "__main__":
    # Exemplo de uso
    client = OllamaAnthropicClient(model="qwen2.5-coder:7b")
    
    response = client.chat(
        "Write a function to check if a number is prime",
        temperature=0.2
    )
    print(response)
