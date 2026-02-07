# Contexto da Execução do Agente Cleudocode

## Objetivo
Realizar instalação e configuração de ponta a ponta do Cleudocode, e construir o "Controle de Missão": um esquadrão de agentes de IA autônomos inspirados na arquitetura de pbteja1998.

## Premissas
- Host: Ubuntu 24.04 LTS (esperado)
- Container Engine: Docker com Compose v2
- Repositório: cleudocode/cleudocode

## Regras de Ouro
1. **STOP ON ERROR**: Qualquer código de saída != 0 deve abortar o processo imediatamente. Reportar comando, erro e recomendação.
2. **ZERO SECRETS**: Nunca colar chaves de API, senhas ou tokens no chat. Usar arquivos locais protegidos ou input interativo.
3. **LOGGING**: Registrar decisões em `insights.md`. Redigir segredos nos logs.
4. **PERMISSÕES**: Assumir ambiente sem systemd se necessário; usar arquivos com chmod 600 para segredos.

## Caminho UCM
Ajustado para `/root/cleudocode/ucm` devido a restrições de workspace da ferramenta.

