"""
Exemplos de uso do Stitch MCP Client

Demonstra como usar o cliente Stitch para gerar UIs, gerenciar projetos e baixar código.
"""

from core.mcp_client import StitchClient
import json


def exemplo_listar_projetos():
    """Exemplo: Listar todos os projetos"""
    print("="*70)
    print("📋 EXEMPLO 1: Listar Projetos")
    print("="*70)
    
    client = StitchClient()
    projects = client.list_projects()
    
    print(f"\n✨ Total de projetos: {len(projects)}\n")
    
    for i, proj in enumerate(projects, 1):
        print(f"🎨 Projeto {i}:")
        print(f"   Título: {proj.get('title', 'N/A')}")
        print(f"   ID: {proj.get('name', 'N/A')}")
        print(f"   Tipo: {proj.get('deviceType', 'N/A')}")
        print(f"   Criado: {proj.get('createTime', 'N/A')}")
        
        # Tema de design
        theme = proj.get('designTheme', {})
        if theme:
            print(f"   Tema:")
            print(f"     - Modo: {theme.get('colorMode', 'N/A')}")
            print(f"     - Fonte: {theme.get('font', 'N/A')}")
            print(f"     - Cor: {theme.get('customColor', 'N/A')}")
        
        # Telas
        screens = proj.get('screenInstances', [])
        if screens:
            print(f"   Telas: {len(screens)}")
        
        print()


def exemplo_detalhes_projeto():
    """Exemplo: Obter detalhes de um projeto específico"""
    print("="*70)
    print("📊 EXEMPLO 2: Detalhes de Projeto")
    print("="*70)
    
    client = StitchClient()
    
    # Primeiro, listar projetos para pegar um ID
    projects = client.list_projects()
    if not projects:
        print("❌ Nenhum projeto encontrado")
        return
    
    # Pegar o primeiro projeto
    project_id = projects[0].get('name', '')
    print(f"\n🔍 Buscando detalhes do projeto: {project_id}\n")
    
    try:
        details = client.get_project(project_id)
        print(json.dumps(details, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"⚠️ Erro ao obter detalhes: {e}")


def exemplo_listar_telas():
    """Exemplo: Listar telas de um projeto"""
    print("="*70)
    print("🖼️  EXEMPLO 3: Listar Telas de um Projeto")
    print("="*70)
    
    client = StitchClient()
    
    # Pegar primeiro projeto
    projects = client.list_projects()
    if not projects:
        print("❌ Nenhum projeto encontrado")
        return
    
    project_id = projects[0].get('name', '')
    print(f"\n📱 Listando telas do projeto: {projects[0].get('title', 'N/A')}\n")
    
    try:
        screens = client.list_screens(project_id)
        print(f"✨ Total de telas: {len(screens)}\n")
        
        for i, screen in enumerate(screens, 1):
            print(f"🖼️  Tela {i}:")
            print(f"   ID: {screen.get('id', 'N/A')}")
            print(f"   Dimensões: {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}")
            print()
    except Exception as e:
        print(f"⚠️ Erro ao listar telas: {e}")


def exemplo_gerar_tela():
    """Exemplo: Gerar nova tela a partir de prompt"""
    print("="*70)
    print("✨ EXEMPLO 4: Gerar Nova Tela")
    print("="*70)
    
    client = StitchClient()
    
    prompt = """
    Crie uma tela de login moderna com:
    - Campo de email
    - Campo de senha
    - Botão de login
    - Link para recuperar senha
    - Opção de login com Google
    - Design minimalista e elegante
    """
    
    print(f"\n📝 Prompt: {prompt.strip()}\n")
    print("🎨 Gerando tela...")
    
    try:
        result = client.generate_screen(
            prompt=prompt,
            device_type="MOBILE"
        )
        
        print("\n✅ Tela gerada com sucesso!")
        print(f"\n📊 Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erro ao gerar tela: {e}")


def exemplo_baixar_codigo():
    """Exemplo: Baixar código de uma tela"""
    print("="*70)
    print("💻 EXEMPLO 5: Baixar Código de Tela")
    print("="*70)
    
    client = StitchClient()
    
    # Pegar primeira tela do primeiro projeto
    projects = client.list_projects()
    if not projects:
        print("❌ Nenhum projeto encontrado")
        return
    
    project_id = projects[0].get('name', '')
    
    try:
        screens = client.list_screens(project_id)
        if not screens:
            print("❌ Nenhuma tela encontrada")
            return
        
        screen_id = screens[0].get('id', '')
        print(f"\n📥 Baixando código da tela: {screen_id}\n")
        
        code = client.fetch_screen_code(screen_id)
        
        print("✅ Código baixado!")
        print(f"\n📄 Tamanho: {len(code)} caracteres")
        print(f"\n💻 Primeiras 500 caracteres:")
        print("-" * 70)
        print(code[:500])
        print("-" * 70)
        
        # Salvar em arquivo
        output_file = f"screen_{screen_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"\n✅ Código salvo em: {output_file}")
        
    except Exception as e:
        print(f"❌ Erro ao baixar código: {e}")


def exemplo_ferramentas_disponiveis():
    """Exemplo: Listar ferramentas disponíveis"""
    print("="*70)
    print("🛠️  EXEMPLO 6: Ferramentas Disponíveis")
    print("="*70)
    
    client = StitchClient()
    tools = client.list_available_tools()
    
    print(f"\n✨ Total de ferramentas: {len(tools)}\n")
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['name']}")
        print(f"   📝 {tool['description']}")
        print()


if __name__ == "__main__":
    import sys
    
    exemplos = {
        "1": ("Listar Projetos", exemplo_listar_projetos),
        "2": ("Detalhes de Projeto", exemplo_detalhes_projeto),
        "3": ("Listar Telas", exemplo_listar_telas),
        "4": ("Gerar Nova Tela", exemplo_gerar_tela),
        "5": ("Baixar Código", exemplo_baixar_codigo),
        "6": ("Ferramentas Disponíveis", exemplo_ferramentas_disponiveis),
    }
    
    if len(sys.argv) > 1:
        exemplo_num = sys.argv[1]
        if exemplo_num in exemplos:
            nome, func = exemplos[exemplo_num]
            print(f"\n🚀 Executando: {nome}\n")
            func()
        else:
            print(f"❌ Exemplo '{exemplo_num}' não encontrado")
    else:
        print("\n" + "="*70)
        print("🎨 EXEMPLOS DE USO DO STITCH MCP CLIENT")
        print("="*70)
        print("\nUso: python3 stitch_examples.py <numero_exemplo>")
        print("\nExemplos disponíveis:\n")
        
        for num, (nome, _) in exemplos.items():
            print(f"  {num}. {nome}")
        
        print("\nExemplo:")
        print("  python3 stitch_examples.py 1")
        print()
