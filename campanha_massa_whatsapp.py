"""
Sistema de Campanhas de Envio em Massa para WhatsApp
"""
import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any
from core.config import settings
from gateways.whatsapp_adapter import WhatsAppGateway

class CampanhaMassaWhatsApp:
    def __init__(self):
        self.gateway = WhatsAppGateway()
        self.contatos_armazenados = []
        
    def carregar_contatos_existentes(self):
        """Carrega contatos que já foram identificados pelo sistema"""
        print("Carregando contatos existentes do sistema...")
        
        # Baseado nas informações que você forneceu, temos alguns contatos identificados
        contatos_existentes = [
            {
                "id": "112928179142781@lid",
                "nome": "Ronaldo Simplicio",
                "grupo": "554184212269-1488774100@g.us",
                "ultimo_contato": "2026-01-27 13:23:31",
                "tipo": "individual"
            }
        ]
        
        self.contatos_armazenados.extend(contatos_existentes)
        print(f"[OK] {len(contatos_existentes)} contatos carregados")
        
    def adicionar_contato(self, contato_id: str, nome: str, tipo: str = "individual", grupo: str = None):
        """Adiciona um novo contato à lista de envio"""
        contato = {
            "id": contato_id,
            "nome": nome,
            "grupo": grupo,
            "ultimo_contato": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "envios": []
        }
        
        # Evitar duplicatas
        if not any(c['id'] == contato_id for c in self.contatos_armazenados):
            self.contatos_armazenados.append(contato)
            print(f"[OK] Contato adicionado: {nome} ({contato_id})")
        else:
            print(f"[INFO] Contato já existe: {nome} ({contato_id})")
    
    def criar_campanha(self, nome_campanha: str, mensagem: str, contatos: List[str] = None):
        """Cria uma nova campanha de envio em massa"""
        print(f"\nCriando campanha: {nome_campanha}")
        print(f"Mensagem: {mensagem[:50]}...")
        
        if not contatos:
            # Se não especificar contatos, usar todos os contatos armazenados
            contatos = [c['id'] for c in self.contatos_armazenados]
        
        print(f"Destinatários: {len(contatos)} contatos")
        
        return {
            "nome": nome_campanha,
            "mensagem": mensagem,
            "destinatarios": contatos,
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "criada",
            "envios": []
        }
    
    def enviar_campanha(self, campanha: Dict[str, Any], delay_entre_envios: float = 2.0):
        """Envia a campanha para todos os destinatários"""
        print(f"\nIniciando envio da campanha: {campanha['nome']}")
        
        resultados = []
        total_destinatarios = len(campanha['destinatarios'])
        
        for i, contato_id in enumerate(campanha['destinatarios']):
            print(f"\n[{i+1}/{total_destinatarios}] Enviando para: {contato_id}")
            
            try:
                # Encontrar nome do contato se disponível
                contato_info = next((c for c in self.contatos_armazenados if c['id'] == contato_id), None)
                nome_contato = contato_info['nome'] if contato_info else contato_id
                
                # Personalizar mensagem se possível
                mensagem_personalizada = campanha['mensagem']
                if nome_contato and nome_contato != contato_id:
                    mensagem_personalizada = mensagem_personalizada.replace("{nome}", nome_contato)
                
                # Enviar mensagem
                resultado = self.gateway.send_message(contato_id, mensagem_personalizada)
                
                envio_registro = {
                    "contato_id": contato_id,
                    "nome": nome_contato,
                    "status": "enviado" if resultado else "falhou",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tentativas": 1
                }
                
                resultados.append(envio_registro)
                campanha['envios'].append(envio_registro)
                
                if resultado:
                    print(f"[OK] Enviado com sucesso para {nome_contato}")
                else:
                    print(f"[ERRO] Falha ao enviar para {nome_contato}")
                
                # Delay entre envios para evitar bloqueio
                if i < len(campanha['destinatarios']) - 1:  # Não esperar após o último
                    print(f"Aguardando {delay_entre_envios}s antes do próximo envio...")
                    time.sleep(delay_entre_envios)
                    
            except Exception as e:
                print(f"[ERRO] Erro ao enviar para {contato_id}: {e}")
                envio_registro = {
                    "contato_id": contato_id,
                    "nome": contato_id,
                    "status": "erro",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "erro": str(e),
                    "tentativas": 1
                }
                resultados.append(envio_registro)
                campanha['envios'].append(envio_registro)
        
        # Atualizar status da campanha
        campanha['status'] = "concluida"
        campanha['resultados'] = {
            "total_envios": len(resultados),
            "envios_sucesso": len([r for r in resultados if r['status'] == 'enviado']),
            "envios_falha": len([r for r in resultados if r['status'] == 'falhou']),
            "envios_erro": len([r for r in resultados if r['status'] == 'erro'])
        }
        
        print(f"\nResultados da campanha '{campanha['nome']}':")
        print(f"   Total: {campanha['resultados']['total_envios']}")
        print(f"   Sucesso: {campanha['resultados']['envios_sucesso']}")
        print(f"   Falha: {campanha['resultados']['envios_falha']}")
        print(f"   Erro: {campanha['resultados']['envios_erro']}")
        
        return campanha
    
    def relatorio_campanha(self, campanha: Dict[str, Any]):
        """Gera relatório detalhado da campanha"""
        print(f"\nRELATÓRIO DA CAMPANHA: {campanha['nome']}")
        print("="*50)
        
        resultados = campanha.get('resultados', {})
        if resultados:
            print(f"Data de criação: {campanha['data_criacao']}")
            print(f"Total de envios: {resultados.get('total_envios', 0)}")
            print(f"Sucessos: {resultados.get('envios_sucesso', 0)}")
            print(f"Falhas: {resultados.get('envios_falha', 0)}")
            print(f"Erros: {resultados.get('envios_erro', 0)}")
        
        # Detalhes dos envios
        envios = campanha.get('envios', [])
        if envios:
            print(f"\nDetalhes dos envios:")
            for envio in envios[:10]:  # Mostrar os primeiros 10
                status_simbolo = "[OK]" if envio['status'] == 'enviado' else "[ERRO]"
                print(f"  {status_simbolo} {envio['nome']} - {envio['status']} ({envio['timestamp']})")
            
            if len(envios) > 10:
                print(f"  ... e mais {len(envios) - 10} envios")
    
    def criar_mensagem_personalizada(self, tipo_mensagem: str, parametros: Dict[str, Any] = None):
        """Cria mensagens personalizadas para diferentes tipos de campanha"""
        
        if tipo_mensagem == "boas_vindas":
            return """[**Atendimento HUMANO**]https://wa.me/5588921567214

Olá {nome}! 👋 Seja bem-vindx ao nosso canal!
📞 Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
💡 **Não perca tempo. A revolução do atendimento começa agora!**
https://www.whatsapp.com/channel/558894227586"""
        
        elif tipo_mensagem == "promocao":
            produto = parametros.get('produto', 'nosso produto')
            desconto = parametros.get('desconto', '20%')
            return f"""OFERTA ESPECIAL para {nome}!
Aproveite {desconto} de desconto em {produto}!
Clique: https://wa.me/558894227586
Oferta válida por tempo limitado!"""
        
        elif tipo_mensagem == "informativa":
            titulo = parametros.get('titulo', 'Novidade!')
            conteudo = parametros.get('conteudo', 'Temos novidades para você.')
            return f"""{titulo}
{conteudo}
Saiba mais: https://wa.me/558894227586
Atenciosamente, Equipe {nome}"""
        
        else:
            return parametros.get('mensagem', f'Mensagem padrão para {nome}')

def main():
    print("Sistema de Campanhas de Envio em Massa para WhatsApp")
    print("="*60)
    
    # Inicializar o sistema
    sistema = CampanhaMassaWhatsApp()
    
    # Carregar contatos existentes
    sistema.carregar_contatos_existentes()
    
    # Adicionar mais contatos de exemplo (você pode substituir pelos reais)
    sistema.adicionar_contato("558894227586@s.whatsapp.net", "Canal Oficial", "canal")
    sistema.adicionar_contato("5588921567214@s.whatsapp.net", "Atendimento Humano", "individual")
    
    print(f"\nContatos disponíveis: {len(sistema.contatos_armazenados)}")
    for contato in sistema.contatos_armazenados:
        print(f"   • {contato['nome']} ({contato['id']})")
    
    # Criar uma campanha de exemplo
    mensagem_boas_vindas = sistema.criar_mensagem_personalizada(
        "boas_vindas",
        {"produto": "serviços exclusivos"}
    )

    campanha = sistema.criar_campanha(
        nome_campanha="Campanha de Boas-Vindas Janeiro 2026",
        mensagem=mensagem_boas_vindas,
        contatos=[c['id'] for c in sistema.contatos_armazenados]  # Enviar para todos
    )

    # Enviar automaticamente para demonstração
    print("\nIniciando envio da campanha de demonstração...")
    campanha = sistema.enviar_campanha(campanha, delay_entre_envios=1.0)  # Delay menor para demonstração
    sistema.relatorio_campanha(campanha)
    
    print(f"\n{'='*60}")
    print("SISTEMA DE CAMPANHAS DE WHATSAPP - CONCLUÍDO")
    print("="*60)
    print("\nDICAS:")
    print("- Use delays adequados para evitar bloqueio")
    print("- Personalize mensagens para melhor engajamento")
    print("- Monitore resultados para otimizar futuras campanhas")
    print("- Respeite políticas de uso do WhatsApp")

if __name__ == "__main__":
    main()