"""
Script de Teste - Design Tokens Cleudocode
Execute este script para verificar se os tokens foram implementados corretamente

Uso:
    python test_design_tokens.py
"""

def test_import():
    """Testa se o módulo design_tokens pode ser importado"""
    try:
        import design_tokens
        print("✅ Módulo design_tokens importado com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar design_tokens: {e}")
        return False

def test_colors():
    """Testa se as cores estão definidas corretamente"""
    try:
        from design_tokens import COLORS
        
        assert COLORS['brand']['primary'] == '#FF5F5F', "Cor primária incorreta"
        assert COLORS['brand']['secondary'] == '#6366F1', "Cor secundária incorreta"
        assert COLORS['background']['primary'] == '#080808', "Fundo principal incorreto"
        
        print("✅ Cores definidas corretamente")
        print(f"   - Primária: {COLORS['brand']['primary']}")
        print(f"   - Secundária: {COLORS['brand']['secondary']}")
        print(f"   - Fundo: {COLORS['background']['primary']}")
        return True
    except AssertionError as e:
        print(f"❌ Erro nas cores: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_fonts():
    """Testa se as fontes estão definidas"""
    try:
        from design_tokens import FONTS
        
        assert 'Inter' in FONTS['family']['sans'], "Fonte Inter não encontrada"
        assert FONTS['size']['7xl'] == '72px', "Tamanho 7xl incorreto"
        assert FONTS['weight']['black'] == 900, "Peso black incorreto"
        
        print("✅ Fontes definidas corretamente")
        print(f"   - Família: Inter")
        print(f"   - Tamanho 7xl: {FONTS['size']['7xl']}")
        print(f"   - Peso black: {FONTS['weight']['black']}")
        return True
    except AssertionError as e:
        print(f"❌ Erro nas fontes: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_css_generation():
    """Testa se a função generate_streamlit_css funciona"""
    try:
        from design_tokens import generate_streamlit_css
        
        css = generate_streamlit_css()
        
        assert isinstance(css, str), "CSS deve ser string"
        assert len(css) > 1000, "CSS muito curto"
        assert '--brand-primary' in css, "Variável CSS --brand-primary não encontrada"
        assert '#FF5F5F' in css, "Cor primária não encontrada no CSS"
        assert 'Inter' in css, "Fonte Inter não encontrada no CSS"
        
        print("✅ Função generate_streamlit_css() funciona corretamente")
        print(f"   - CSS gerado: {len(css)} caracteres")
        print(f"   - Contém variáveis CSS: Sim")
        print(f"   - Contém fonte Inter: Sim")
        return True
    except AssertionError as e:
        print(f"❌ Erro na geração de CSS: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_all_tokens():
    """Testa se todos os dicionários de tokens existem"""
    try:
        from design_tokens import (
            COLORS, FONTS, SPACING, BORDER_RADIUS, 
            SHADOWS, TRANSITIONS, Z_INDEX
        )
        
        tokens = {
            'COLORS': COLORS,
            'FONTS': FONTS,
            'SPACING': SPACING,
            'BORDER_RADIUS': BORDER_RADIUS,
            'SHADOWS': SHADOWS,
            'TRANSITIONS': TRANSITIONS,
            'Z_INDEX': Z_INDEX
        }
        
        print("✅ Todos os dicionários de tokens existem:")
        for name, token_dict in tokens.items():
            keys = list(token_dict.keys())
            print(f"   - {name}: {len(keys)} categorias")
        
        return True
    except ImportError as e:
        print(f"❌ Token ausente: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DE DESIGN TOKENS - CLEUDOCODE")
    print("=" * 60)
    print()
    
    tests = [
        ("Importação do módulo", test_import),
        ("Cores", test_colors),
        ("Fontes", test_fonts),
        ("Geração de CSS", test_css_generation),
        ("Todos os tokens", test_all_tokens)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Testando: {name}")
        print("-" * 60)
        result = test_func()
        results.append(result)
        print()
    
    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ SUCESSO! Todos os {total} testes passaram!")
        print()
        print("Os design tokens estão prontos para uso.")
        print("Execute o Streamlit app para ver as mudanças:")
        print()
        print("  streamlit run web_app.py")
        print()
        return 0
    else:
        print(f"❌ FALHA! {passed}/{total} testes passaram")
        print()
        print("Verifique os erros acima e corrija antes de usar.")
        return 1

if __name__ == "__main__":
    exit(main())
