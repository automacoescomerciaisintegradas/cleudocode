# Cleudocode Browser Relay Extension

Extensão do Chrome para conectar o Cleudocode Gateway ao navegador, permitindo automação de abas.

## Instalação (Modo Desenvolvedor)

1. **Abra o Chrome** e navegue para `chrome://extensions/`

2. **Ative o "Modo do desenvolvedor"** no canto superior direito

3. **Clique em "Carregar sem compactação"**

4. **Selecione a pasta** `agent-browser/extension/`

5. **Fixe a extensão** na barra de ferramentas

## Como Usar

1. **Inicie o Cleudocode Gateway** com controle de navegador habilitado
2. **Verifique se o relay server** está acessível em `http://127.0.0.1:18902/`
3. **Clique no ícone da extensão** em qualquer aba
4. **Clique em "Conectar Aba"** para permitir automação
5. **O ícone ficará verde** quando conectado

## Recursos

- ✅ Conexão com Gateway via relay server
- ✅ Controle de abas individuais
- ✅ Execução de comandos JavaScript
- ✅ Automação de elementos da página
- ✅ Status visual da conexão
- ✅ Configuração de porta personalizada

## Arquivos da Extensão

- `manifest.json` - Configuração da extensão
- `background.js` - Script de background (service worker)
- `popup.html` - Interface do usuário
- `popup.js` - Lógica da interface
- `content.js` - Script injetado nas páginas
- `icons/` - Ícones da extensão

## Permissões Necessárias

- `activeTab` - Acesso à aba ativa
- `tabs` - Gerenciamento de abas
- `storage` - Armazenamento de configurações
- `debugger` - Controle via Chrome DevTools Protocol
- `<all_urls>` - Acesso a todos os sites

## Configuração do Gateway

Para usar a extensão, o Gateway deve estar configurado com:

```bash
# Porta padrão do relay server
CLEUDOCODE_BROWSER_RELAY_PORT=18902

# Habilitar controle de navegador
CLEUDOCODE_BROWSER_CONTROL=true
```

## Solução de Problemas

### Gateway Desconectado
- Verifique se o Gateway está rodando
- Confirme se a porta 18902 está acessível
- Teste: `curl http://127.0.0.1:18902/status`

### Aba Não Conecta
- Recarregue a página
- Desative/ative a extensão
- Verifique permissões no Chrome

### Comandos Não Executam
- Verifique se a aba está conectada
- Confirme se o debugger está ativo
- Veja o console para erros

## Desenvolvimento

Para modificar a extensão:

1. Edite os arquivos necessários
2. Vá para `chrome://extensions/`
3. Clique no botão "Recarregar" da extensão
4. Teste as mudanças

## Segurança

- A extensão só funciona com o Gateway local
- Conexões são feitas apenas para `127.0.0.1`
- Nenhum dado é enviado para servidores externos
- Controle total sobre quais abas conectar