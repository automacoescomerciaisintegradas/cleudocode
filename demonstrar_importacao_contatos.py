"""
Script de demonstração do sistema de importação de contatos para WhatsApp
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class GerenciadorContatosDemo:
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
    
    def criar_contato_exemplo(self):
        """Cria contatos de exemplo baseados nas informações recebidas"""
        contatos_exemplo = [
            {
                "id": "112928179142781@lid",
                "nome": "Ronaldo Simplicio",
                "fonte": "webhook_recebido",
                "grupo": "554184212269-1488774100@g.us",
                "data_importacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": ["ativo", "grupo_principal"],
                "historico": []
            },
            {
                "id": "558894227586@s.whatsapp.net",
                "nome": "Canal Oficial",
                "fonte": "configuracao_sistema",
                "grupo": None,
                "data_importacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": ["canal", "oficial"],
                "historico": []
            },
            {
                "id": "5588921567214@s.whatsapp.net",
                "nome": "Atendimento Humano",
                "fonte": "configuracao_sistema",
                "grupo": None,
                "data_importacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tags": ["atendimento", "humano"],
                "historico": []
            }
        ]
        
        self.lista_contatos.extend(contatos_exemplo)
        print(f"[OK] {len(contatos_exemplo)} contatos de exemplo criados")
        self.salvar_contatos()
    
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
                    "fonte": "importacao_planilha",
                    "grupo": None,
                    "data_importacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": ["importado"],
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
    
    def criar_lista_contatos(self, nome_lista: str, contatos_ids: List[str]):
        """Cria uma lista específica de contatos"""
        contatos_lista = []
        
        for contato_id in contatos_ids:
            contato = next((c for c in self.lista_contatos if c['id'] == contato_id), None)
            if contato:
                contatos_lista.append(contato)
            else:
                print(f"[AVISO] Contato não encontrado: {contato_id}")
        
        lista = {
            "nome": nome_lista,
            "contatos": [c['id'] for c in contatos_lista],
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_contatos": len(contatos_lista),
            "tags_associadas": []
        }
        
        print(f"[OK] Lista '{nome_lista}' criada com {len(contatos_lista)} contatos")
        return lista
    
    def criar_campanha_por_lista(self, nome_campanha: str, lista_contatos: List[str], mensagem: str):
        """Cria uma campanha usando uma lista específica de contatos"""
        contatos_validos = []
        
        for contato_id in lista_contatos:
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
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "criada",
            "total_destinatarios": len(contatos_validos),
            "envios": []
        }
        
        print(f"[OK] Campanha '{nome_campanha}' criada com {len(contatos_validos)} destinatários")
        return campanha
    
    def criar_mensagem_boas_vindas(self):
        """Cria a mensagem de boas-vindas configurada"""
        return """[**Atendimento HUMANO**]https://wa.me/5588921567214

Olá {nome}! Seja bem-vindx ao nosso canal!
Telefone: (88) 9215-67214
Contato e Suporte
[**Saiba Mais!!!!**]
https://wa.me/558894227586
[**Atendimento HUMANO**]https://wa.me/5588921567214
Telefone: (88) 9215-67214
* Nao perca tempo. A revolucao do atendimento comeca agora! *
https://www.whatsapp.com/channel/558894227586"""
    
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
            "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

def criar_arquivo_exemplo():
    """Cria arquivos de exemplo para testar importação"""
    import csv
    
    # Criar arquivo CSV de exemplo
    dados_csv = [
        ['nome', 'numero', 'cidade'],
        ['Maria Silva', '5588999999999', 'Fortaleza'],
        ['João Santos', '5585988888888', 'São Paulo'],
        ['Ana Costa', '5511977777777', 'Rio de Janeiro'],
        ['Pedro Oliveira', '5588966666666', 'Juazeiro do Norte']
    ]
    
    with open('contatos_exemplo.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(dados_csv)
    
    print("[OK] Arquivo CSV de exemplo criado: contatos_exemplo.csv")
    
    # Criar arquivo Excel de exemplo
    df_excel = pd.DataFrame(dados_csv[1:], columns=dados_csv[0])
    df_excel.to_excel('contatos_exemplo.xlsx', index=False)
    
    print("[OK] Arquivo Excel de exemplo criado: contatos_exemplo.xlsx")

def main():
    print("Demonstração do Sistema de Importação de Contatos para WhatsApp")
    print("="*70)
    
    # Criar arquivos de exemplo
    criar_arquivo_exemplo()
    
    # Inicializar o gerenciador
    gerenciador = GerenciadorContatosDemo()
    
    # Criar contatos de exemplo
    gerenciador.criar_contato_exemplo()
    
    print(f"\nContatos atuais: {len(gerenciador.lista_contatos)}")
    for contato in gerenciador.lista_contatos:
        print(f"  • {contato['nome']} - {contato['id']}")
    
    # Importar contatos de CSV
    print(f"\nImportando contatos de CSV...")
    contatos_csv = gerenciador.importar_csv('contatos_exemplo.csv', 'numero', 'nome')
    gerenciador.adicionar_contatos(contatos_csv)
    
    # Importar contatos de Excel
    print(f"\nImportando contatos de Excel...")
    contatos_excel = gerenciador.importar_excel('contatos_exemplo.xlsx', coluna_numero='numero', coluna_nome='nome')
    gerenciador.adicionar_contatos(contatos_excel)
    
    print(f"\nTotal de contatos após importação: {len(gerenciador.lista_contatos)}")
    
    # Criar uma lista de contatos específica
    ids_contatos = [c['id'] for c in gerenciador.lista_contatos[:5]]  # Pegar os primeiros 5
    lista_teste = gerenciador.criar_lista_contatos("Clientes VIP", ids_contatos)
    
    # Criar mensagem de boas-vindas
    mensagem_boas_vindas = gerenciador.criar_mensagem_boas_vindas()
    
    # Criar campanha para a lista
    campanha = gerenciador.criar_campanha_por_lista(
        "Campanha de Boas-Vindas - Clientes VIP",
        ids_contatos,
        mensagem_boas_vindas
    )
    
    # Mostrar estatísticas
    print(f"\nESTATÍSTICAS:")
    stats = gerenciador.obter_estatisticas()
    print(f"  Total de contatos: {stats['total_contatos']}")
    print(f"  Por fonte: {stats['por_fonte']}")
    print(f"  Tags mais usadas: {stats['tags_populares']}")
    
    # Exportar contatos
    gerenciador.exportar_contatos('contatos_exportados.csv', 'csv')
    gerenciador.exportar_contatos('contatos_exportados.xlsx', 'excel')
    
    print(f"\n{'='*70}")
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("="*70)
    print("\nFUNCIONALIDADES IMPLEMENTADAS:")
    print("[OK] Importacao de contatos de CSV")
    print("[OK] Importacao de contatos de Excel")
    print("[OK] Criacao de listas de contatos especificas")
    print("[OK] Criacao de campanhas por lista")
    print("[OK] Mensagem de boas-vindas configurada")
    print("[OK] Exportacao de contatos em diferentes formatos")
    print("[OK] Sistema de tags e categorizacao")
    print("[OK] Estatisticas de contatos")

    print(f"\nDICAS PARA USO:")
    print("1. Substitua os arquivos de exemplo pelos seus arquivos reais")
    print("2. Use os IDs de contatos reais que aparecem nos webhooks")
    print("3. Personalize as mensagens conforme necessario")
    print("4. Crie listas especificas para diferentes campanhas")
    print("5. Monitore as estatisticas para otimizar envios")

if __name__ == "__main__":
    main()