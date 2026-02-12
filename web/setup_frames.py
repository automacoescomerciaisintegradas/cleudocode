#!/usr/bin/env python3
"""
Script para organizar frames WebP para a página de contato
Automações Comerciais Integradas

Este script ajuda a:
1. Renomear frames para o formato correto (frame-001.webp, frame-002.webp, etc.)
2. Verificar se todos os frames estão presentes
3. Criar a estrutura de pastas necessária
"""

import os
import sys
import shutil
from pathlib import Path


def create_frames_directory():
    """Cria o diretório para armazenar os frames"""
    frames_dir = Path("web/frames")
    frames_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Diretório criado: {frames_dir.absolute()}")
    return frames_dir


def rename_frames(source_dir, target_dir, prefix="frame-", padding=3):
    """
    Renomeia frames para o formato padronizado
    
    Args:
        source_dir: Diretório contendo os frames originais
        target_dir: Diretório de destino
        prefix: Prefixo para os nomes dos arquivos
        padding: Número de dígitos para padding (3 = 001, 4 = 0001)
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"❌ Erro: Diretório {source_dir} não encontrado!")
        return False
    
    # Encontra todos os arquivos WebP
    webp_files = sorted(source_path.glob("*.webp"))
    
    if not webp_files:
        print(f"❌ Nenhum arquivo WebP encontrado em {source_dir}")
        return False
    
    print(f"📁 Encontrados {len(webp_files)} arquivos WebP")
    print(f"🔄 Renomeando para formato: {prefix}XXX.webp\n")
    
    for index, file_path in enumerate(webp_files, start=1):
        # Gera novo nome com padding
        new_name = f"{prefix}{str(index).zfill(padding)}.webp"
        new_path = target_dir / new_name
        
        # Copia arquivo com novo nome
        shutil.copy2(file_path, new_path)
        print(f"  {index:3d}. {file_path.name:40s} → {new_name}")
    
    print(f"\n✅ {len(webp_files)} frames renomeados com sucesso!")
    return True


def verify_frames(frames_dir, total_frames, prefix="frame-", padding=3):
    """Verifica se todos os frames esperados estão presentes"""
    frames_path = Path(frames_dir)
    
    print(f"\n🔍 Verificando {total_frames} frames em {frames_dir}...\n")
    
    missing_frames = []
    
    for i in range(1, total_frames + 1):
        frame_name = f"{prefix}{str(i).zfill(padding)}.webp"
        frame_path = frames_path / frame_name
        
        if not frame_path.exists():
            missing_frames.append(frame_name)
            print(f"  ❌ {frame_name} - FALTANDO")
        else:
            # Verifica tamanho do arquivo
            size_kb = frame_path.stat().st_size / 1024
            print(f"  ✅ {frame_name} - {size_kb:.1f} KB")
    
    if missing_frames:
        print(f"\n⚠️  {len(missing_frames)} frames faltando:")
        for frame in missing_frames[:10]:  # Mostra apenas os primeiros 10
            print(f"     - {frame}")
        if len(missing_frames) > 10:
            print(f"     ... e mais {len(missing_frames) - 10}")
        return False
    else:
        print(f"\n✅ Todos os {total_frames} frames estão presentes!")
        return True


def get_total_size(frames_dir):
    """Calcula o tamanho total de todos os frames"""
    frames_path = Path(frames_dir)
    total_size = sum(f.stat().st_size for f in frames_path.glob("*.webp"))
    return total_size


def main():
    print("=" * 60)
    print("  SETUP DE FRAMES PARA PÁGINA DE CONTATO")
    print("  Automações Comerciais Integradas")
    print("=" * 60)
    print()
    
    # Menu de opções
    print("Escolha uma opção:")
    print("  1. Criar diretório de frames")
    print("  2. Renomear frames de outro diretório")
    print("  3. Verificar frames existentes")
    print("  4. Estatísticas dos frames")
    print("  0. Sair")
    print()
    
    choice = input("Opção: ").strip()
    
    if choice == "1":
        frames_dir = create_frames_directory()
        print(f"\n📝 Próximo passo: Copie seus frames WebP para {frames_dir.absolute()}")
        print(f"   Ou use a opção 2 para renomear frames de outro diretório")
    
    elif choice == "2":
        source = input("Diretório de origem (com os frames originais): ").strip()
        target = create_frames_directory()
        
        print("\nConfigurações:")
        prefix = input("Prefixo dos arquivos (padrão: frame-): ").strip() or "frame-"
        padding = input("Dígitos de padding (padrão: 3 para 001): ").strip() or "3"
        padding = int(padding)
        
        rename_frames(source, target, prefix, padding)
    
    elif choice == "3":
        frames_dir = input("Diretório dos frames (padrão: web/frames): ").strip() or "web/frames"
        total = input("Número total de frames (padrão: 120): ").strip() or "120"
        total = int(total)
        
        prefix = input("Prefixo dos arquivos (padrão: frame-): ").strip() or "frame-"
        padding = input("Dígitos de padding (padrão: 3): ").strip() or "3"
        padding = int(padding)
        
        verify_frames(frames_dir, total, prefix, padding)
    
    elif choice == "4":
        frames_dir = input("Diretório dos frames (padrão: web/frames): ").strip() or "web/frames"
        frames_path = Path(frames_dir)
        
        if not frames_path.exists():
            print(f"❌ Diretório {frames_dir} não encontrado!")
            return
        
        webp_files = list(frames_path.glob("*.webp"))
        
        if not webp_files:
            print(f"❌ Nenhum arquivo WebP encontrado em {frames_dir}")
            return
        
        total_size = get_total_size(frames_dir)
        avg_size = total_size / len(webp_files) if webp_files else 0
        
        print(f"\n📊 Estatísticas:")
        print(f"  Total de frames: {len(webp_files)}")
        print(f"  Tamanho total: {total_size / (1024 * 1024):.2f} MB")
        print(f"  Tamanho médio por frame: {avg_size / 1024:.1f} KB")
        print(f"  Menor frame: {min(f.stat().st_size for f in webp_files) / 1024:.1f} KB")
        print(f"  Maior frame: {max(f.stat().st_size for f in webp_files) / 1024:.1f} KB")
    
    elif choice == "0":
        print("👋 Até logo!")
        return
    
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
