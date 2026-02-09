import os
import requests
import json
import logging

logger = logging.getLogger(__name__)

class LLMHub:
    def __init__(self):
        pass

    def query(self, messages, model=None, provider=None, temperature=0.7, **kwargs):
        """Executa consulta ao LLM com suporte a falha automática (fallback)."""
        
        # 1. Se um provedor específico for solicitado, tentamos apenas ele
        if provider:
            return self._dispatch_query(messages, model, provider, temperature, **kwargs)

        # 2. Caso contrário, tentamos a sequência de fallback do .env
        # Incluindo 'google' e 'openrouter' na sequência padrão se não definido
        default_seq = "ollama,anthropic,zai,google,openrouter,openai"
        fallback_str = os.getenv("LLM_FALLBACK_SEQUENCE", default_seq)
        sequence = [p.strip() for p in fallback_str.split(",")]
        
        errors = []
        for p in sequence:
            try:
                # Verificar se temos chave para provedores cloud antes de tentar
                if p == "openai" and not os.getenv("OPENAI_API_KEY"): continue
                if p == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"): continue
                if p == "google" and not os.getenv("GOOGLE_API_KEY"): continue
                if p == "openrouter" and not os.getenv("OPENROUTER_API_KEY"): continue
                if p == "zai" and not os.getenv("ZAI_API_KEY"): continue
                if p == "groq" and not os.getenv("GROQ_API_KEY"): continue
                if p == "moonshot" and not os.getenv("MOONSHOT_API_KEY"): continue

                logger.info(f"Tentando provedor: {p}")
                return self._dispatch_query(messages, model, p, temperature, **kwargs)
            except Exception as e:
                err_msg = f"{p}: {str(e)}"
                logger.warning(f"Falha no provedor {err_msg}")
                errors.append(err_msg)
                continue
        
        error_report = " | ".join(errors)
        raise RuntimeError(f"Todos os provedores de LLM falharam. Relatório: [{error_report}]")

    def _dispatch_query(self, messages, model, provider, temperature, **kwargs):
        """Roteia a query para o método do provedor correto."""
        if provider == "openai":
            return self._query_openai(messages, model or "gpt-4o-mini", temperature, **kwargs)
        elif provider == "anthropic":
            return self._query_anthropic(messages, model or "claude-3-5-sonnet-20241022", temperature, **kwargs)
        elif provider == "zai":
            return self._query_zai(messages, model or os.getenv("ZAI_MODEL", "glm-4-32b-0414-128k"), temperature, **kwargs)
        elif provider == "openrouter":
            return self._query_openrouter(messages, model or "google/gemini-flash-2.0", temperature, **kwargs)
        elif provider == "google":
            return self._query_google(messages, model or "gemini-1.5-pro", temperature, **kwargs)
        elif provider == "google-antigravity":
            return self._query_google_antigravity(messages, model or "google/antigravity-v1", temperature, **kwargs)
        elif provider == "ollama":
            return self._query_ollama(messages, model or os.getenv("DEEPSEEK_MODEL", "qwen2.5:7b"), temperature, **kwargs)
        elif provider == "groq":
            return self._query_groq(messages, model or "openai/gpt-oss-20b", temperature, **kwargs)
        elif provider == "moonshot":
            return self._query_moonshot(messages, model or "kimi-k2.5", temperature, **kwargs)
        else:
            raise ValueError(f"Provedor desconhecido: {provider}")

    def _query_openai(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _query_anthropic(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada")
            
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Converter formato OpenAI (messages) para formato Anthropic se necessário
        # Simplificação: assume que messages já estão no formato correto ou converte sistema
        system_msg = ""
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                anthropic_messages.append({"role": m["role"], "content": m["content"]})
        
        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": anthropic_messages,
            "temperature": temperature,
            **kwargs
        }
        if system_msg:
            payload["system"] = system_msg
            
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["content"][0]["text"]

    def _query_zai(self, messages, model, temperature, **kwargs):
        """Provedor Z.AI (usando API compatível com Anthropic mas URL customizada)"""
        api_key = os.getenv("ZAI_API_KEY")
        base_url = os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/anthropic").rstrip('/')
        
        if not api_key:
            raise ValueError("ZAI_API_KEY não configurada")
            
        url = f"{base_url}/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_msg = ""
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                anthropic_messages.append({"role": m["role"], "content": m["content"]})
        
        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": anthropic_messages,
            "temperature": temperature,
            **kwargs
        }
        if system_msg:
            payload["system"] = system_msg
            
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["content"][0]["text"]

    def _query_ollama(self, messages, model, temperature, **kwargs):
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
        
        # Lista de hosts para tentar
        hosts_to_try = []
        
        # Sugerir alternativas baseadas no ambiente
        if os.path.exists('/.dockerenv'):
            # No Docker, host.docker.internal é o host real (onde o Ollama costuma estar)
            alt = ollama_host.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
            hosts_to_try.append(alt)
            if ollama_host not in hosts_to_try: hosts_to_try.append(ollama_host)
        else:
            hosts_to_try.append(ollama_host)
            alt = ollama_host.replace("host.docker.internal", "localhost")
            if alt not in hosts_to_try: hosts_to_try.append(alt)

        url_path = "/v1/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            **kwargs
        }
        
        last_err = None
        for current_host in hosts_to_try:
            try:
                url = f"{current_host}{url_path}"
                response = requests.post(url, json=payload, timeout=120)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                last_err = e
                continue
                
        raise RuntimeError(f"Ollama offline (Tentados: {', '.join(hosts_to_try)}): {last_err}")

    def _query_google_antigravity(self, messages, model, temperature, **kwargs):
        auth_token = os.getenv("GOOGLE_ANTIGRAVITY_TOKEN")
        if not auth_token:
            raise ValueError("GOOGLE_ANTIGRAVITY_TOKEN não configurada.")
            
        gateway_url = os.getenv("ANTIGRAVITY_GATEWAY_URL")
        if not gateway_url:
            base_url = "http://host.docker.internal:18900" if os.path.exists('/.dockerenv') else "http://localhost:18900"
            gateway_url = f"{base_url}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(gateway_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _query_openrouter(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY não configurada")
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://cleudocode.com.br",
            "X-Title": "Cleudocode",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _query_google(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Converter mensagens para formato Google
        contents = []
        system_instruction = None
        
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m["content"]}]
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 4096,
            }
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction
            
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return "Erro: Resposta vazia do Google Gemini"

    def _query_groq(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não configurada")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _query_moonshot(self, messages, model, temperature, **kwargs):
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY não configurada")
        
        url = "https://api.moonshot.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Instância única global
llm_hub = LLMHub()
