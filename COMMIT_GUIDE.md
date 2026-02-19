# Guia de Commits para o Projeto Cleudocode

Este guia descreve como fazer commits de forma eficaz no projeto Cleudocode, seguindo as melhores práticas de versionamento e documentação.

## Sumário

1. [Formato de Commit](#formato-de-commit)
2. [Tipos de Commits](#tipos-de-commits)
3. [Escopo do Commit](#escopo-do-commit)
4. [Mensagem do Commit](#mensagem-do-commit)
5. [Exemplos de Commits](#exemplos-de-commits)
6. [Scripts de Commit](#scripts-de-commit)
7. [Boas Práticas](#boas-práticas)

## Formato de Commit

O formato de commit segue a convenção do Angular e é estruturado da seguinte forma:

```
<tipo>(<escopo>): <assunto>

<corpo>

<footer>
```

## Tipos de Commits

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Alterações que não afetam o significado do código (espaço em branco, formatação, ponto e vírgula ausente, etc)
- `refactor`: Refatoração de código
- `perf`: Melhoria de performance
- `test`: Adição ou modificação de testes
- `chore`: Atualizações de tarefas de build, configurações auxiliares, etc

## Escopo do Commit

O escopo indica a parte do código que está sendo alterada. Exemplos comuns:

- `cli`: Componentes da interface de linha de comando
- `web`: Componentes da interface web
- `api`: Componentes da API
- `gateway`: Componentes de gateway
- `daemon`: Componentes do daemon
- `llm`: Componentes de provedores de LLM
- `config`: Configurações e variáveis de ambiente
- `docker`: Configurações do Docker
- `docs`: Documentação

## Mensagem do Commit

- Use o imperativo no título do commit: "Adiciona", "Corrige", "Remove", etc.
- Limite o título a 50 caracteres
- Use caixa baixa, exceto quando for necessário usar maiúsculas
- Não finalize o título com ponto
- Adicione uma linha em branco após o título
- Escreva corpo explicativo com quebras de linha em ~72 caracteres
- Explique o quê e o porquê, não o como

## Exemplos de Commits

### Bom

```
feat(cli): adiciona comando de status para mostrar status dos agentes

Adiciona o comando `status` ao CLI que mostra o status detalhado
dos agentes em execução, incluindo métricas de desempenho e
progresso das tarefas.

Closes #123
```

```
fix(web): corrige falha na inicialização do servidor web

Corrige problema onde o servidor web falhava ao iniciar devido
à importação ausente do módulo token_usage_tracker.
```

```
docs(readme): atualiza instruções de instalação para Windows e WSL

Expande o README com instruções detalhadas para instalação no
Windows usando WSL e nativamente, incluindo pré-requisitos e
passos de configuração.
```

### Ruim

```
fix: fix bug
```

```
added some stuff to readme
```

## Scripts de Commit

### Script de Commit Automático

Para facilitar os commits, você pode usar o seguinte script:

```bash
#!/bin/bash
# commit.sh - Script de commit automatizado

echo "Script de Commit Automatizado do Cleudocode"
echo "========================================="

# Pergunta pelo tipo de commit
echo "Tipo de commit:"
echo "1) feat - Nova funcionalidade"
echo "2) fix - Correção de bug"
echo "3) docs - Documentação"
echo "4) style - Estilo/formato"
echo "5) refactor - Refatoração"
echo "6) perf - Performance"
echo "7) test - Testes"
echo "8) chore - Tarefas auxiliares"
read -p "Escolha (1-8): " type_choice

case $type_choice in
    1) TYPE="feat";;
    2) TYPE="fix";;
    3) TYPE="docs";;
    4) TYPE="style";;
    5) TYPE="refactor";;
    6) TYPE="perf";;
    7) TYPE="test";;
    8) TYPE="chore";;
    *) echo "Opção inválida"; exit 1;;
esac

# Pergunta pelo escopo
read -p "Escopo (opcional, ex: cli, web, api): " SCOPE

# Pergunta pela mensagem
read -p "Mensagem curta: " SUBJECT

# Monta o commit
if [ -z "$SCOPE" ]; then
    COMMIT_MSG="$TYPE: $SUBJECT"
else
    COMMIT_MSG="$TYPE($SCOPE): $SUBJECT"
fi

# Adiciona arquivos modificados
git add .

# Faz o commit
git commit -m "$COMMIT_MSG"

echo "Commit realizado: $COMMIT_MSG"
echo "Lembre-se de fazer git push para enviar as alterações"
```

### Script de Push com Verificação

```bash
#!/bin/bash
# push.sh - Script de push com verificação

echo "Script de Push com Verificação do Cleudocode"
echo "============================================"

# Verifica o status do repositório
echo "Verificando status do repositório..."
git status

# Pergunta confirmação
read -p "Deseja continuar com o push? (s/n): " confirm
if [[ $confirm =~ ^[Ss]$ ]]; then
    echo "Realizando push..."
    git push origin $(git branch --show-current)
    echo "Push concluído!"
else
    echo "Operação cancelada."
fi
```

## Boas Práticas

### Antes de Fazer um Commit

1. **Teste suas alterações**: Certifique-se de que seu código funciona como esperado
2. **Verifique o estilo**: Siga as convenções de estilo do projeto
3. **Documente mudanças significativas**: Atualize a documentação quando necessário
4. **Verifique conflitos potenciais**: Mantenha sua branch atualizada com a main

### Organização de Commits

1. **Commits atômicos**: Cada commit deve representar uma única mudança lógica
2. **Séries lógicas**: Organize commits em séries lógicas para facilitar revisão
3. **Evite commits grandes**: Divida alterações grandes em commits menores e mais focados
4. **Mantenha histórico limpo**: Use `git rebase -i` para reorganizar commits se necessário

### Workflow de Contribuição

1. Crie uma branch a partir da main: `git checkout -b feature/nome-da-feature`
2. Faça suas alterações e commits com mensagens descritivas
3. Atualize sua branch com a main: `git rebase main`
4. Faça push para sua branch: `git push origin feature/nome-da-feature`
5. Abra um Pull Request com descrição clara das alterações

## Mensagens de Commit Comuns

Para facilitar, aqui estão algumas frases comuns usadas em commits:

- `feat(cli): adiciona comando de status`
- `fix(web): corrige falha na inicialização`
- `docs(readme): atualiza instruções de instalação`
- `refactor(api): melhora estrutura de autenticação`
- `perf(daemon): otimiza uso de memória`
- `test(gateway): adiciona testes para validação de token`
- `chore(config): atualiza variáveis de ambiente`

## Convenções Adicionais

- Use prefixos para indicar o impacto: `[BREAKING]` para mudanças incompatíveis
- Referencie issues com `Closes #123` ou `Fixes #123`
- Use `[WIP]` para trabalhos em andamento (Work In Progress)
- Mantenha consistência com commits anteriores do projeto

---

© **Automações Comerciais Integradas! 2026** ⚙️ Todos os direitos reservados.
[contato@automacoescomerciais.com.br](mailto:contato@automacoescomerciais.com.br)
[GitHub Cleudocode](https://github.com/automacoescomerciaisintegradas/cleudocode)