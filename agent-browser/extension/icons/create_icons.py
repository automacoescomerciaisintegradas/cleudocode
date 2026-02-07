#!/usr/bin/env python3
"""
Script para criar ícones da extensão Cleudocode Browser Relay
"""

from PIL import Image, ImageDraw
import os

def create_icon(size, active=False):
    """Cria um ícone do Cleudocode"""
    # Cores
    bg_color = (10, 10, 10, 255)  # Fundo escuro
    primary_color = (255, 95, 95, 255) if not active else (16, 185, 129, 255)  # Salmon ou Verde
    secondary_color = (255, 255, 255, 255)  # Branco
    
    # Cria imagem
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calcula dimensões baseadas no tamanho
    margin = size // 8
    inner_size = size - (margin * 2)
    center = size // 2
    
    # Desenha círculo de fundo
    circle_margin = size // 6
    draw.ellipse([
        circle_margin, circle_margin,
        size - circle_margin, size - circle_margin
    ], fill=primary_color)
    
    # Desenha símbolo do terminal (>)
    symbol_size = inner_size // 3
    symbol_x = center - symbol_size // 4
    symbol_y = center - symbol_size // 2
    
    # Desenha ">" como triângulo
    points = [
        (symbol_x, symbol_y),
        (symbol_x + symbol_size, center),
        (symbol_x, symbol_y + symbol_size)
    ]
    draw.polygon(points, fill=secondary_color)
    
    return img

def main():
    """Cria todos os ícones necessários"""
    # Cria diretório se não existir
    os.makedirs('icons', exist_ok=True)
    
    sizes = [16, 32, 48, 128]
    
    # Ícones normais
    for size in sizes:
        icon = create_icon(size, active=False)
        icon.save(f'icons/icon{size}.png', 'PNG')
        print(f'Criado: icon{size}.png')
    
    # Ícones ativos (quando conectado)
    for size in sizes:
        icon = create_icon(size, active=True)
        icon.save(f'icons/icon{size}_active.png', 'PNG')
        print(f'Criado: icon{size}_active.png')
    
    print('Todos os ícones foram criados com sucesso!')

if __name__ == '__main__':
    main()