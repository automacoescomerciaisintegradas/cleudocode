# TODO: Transformar Cleudocode em OpenClaw-like

## Fase 1: Estrutura Base ✅
- [x] Criar arquivos UCM (context.md, todos.md, insights.md)
- [x] Criar diretório ~/.cleudocode/
- [x] Criar config.yaml base
- [x] Gerar gateway token seguro
- [x] Criar estrutura de workspace

## Fase 2: CLI Aprimorado ⏳
- [x] Adicionar comando `cleudocode dashboard`
- [x] Implementar autenticação via token no CLI
- [x] Adicionar comando `cleudocode init` (setup inicial) ✅
- [ ] Adicionar comando `cleudocode skills` (gerenciar skills)
- [ ] Adicionar comando `cleudocode chat` (chat direto no terminal)
- [x] Melhorar comando `cleudocode config` para editar config.yaml ✅

## Fase 3: Sistema de Configuração ✅
- [x] Criar parser de config.yaml
- [x] Migrar configurações de .env para config.yaml
- [x] Implementar validação de configuração
- [x] Adicionar suporte a múltiplos perfis

## Fase 4: Dashboard com Autenticação ✅
- [x] Implementar autenticação via token no dashboard
- [x] Criar endpoint /auth com validação de token
- [x] Adicionar middleware de autenticação
- [x] Criar página de login/token input
- [x] Implementar auto-login via URL com token

## Fase 5: Gateway Multi-Canal
- [ ] Refatorar gateway para suportar múltiplos canais
- [ ] Implementar adaptadores para cada canal (Telegram, Discord, WhatsApp)
- [ ] Adicionar sistema de roteamento de mensagens
- [ ] Implementar fila de mensagens

## Fase 6: Skills/Plugins System
- [ ] Criar estrutura de skills
- [ ] Implementar skill loader
- [ ] Adicionar marketplace de skills
- [ ] Criar sistema de versionamento de skills
- [ ] Implementar sandboxing para skills

## Fase 7: Melhorias de UX
- [ ] Adicionar progress bars e spinners no CLI
- [ ] Melhorar mensagens de erro
- [ ] Adicionar modo verbose/debug
- [ ] Criar wizard interativo de setup
- [ ] Adicionar auto-complete para comandos

## Fase 8: Documentação
- [ ] Atualizar README.md
- [ ] Criar guia de início rápido
- [ ] Documentar API do gateway
- [ ] Criar guia de desenvolvimento de skills
- [ ] Adicionar exemplos de uso

## Prioridade Imediata (Hoje)
1. Criar estrutura ~/.cleudocode/
2. Implementar config.yaml
3. Gerar gateway token
4. Adicionar comando `cleudocode dashboard`
5. Implementar autenticação no dashboard
