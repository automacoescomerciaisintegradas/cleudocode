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
        # Incluindo 'google', 'openrouter' e 'ollama' na sequência padrão se não definido
        default_seq = "anthropic,zai,google,openrouter,openai,ollama"
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
                if p == "ollama" and not os.getenv("OLLAMA_ENABLED", "true") == "true": continue

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
            return self._query_google(messages, model or "gemini-1.5-flash", temperature, **kwargs)
        elif provider == "ollama":
            return self._query_ollama(messages, model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b"), temperature, **kwargs)
        elif provider == "google-antigravity":
            return self._query_google_antigravity(messages, model or "google/antigravity-v1", temperature, **kwargs)
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
        
        # 1. Extract System Message
        system_msg = ""
        filtered_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                filtered_msgs.append(m)
        
        # 2. Sanitize Messages (Must start with user, alternate user/assistant)
        anthropic_messages = []
        if not filtered_msgs:
            # Fallback if no messages
            anthropic_messages.append({"role": "user", "content": "Hello"})
        else:
            # Ensure first message is user
            if filtered_msgs[0]["role"] != "user":
                 anthropic_messages.append({"role": "user", "content": "Context:"})
            
            # Merge consecutive same-role messages
            last_role = None
            for m in filtered_msgs:
                role = m["role"]
                content = m["content"]
                
                if role == last_role:
                    # Append to previous message content
                    anthropic_messages[-1]["content"] += f"\n\n{content}"
                else:
                    anthropic_messages.append({"role": role, "content": content})
                    last_role = role

        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": anthropic_messages,
            "temperature": temperature,
            **kwargs
        }
        if system_msg:
            payload["system"] = system_msg.strip()
            
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                 logger.error(f"Anthropic 400 Error: {response.text}")
            raise e
            
        return response.json()["content"][0]["text"]

    def _query_zai(self, messages, model, temperature, **kwargs):
        """Provedor Z.AI / GLM-4 (usando API compatível com OpenAI)"""
        api_key = os.getenv("ZAI_API_KEY")
        base_url = os.getenv("ZAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4").rstrip('/')
        
        if not api_key:
            raise ValueError("ZAI_API_KEY não configurada")
        
        # GLM/BigModel usa formato OpenAI, não Anthropic
        url = f"{base_url}/chat/completions"
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


    def _query_google_antigravity(self, messages, model, temperature, **kwargs):
        auth_token = os.getenv("GOOGLE_ANTIGRAVITY_TOKEN")
        if not auth_token:
            raise ValueError("GOOGLE_ANTIGRAVITY_TOKEN não configurada.")
            
        # Use direct Google API if token is present, bypassing local gateway
        # Map antigravity model to a real Google model
        real_model = "gemini-2.0-flash-exp"
        if model == "google/antigravity-v1":
             real_model = "gemini-2.0-flash-exp" # Fast and good for agents
        else:
             real_model = model

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model}:generateContent"
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to Google format (same as _query_google)
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

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return "Erro: Resposta vazia do Google Antigravity"
            
        except requests.exceptions.HTTPError as e:
            # Fallback to Gateway if direct API fails (e.g. invalid token scope)
            logger.warning(f"Direct Google API failed ({e}), falling back to Gateway...")
            raise e


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
            
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
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

    def _query_ollama(self, messages, model, temperature, **kwargs):
        """Provedor Ollama para execução local."""
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
        url = f"{host}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            logger.error(f"Erro no Ollama: {e}")
            raise e

# Instância única global
llm_hub = LLMHub()
