"""
Sistema de Importação e Gerenciamento de Contatos para Campanhas de WhatsApp
"""
import pandas as pd
import csv
import json
import os
from typing import List, Dict, Any
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from core.config import settings

class GerenciadorContatos:
    def __init__(self):
        self.lista_contatos = []
        self.arquivo_contatos = "contatos_armazenados.json"
        self.carregar_contatos_salvos()
    
    def carregar_contatos_salvos(self):
        """Carrega contatos previamente salvos"""
        if os.path.exists(self.arquivo_contatos):
            try:
                with open(self.arquivo_contatos, 'r', encoding='utf-8') as f:
                    self.lista_contatos = json.load(f)
                print(f"[INFO] {len(self.lista_contatos)} contatos carregados do arquivo")
            except Exception as e:
                print(f"[ERRO] Erro ao carregar contatos salvos: {e}")
    
    def salvar_contatos(self):
        """Salva a lista de contatos no arquivo"""
        try:
            with open(self.arquivo_contatos, 'w', encoding='utf-8') as f:
                json.dump(self.lista_contatos, f, ensure_ascii=False, indent=2)
            print(f"[INFO] {len(self.lista_contatos)} contatos salvos")
        except Exception as e:
            print(f"[ERRO] Erro ao salvar contatos: {e}")
    
    def importar_csv(self, caminho_arquivo: str, coluna_numero: str = 'numero', coluna_nome: str = 'nome'):
        """Importa contatos de arquivo CSV"""
        try:
            df = pd.read_csv(caminho_arquivo, encoding='utf-8')
            return self._processar_dataframe(df, coluna_numero, coluna_nome)
        except Exception as e:
            print(f"[ERRO] Erro ao importar CSV: {e}")
            return []
    
    def importar_excel(self, caminho_arquivo: str, aba: str = None, coluna_numero: str = 'numero', coluna_nome: str = 'nome'):
        """Importa contatos de arquivo Excel"""
        try:
            if aba:
                df = pd.read_excel(caminho_arquivo, sheet_name=aba)
            else:
                df = pd.read_excel(caminho_arquivo)
            return self._processar_dataframe(df, coluna_numero, coluna_nome)
        except Exception as e:
            print(f"[ERRO] Erro ao importar Excel: {e}")
            return []
    
    def importar_google_sheets(self, url_planilha: str, aba_nome: str = None, coluna_numero: str = 'numero', coluna_nome: str = 'nome'):
        """Importa contatos de Google Sheets"""
        try:
            # Configuração para acesso ao Google Sheets
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            # Verificar se temos credenciais do Google
            google_creds = {
                "type": "service_account",
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("GOOGLE_PRIVATE_KEY") else None,
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL')}"
            }
            
            if google_creds["private_key"]:
                credentials = Credentials.from_service_account_info(google_creds, scopes=scopes)
                gc = gspread.authorize(credentials)
                
                # Abrir planilha
                if aba_nome:
                    worksheet = gc.open_by_url(url_planilha).worksheet(aba_nome)
                else:
                    worksheet = gc.open_by_url(url_planilha).sheet1
                
                # Obter dados
                dados = worksheet.get_all_records()
                df = pd.DataFrame(dados)
                
                return self._processar_dataframe(df, coluna_numero, coluna_nome)
            else:
                print("[AVISO] Credenciais do Google não configuradas para acesso ao Sheets")
                return []
                
        except Exception as e:
            print(f"[ERRO] Erro ao importar Google Sheets: {e}")
            return []
    
    def _processar_dataframe(self, df: pd.DataFrame, coluna_numero: str, coluna_nome: str):
        """Processa dataframe e extrai contatos"""
        contatos_importados = []
        
        # Verificar se as colunas existem
        col_numero = None
        col_nome = None
        
        for col in df.columns:
            if coluna_numero.lower() in col.lower():
                col_numero = col
            if coluna_nome.lower() in col.lower():
                col_nome = col
        
        if not col_numero:
            # Tentar encontrar colunas comuns para número de telefone
            colunas_telefone = ['telefone', 'celular', 'numero', 'phone', 'mobile', 'whatsapp', 'tel', 'num']
            for col in df.columns:
                if any(term in col.lower() for term in colunas_telefone):
                    col_numero = col
                    break
        
        if not col_nome:
            # Tentar encontrar colunas comuns para nome
            colunas_nome = ['nome', 'name', 'cliente', 'contato', 'razao', 'empresa']
            for col in df.columns:
                if any(term in col.lower() for term in colunas_nome):
                    col_nome = col
                    break
        
        if not col_numero:
            print(f"[ERRO] Coluna de número não encontrada. Colunas disponíveis: {list(df.columns)}")
            return []
        
        print(f"[INFO] Processando {len(df)} linhas...")
        
        for idx, row in df.iterrows():
            numero = str(row[col_numero]).strip()
            
            # Padronizar número de telefone
            numero_padronizado = self.padronizar_numero(numero)
            
            if numero_padronizado:
                nome = row[col_nome] if col_nome and col_nome in row else f"Contato {idx+1}"
                
                contato = {
                    "id": f"{numero_padronizado}@s.whatsapp.net",
                    "nome": str(nome),
                    "fonte": "importacao",
                    "data_importacao": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": [],
                    "historico": []
                }
                
                contatos_importados.append(contato)
        
        print(f"[OK] {len(contatos_importados)} contatos importados com sucesso")
        return contatos_importados
    
    def padronizar_numero(self, numero: str) -> str:
        """Padroniza número de telefone para formato internacional"""
        if not numero:
            return None
        
        # Remover caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, str(numero)))
        
        # Verificar se tem DDI
        if len(numero_limpo) == 11 and numero_limpo.startswith('55'):  # 55XXYYYYYYYY
            return numero_limpo
        elif len(numero_limpo) == 10 or len(numero_limpo) == 11:  # XXYYYYYYYY ou XXYYYYYYYYY
            # Adicionar DDI do Brasil
            return f"55{numero_limpo}"
        elif len(numero_limpo) == 9:  # Celular sem DDD
            # Supondo DDD padrão do Ceará
            return f"55859{numero_limpo}"
        elif len(numero_limpo) == 8:  # Fixo sem DDD
            # Supondo DDD padrão do Ceará
            return f"5585{numero_limpo}"
        else:
            # Número já tem DDI ou formato internacional
            return numero_limpo
    
    def adicionar_contatos(self, novos_contatos: List[Dict[str, Any]]):
        """Adiciona novos contatos à lista, evitando duplicatas"""
        contatos_adicionados = 0
        
        for contato in novos_contatos:
            # Verificar se contato já existe
            if not any(c['id'] == contato['id'] for c in self.lista_contatos):
                self.lista_contatos.append(contato)
                contatos_adicionados += 1
            else:
                print(f"[AVISO] Contato já existe: {contato['nome']} ({contato['id']})")
        
        if contatos_adicionados > 0:
            self.salvar_contatos()
            print(f"[OK] {contatos_adicionados} novos contatos adicionados")
        
        return contatos_adicionados
    
    def criar_campanha_por_lista(self, nome_campanha: str, contatos_ids: List[str], mensagem: str):
        """Cria uma campanha usando uma lista específica de contatos"""
        contatos_validos = []
        
        for contato_id in contatos_ids:
            contato = next((c for c in self.lista_contatos if c['id'] == contato_id), None)
            if contato:
                contatos_validos.append(contato)
            else:
                print(f"[AVISO] Contato não encontrado na lista: {contato_id}")
        
        if not contatos_validos:
            print(f"[ERRO] Nenhum contato válido encontrado para a campanha '{nome_campanha}'")
            return None
        
        campanha = {
            "nome": nome_campanha,
            "mensagem": mensagem,
            "destinatarios": [c['id'] for c in contatos_validos],
            "data_criacao": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "criada",
            "total_destinatarios": len(contatos_validos),
            "envios": []
        }
        
        print(f"[OK] Campanha '{nome_campanha}' criada com {len(contatos_validos)} destinatários")
        return campanha
    
    def criar_campanha_por_tags(self, nome_campanha: str, tags: List[str], mensagem: str):
        """Cria uma campanha para contatos com determinadas tags"""
        contatos_filtrados = []
        
        for contato in self.lista_contatos:
            if any(tag in contato.get('tags', []) for tag in tags):
                contatos_filtrados.append(contato)
        
        if not contatos_filtrados:
            print(f"[AVISO] Nenhum contato encontrado com as tags: {tags}")
            return None
        
        campanha = {
            "nome": nome_campanha,
            "mensagem": mensagem,
            "destinatarios": [c['id'] for c in contatos_filtrados],
            "data_criacao": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "criada",
            "total_destinatarios": len(contatos_filtrados),
            "envios": []
        }
        
        print(f"[OK] Campanha '{nome_campanha}' criada com {len(contatos_filtrados)} destinatários (filtrados por tags: {tags})")
        return campanha
    
    def obter_estatisticas(self):
        """Obtém estatísticas da lista de contatos"""
        total_contatos = len(self.lista_contatos)
        
        # Contar por fonte
        fontes = {}
        for contato in self.lista_contatos:
            fonte = contato.get('fonte', 'desconhecida')
            fontes[fonte] = fontes.get(fonte, 0) + 1
        
        # Contar por tags
        todas_tags = []
        for contato in self.lista_contatos:
            todas_tags.extend(contato.get('tags', []))
        
        tags_count = {}
        for tag in todas_tags:
            tags_count[tag] = tags_count.get(tag, 0) + 1
        
        estatisticas = {
            "total_contatos": total_contatos,
            "por_fonte": fontes,
            "tags_populares": tags_count,
            "data_atualizacao": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return estatisticas
    
    def exportar_contatos(self, caminho_saida: str, formato: str = 'csv'):
        """Exporta contatos para arquivo"""
        if not self.lista_contatos:
            print("[AVISO] Nenhum contato para exportar")
            return
        
        df = pd.DataFrame(self.lista_contatos)
        
        if formato.lower() == 'csv':
            df.to_csv(caminho_saida, index=False, encoding='utf-8')
        elif formato.lower() == 'excel' or formato.lower() == 'xlsx':
            df.to_excel(caminho_saida, index=False)
        elif formato.lower() == 'json':
            df.to_json(caminho_saida, orient='records', force_ascii=False, indent=2)
        else:
            print(f"[ERRO] Formato '{formato}' não suportado")
            return
        
        print(f"[OK] {len(self.lista_contatos)} contatos exportados para: {caminho_saida}")

def menu_interativo():
    """Menu interativo para gerenciamento de contatos"""
    gerenciador = GerenciadorContatos()
    
    while True:
        print(f"\n{'='*60}")
        print("GERENCIADOR DE CONTATOS PARA CAMPANHAS DE WHATSAPP")
        print("="*60)
        print("1. Importar contatos de CSV")
        print("2. Importar contatos de Excel")
        print("3. Importar contatos de Google Sheets")
        print("4. Visualizar contatos")
        print("5. Criar campanha por lista de contatos")
        print("6. Criar campanha por tags")
        print("7. Ver estatísticas")
        print("8. Exportar contatos")
        print("9. Sair")
        print("-"*60)
        
        opcao = input("Escolha uma opção (1-9): ").strip()
        
        if opcao == '1':
            caminho = input("Caminho do arquivo CSV: ").strip()
            if os.path.exists(caminho):
                col_numero = input("Nome da coluna de número (padrão: 'numero'): ").strip() or 'numero'
                col_nome = input("Nome da coluna de nome (padrão: 'nome'): ").strip() or 'nome'
                
                contatos = gerenciador.importar_csv(caminho, col_numero, col_nome)
                if contatos:
                    gerenciador.adicionar_contatos(contatos)
            else:
                print("[ERRO] Arquivo não encontrado")
        
        elif opcao == '2':
            caminho = input("Caminho do arquivo Excel: ").strip()
            if os.path.exists(caminho):
                aba = input("Nome da aba (pressione Enter para usar a primeira): ").strip() or None
                col_numero = input("Nome da coluna de número (padrão: 'numero'): ").strip() or 'numero'
                col_nome = input("Nome da coluna de nome (padrão: 'nome'): ").strip() or 'nome'
                
                contatos = gerenciador.importar_excel(caminho, aba, col_numero, col_nome)
                if contatos:
                    gerenciador.adicionar_contatos(contatos)
            else:
                print("[ERRO] Arquivo não encontrado")
        
        elif opcao == '3':
            url = input("URL da planilha Google Sheets: ").strip()
            if url:
                aba = input("Nome da aba (pressione Enter para usar a primeira): ").strip() or None
                col_numero = input("Nome da coluna de número (padrão: 'numero'): ").strip() or 'numero'
                col_nome = input("Nome da coluna de nome (padrão: 'nome'): ").strip() or 'nome'
                
                contatos = gerenciador.importar_google_sheets(url, aba, col_numero, col_nome)
                if contatos:
                    gerenciador.adicionar_contatos(contatos)
        
        elif opcao == '4':
            print(f"\nCONTATOS ARMAZENADOS: {len(gerenciador.lista_contatos)}")
            for i, contato in enumerate(gerenciador.lista_contatos[:20], 1):  # Mostrar os primeiros 20
                print(f"  {i:2d}. {contato['nome']} - {contato['id']}")
            
            if len(gerenciador.lista_contatos) > 20:
                print(f"  ... e mais {len(gerenciador.lista_contatos) - 20} contatos")
        
        elif opcao == '5':
            nome_campanha = input("Nome da campanha: ").strip()
            mensagem = input("Mensagem da campanha: ").strip()
            
            if nome_campanha and mensagem:
                print("\nContatos disponíveis:")
                for i, contato in enumerate(gerenciador.lista_contatos):
                    print(f"  {i+1:2d}. {contato['nome']} - {contato['id']}")
                
                ids_input = input("\nIDs dos contatos (separados por vírgula): ").strip()
                if ids_input:
                    ids = [id.strip() for id in ids_input.split(',')]
                    campanha = gerenciador.criar_campanha_por_lista(nome_campanha, ids, mensagem)
                    if campanha:
                        print(f"[OK] Campanha '{nome_campanha}' criada com {campanha['total_destinatarios']} destinatários")
        
        elif opcao == '6':
            nome_campanha = input("Nome da campanha: ").strip()
            mensagem = input("Mensagem da campanha: ").strip()
            tags_input = input("Tags (separadas por vírgula): ").strip()
            
            if nome_campanha and mensagem and tags_input:
                tags = [tag.strip() for tag in tags_input.split(',')]
                campanha = gerenciador.criar_campanha_por_tags(nome_campanha, tags, mensagem)
                if campanha:
                    print(f"[OK] Campanha '{nome_campanha}' criada com {campanha['total_destinatarios']} destinatários")
        
        elif opcao == '7':
            stats = gerenciador.obter_estatisticas()
            print(f"\nESTATÍSTICAS:")
            print(f"  Total de contatos: {stats['total_contatos']}")
            print(f"  Por fonte: {stats['por_fonte']}")
            print(f"  Tags mais usadas: {stats['tags_populares']}")
        
        elif opcao == '8':
            caminho = input("Caminho para exportar: ").strip()
            formato = input("Formato (csv/excel/json, padrão: csv): ").strip() or 'csv'
            if caminho:
                gerenciador.exportar_contatos(caminho, formato)
        
        elif opcao == '9':
            print("\nSistema de gerenciamento de contatos encerrado.")
            break
        
        else:
            print("[ERRO] Opção inválida")

if __name__ == "__main__":
    print("Sistema de Gerenciamento de Contatos para Campanhas de WhatsApp")
    print("="*60)
    
    # Executar menu interativo
    menu_interativo()
    
    print(f"\n{'='*60}")
    print("SISTEMA ENCERRADO")
    print("="*60)