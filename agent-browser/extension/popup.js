// Cleudocode Browser Relay - Popup Script
// Interface do usuário para controlar a conexão

class PopupController {
  constructor() {
    this.currentTabId = null;
    this.isTabConnected = false;
    this.isGatewayConnected = false;
    
    this.init();
  }

  async init() {
    // Elementos da interface
    this.elements = {
      gatewayStatus: document.getElementById('gateway-status'),
      tabStatus: document.getElementById('tab-status'),
      relayPort: document.getElementById('relay-port'),
      toggleBtn: document.getElementById('btn-toggle'),
      refreshBtn: document.getElementById('btn-refresh'),
      portInput: document.getElementById('relay-port-input')
    };

    // Event listeners
    this.elements.toggleBtn.addEventListener('click', () => this.toggleConnection());
    this.elements.refreshBtn.addEventListener('click', () => this.refreshStatus());
    this.elements.portInput.addEventListener('change', () => this.updatePort());

    // Carrega configurações salvas
    await this.loadSettings();
    
    // Obtém a aba atual
    await this.getCurrentTab();
    
    // Atualiza status inicial
    await this.refreshStatus();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get(['relayPort']);
      if (result.relayPort) {
        this.elements.portInput.value = result.relayPort;
        this.elements.relayPort.textContent = result.relayPort;
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    }
  }

  async updatePort() {
    const port = parseInt(this.elements.portInput.value);
    if (port >= 1024 && port <= 65535) {
      try {
        await chrome.storage.sync.set({ relayPort: port });
        this.elements.relayPort.textContent = port;
        
        // Atualiza status com nova porta
        await this.refreshStatus();
      } catch (error) {
        console.error('Erro ao salvar porta:', error);
      }
    }
  }

  async getCurrentTab() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      this.currentTabId = tab?.id;
    } catch (error) {
      console.error('Erro ao obter aba atual:', error);
    }
  }

  async refreshStatus() {
    try {
      // Solicita status do background script
      const response = await chrome.runtime.sendMessage({ action: 'get_status' });
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Atualiza status do Gateway
      this.isGatewayConnected = response.relay_connected;
      this.updateGatewayStatus(response.relay_connected, response.gateway_status);
      
      // Atualiza status da aba atual
      this.isTabConnected = response.connected_tabs.includes(this.currentTabId);
      this.updateTabStatus(this.isTabConnected);
      
      // Atualiza botão
      this.updateToggleButton();
      
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      this.updateGatewayStatus(false);
      this.updateTabStatus(false);
      this.updateToggleButton();
    }
  }

  updateGatewayStatus(connected, gatewayInfo = null) {
    const statusEl = this.elements.gatewayStatus;
    const dotClass = connected ? 'dot-green' : 'dot-red';
    const statusClass = connected ? 'status-connected' : 'status-disconnected';
    const statusText = connected ? 'Conectado' : 'Desconectado';
    
    statusEl.className = `status-value ${statusClass}`;
    statusEl.innerHTML = `<span class="status-dot ${dotClass}"></span>${statusText}`;
    
    if (connected && gatewayInfo) {
      statusEl.title = `Gateway v${gatewayInfo.version || 'unknown'}`;
    }
  }

  updateTabStatus(connected) {
    const statusEl = this.elements.tabStatus;
    const dotClass = connected ? 'dot-green' : 'dot-red';
    const statusClass = connected ? 'status-connected' : 'status-disconnected';
    const statusText = connected ? 'Conectada' : 'Desconectada';
    
    statusEl.className = `status-value ${statusClass}`;
    statusEl.innerHTML = `<span class="status-dot ${dotClass}"></span>${statusText}`;
  }

  updateToggleButton() {
    const btn = this.elements.toggleBtn;
    
    if (!this.isGatewayConnected) {
      btn.textContent = 'Gateway Desconectado';
      btn.disabled = true;
      btn.className = 'btn btn-secondary';
      return;
    }
    
    if (!this.currentTabId) {
      btn.textContent = 'Nenhuma Aba Ativa';
      btn.disabled = true;
      btn.className = 'btn btn-secondary';
      return;
    }
    
    btn.disabled = false;
    
    if (this.isTabConnected) {
      btn.textContent = 'Desconectar Aba';
      btn.className = 'btn btn-secondary';
    } else {
      btn.textContent = 'Conectar Aba';
      btn.className = 'btn btn-primary';
    }
  }

  async toggleConnection() {
    if (!this.currentTabId) return;
    
    const btn = this.elements.toggleBtn;
    const originalText = btn.textContent;
    
    try {
      btn.disabled = true;
      btn.innerHTML = '<span class="loading"></span> Processando...';
      
      const action = this.isTabConnected ? 'disconnect_tab' : 'connect_tab';
      const response = await chrome.runtime.sendMessage({
        action,
        tabId: this.currentTabId
      });
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // Atualiza status após a operação
      await this.refreshStatus();
      
    } catch (error) {
      console.error('Erro ao alternar conexão:', error);
      
      // Mostra erro temporariamente
      btn.textContent = 'Erro: ' + error.message;
      btn.className = 'btn btn-secondary';
      
      setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
        this.updateToggleButton();
      }, 3000);
    }
  }
}

// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});