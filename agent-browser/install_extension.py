#!/usr/bin/env python3
"""
Script de instalação da extensão Cleudocode Browser Relay
"""

import os
import sys
import json
import shutil
from pathlib import Path

def create_simple_icons():
    """Cria ícones simples usando SVG"""
    
    # SVG base para o ícone
    svg_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" fill="#0a0a0a" rx="{radius}"/>
  <circle cx="{center}" cy="{center}" r="{circle_r}" fill="{color}"/>
  <polygon points="{arrow_points}" fill="white"/>
</svg>'''
    
    sizes = [16, 32, 48, 128]
    colors = {
        'normal': '#FF5F5F',
        'active': '#10b981'
    }
    
    icons_dir = Path('extension/icons')
    icons_dir.mkdir(exist_ok=True)
    
    for size in sizes:
        center = size // 2
        radius = size // 8
        circle_r = size // 3
        arrow_size = size // 6
        arrow_x = center - arrow_size // 2
        arrow_y = center - arrow_size // 2
        
        # Pontos do triângulo (seta >)
        arrow_points = f"{arrow_x},{arrow_y} {arrow_x + arrow_size},{center} {arrow_x},{arrow_y + arrow_size}"
        
        for state, color in colors.items():
            svg_content = svg_template.format(
                size=size,
                center=center,
                radius=radius,
                circle_r=circle_r,
                color=color,
                arrow_points=arrow_points
            )
            
            filename = f'icon{size}.svg' if state == 'normal' else f'icon{size}_active.svg'
            svg_path = icons_dir / filename
            
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            
            print(f'✅ Criado: {filename}')
    
    print(f'📁 Ícones salvos em: {icons_dir.absolute()}')

def get_extension_path():
    """Retorna o caminho absoluto da extensão"""
    extension_dir = Path('extension').resolve()
    return str(extension_dir)

def validate_extension():
    """Valida se todos os arquivos necessários existem"""
    extension_dir = Path('extension')
    required_files = [
        'manifest.json',
        'background.js',
        'popup.html',
        'popup.js',
        'content.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not (extension_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os arquivos necessários estão presentes")
    return True

def show_installation_instructions():
    """Mostra instruções de instalação"""
    extension_path = get_extension_path()
    
    print("\n" + "="*60)
    print("🚀 CLEUDOCODE BROWSER RELAY EXTENSION")
    print("="*60)
    print()
    print("📍 Caminho da extensão:")
    print(f"   {extension_path}")
    print()
    print("📋 INSTRUÇÕES DE INSTALAÇÃO:")
    print()
    print("1. Abra o Google Chrome")
    print("2. Navegue para: chrome://extensions/")
    print("3. Ative o 'Modo do desenvolvedor' (canto superior direito)")
    print("4. Clique em 'Carregar sem compactação'")
    print("5. Selecione a pasta:")
    print(f"   {extension_path}")
    print("6. Fixe a extensão na barra de ferramentas")
    print()
    print("🔧 CONFIGURAÇÃO:")
    print()
    print("1. Inicie o Cleudocode Gateway")
    print("2. Verifique se o relay server está em: http://127.0.0.1:18902/")
    print("3. Clique no ícone da extensão em qualquer aba")
    print("4. Clique em 'Conectar Aba' para habilitar automação")
    print()
    print("✅ A extensão está pronta para uso!")
    print("="*60)

def main():
    """Função principal"""
    print("🔧 Configurando Cleudocode Browser Relay Extension...")
    
    # Cria ícones
    print("\n📦 Criando ícones...")
    create_simple_icons()
    
    # Valida extensão
    print("\n🔍 Validando arquivos...")
    if not validate_extension():
        sys.exit(1)
    
    # Mostra instruções
    show_installation_instructions()
    
    # Salva caminho para uso posterior
    extension_path = get_extension_path()
    with open('extension_path.txt', 'w') as f:
        f.write(extension_path)
    
    print(f"\n💾 Caminho salvo em: extension_path.txt")

if __name__ == '__main__':
    main()