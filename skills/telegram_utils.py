import requests
import json
from skills.base import BaseSkill
from core.config import settings

class TelegramLookupSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="telegram_lookup",
            description="Verifica informações de um Chat ou Canal do Telegram via API. Útil para descobrir Chat IDs. Uso: forneça o @username ou ID numérico."
        )

    def execute(self, params: str) -> str:
        target = params.strip()
        token = settings.get("TELEGRAM_TOKEN")
        
        if not token:
            return "Erro: TELEGRAM_TOKEN não configurado no .env"

        # Tenta limpar o input
        if target.startswith("https://t.me/"):
            target = "@" + target.split("/")[-1]

        url = f"https://api.telegram.org/bot{token}/getChat"
        
        try:
            response = requests.post(url, json={"chat_id": target}, timeout=10)
            data = response.json()
            
            if data.get("ok"):
                chat = data["result"]
                info = [
                    f"✅ **Encontrado!**",
                    f"🆔 ID: `{chat.get('id')}`",
                    f"📌 Tipo: {chat.get('type')}",
                    f"👤 Nome: {chat.get('title') or chat.get('first_name')}",
                    f"🔗 Username: @{chat.get('username')}" if chat.get('username') else "🔗 Username: (sem username)"
                ]
                # Se for privado e não tiver acesso, a API geralmente retorna erro antes.
                return "\n".join(info)
            else:
                err_code = data.get("error_code")
                desc = data.get("description")
                return f"❌ **Erro Telegram ({err_code}):** {desc}\n\nDica: Se for um canal privado ou grupo, certifique-se de que o bot é ADMINISTRADOR."
                
        except Exception as e:
            return f"Erro de conexão com Telegram API: {e}"
