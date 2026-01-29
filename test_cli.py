#!/usr/bin/env python3
"""
Script de teste para o CLI do Cleudocode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cli():
    try:
        # Testar importação
        from cli.main import cli
        print("[OK] Importacao do CLI bem sucedida")

        # Testar se é um grupo do Click
        import click
        if isinstance(cli, click.Group):
            print("[OK] Objeto CLI é um grupo do Click")
        else:
            print("[?] Objeto CLI não é um grupo do Click, mas foi importado")

        # Listar comandos
        if hasattr(cli, 'commands'):
            commands = list(cli.commands.keys())
            print(f"[OK] Comandos disponiveis: {commands}")
        else:
            print("[?] Nao foi possivel listar comandos")

        return True

    except ImportError as e:
        print(f"[ERRO] Erro de importacao: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cli()
    if success:
        print("\n[OK] Teste do CLI concluido com sucesso!")
    else:
        print("\n[ERRO] Teste do CLI falhou!")
        sys.exit(1)