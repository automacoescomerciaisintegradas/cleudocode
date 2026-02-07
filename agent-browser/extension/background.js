// Cleudocode Browser Relay - Background Script
// Gerencia conexões com o Gateway e controle de abas

class CleudocodeRelay {
  constructor() {
    this.relayPort = 18902;
    this.relayUrl = `http://127.0.0.1:${this.relayPort}`;
    this.connectedTabs = new Set();
    this.debuggerSessions = new Map();

    this.init();
  }

  init() {
    // Listener para mensagens do popup e content scripts
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Mantém o canal aberto para resposta assíncrona
    });

    // Listener para quando abas são fechadas
    chrome.tabs.onRemoved.addListener((tabId) => {
      this.disconnectTab(tabId);
    });

    // Listener para mudanças de URL
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && this.connectedTabs.has(tabId)) {
        this.notifyGateway('tab_updated', { tabId, url: tab.url });
      }
    });

    console.log('Cleudocode Browser Relay iniciado');
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'connect_tab':
          await this.connectTab(message.tabId);
          sendResponse({ success: true });
          break;

        case 'disconnect_tab':
          await this.disconnectTab(message.tabId);
          sendResponse({ success: true });
          break;

        case 'get_status':
          const status = await this.getStatus();
          sendResponse(status);
          break;

        case 'execute_command':
          const result = await this.executeCommand(message.tabId, message.command);
          sendResponse(result);
          break;

        default:
          sendResponse({ error: 'Ação desconhecida' });
      }
    } catch (error) {
      console.error('Erro ao processar mensagem:', error);
      sendResponse({ error: error.message });
    }
  }

  async connectTab(tabId) {
    try {
      // Conecta o debugger à aba
      await chrome.debugger.attach({ tabId }, '1.3');

      // Habilita domínios necessários
      await chrome.debugger.sendCommand({ tabId }, 'Runtime.enable');
      await chrome.debugger.sendCommand({ tabId }, 'Page.enable');
      await chrome.debugger.sendCommand({ tabId }, 'DOM.enable');

      this.connectedTabs.add(tabId);
      this.debuggerSessions.set(tabId, { connected: true, timestamp: Date.now() });

      // Notifica o Gateway
      await this.notifyGateway('tab_connected', { tabId });

      console.log(`Aba ${tabId} conectada ao Cleudocode`);

      // Atualiza o ícone da extensão
      chrome.action.setIcon({
        tabId,
        path: {
          16: 'icons/icon16_active.png',
          32: 'icons/icon32_active.png',
          48: 'icons/icon48_active.png',
          128: 'icons/icon128_active.png'
        }
      });

    } catch (error) {
      console.error(`Erro ao conectar aba ${tabId}:`, error);
      throw error;
    }
  }

  async disconnectTab(tabId) {
    try {
      if (this.connectedTabs.has(tabId)) {
        // Desconecta o debugger
        await chrome.debugger.detach({ tabId });

        this.connectedTabs.delete(tabId);
        this.debuggerSessions.delete(tabId);

        // Notifica o Gateway
        await this.notifyGateway('tab_disconnected', { tabId });

        console.log(`Aba ${tabId} desconectada do Cleudocode`);

        // Restaura o ícone padrão
        chrome.action.setIcon({
          tabId,
          path: {
            16: 'icons/icon16.png',
            32: 'icons/icon32.png',
            48: 'icons/icon48.png',
            128: 'icons/icon128.png'
          }
        });
      }
    } catch (error) {
      console.error(`Erro ao desconectar aba ${tabId}:`, error);
    }
  }

  async getStatus() {
    try {
      const response = await fetch(`${this.relayUrl}/status`);
      const gatewayStatus = response.ok ? await response.json() : null;

      return {
        relay_connected: response.ok,
        gateway_status: gatewayStatus,
        connected_tabs: Array.from(this.connectedTabs),
        relay_url: this.relayUrl
      };
    } catch (error) {
      return {
        relay_connected: false,
        error: error.message,
        connected_tabs: Array.from(this.connectedTabs),
        relay_url: this.relayUrl
      };
    }
  }

  async executeCommand(tabId, command) {
    try {
      if (!this.connectedTabs.has(tabId)) {
        throw new Error('Aba não está conectada');
      }

      // Executa comando via Chrome DevTools Protocol
      const result = await chrome.debugger.sendCommand(
        { tabId },
        'Runtime.evaluate',
        {
          expression: command,
          returnByValue: true,
          awaitPromise: true
        }
      );

      return {
        success: true,
        result: result.result.value,
        type: result.result.type
      };

    } catch (error) {
      console.error(`Erro ao executar comando na aba ${tabId}:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async notifyGateway(event, data) {
    try {
      await fetch(`${this.relayUrl}/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          event,
          data,
          timestamp: Date.now()
        })
      });
    } catch (error) {
      console.error('Erro ao notificar Gateway:', error);
    }
  }
}

// Inicializa o relay
const relay = new CleudocodeRelay();