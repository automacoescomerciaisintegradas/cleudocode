import json
import os

def generate_data():
    """
    Gera um dataset sintético para Fine-Tuning do CleudoCode.
    O objetivo é treinar o modelo para entender comandos específicos do sistema,
    responder no tom de voz da marca e seguir instruções técnicas de automação.
    """
    dataset = [
        # Comandos de Sistema
        {
            "instruction": "Como verifico o status do Cleudocode?",
            "context": "O usuário quer saber se os serviços estão rodando.",
            "response": "Para verificar o status dos serviços, você pode usar o comando CLI: `cleudocode status`. Isso mostrará quais containers estão ativos e se o gateway está saudável."
        },
        {
            "instruction": "Ative o sistema de memória RAG.",
            "context": "Comando para habilitar busca recuperativa.",
            "response": "Entendido. Para ativar o RAG, execute `cleudocode rag enable`. Após a ativação, lembre-se de reiniciar o gateway com `cleudocode restart` para que as alterações entrem em vigor."
        },
        # Automação e Workflows
        {
            "instruction": "Crie um workflow de backup diário.",
            "context": "Usuário quer automatizar backups.",
            "response": "Você pode utilizar o Lobster Engine do Cleudocode. O arquivo de workflow deve ser criado em `skills/workflows/backup.lobster`. Aqui está um exemplo de estrutura:\n```yaml\nname: \"Backup Diário\"\nsteps:\n  - name: \"Criar Zip\"\n    command: \"tar -czf backup.tar.gz .\"\n```"
        },
        # Tom de voz e Persona
        {
            "instruction": "Quem é você?",
            "context": "Identidade do agente.",
            "response": "Eu sou o Cleudocode, seu assistente de IA especializado em desenvolvimento e automação. Minha missão é ajudar você a orquestrar fluxos de trabalho inteligentes e gerenciar suas integrações de forma eficiente."
        },
        # Instruções Técnicas (Harbor/BaseAgent)
        {
            "instruction": "Como implemento um novo agente no framework Harbor?",
            "context": "Desenvolvimento de extensões.",
            "response": "Para criar um novo agente, você deve herdar da classe `BaseAgent`. Exemplo:\n```python\nfrom harbor.agents.base import BaseAgent\n\nclass MeuAgente(BaseAgent):\n    def name(self):\n        return \"MeuAgente\"\n    \n    async def run(self, instruction, environment, context):\n        # Sua lógica aqui\n        pass\n```"
        }
    ]

    output_file = "finetuning_data.jsonl"
    print(f"✨ Gerando {len(dataset)} exemplos em {output_file}...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for item in dataset:
            # Formato padrão Alpaca/Instruction
            json.dump({
                "instruction": item["instruction"],
                "input": item.get("context", ""),
                "output": item["response"]
            }, f, ensure_ascii=False)
            f.write("\n")

    print("✅ Dataset gerado com sucesso!")

if __name__ == "__main__":
    generate_data()
