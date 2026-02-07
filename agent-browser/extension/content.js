// Cleudocode Browser Relay - Content Script
// Executa no contexto da página para facilitar automação

(function() {
  'use strict';
  
  // Evita múltiplas injeções
  if (window.cleudocodeRelay) {
    return;
  }
  
  class CleudocodeContentRelay {
    constructor() {
      this.isConnected = false;
      this.tabId = null;
      
      this.init();
    }
    
    init() {
      // Marca como inicializado
      window.cleudocodeRelay = this;
      
      // Listener para mensagens do background script
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        this.handleMessage(message, sender, sendResponse);
        return true;
      });
      
      // Injeta utilitários de automação no contexto da página
      this.injectAutomationUtils();
      
      console.log('Cleudocode Content Relay inicializado');
    }
    
    handleMessage(message, sender, sendResponse) {
      try {
        switch (message.action) {
          case 'execute_script':
            this.executeScript(message.script, sendResponse);
            break;
            
          case 'get_page_info':
            this.getPageInfo(sendResponse);
            break;
            
          case 'find_elements':
            this.findElements(message.selector, sendResponse);
            break;
            
          case 'interact_element':
            this.interactElement(message.selector, message.action, message.value, sendResponse);
            break;
            
          default:
            sendResponse({ error: 'Ação desconhecida no content script' });
        }
      } catch (error) {
        console.error('Erro no content script:', error);
        sendResponse({ error: error.message });
      }
    }
    
    executeScript(script, callback) {
      try {
        const result = eval(script);
        callback({ success: true, result });
      } catch (error) {
        callback({ success: false, error: error.message });
      }
    }
    
    getPageInfo(callback) {
      const info = {
        url: window.location.href,
        title: document.title,
        readyState: document.readyState,
        timestamp: Date.now(),
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        scroll: {
          x: window.scrollX,
          y: window.scrollY
        }
      };
      
      callback({ success: true, info });
    }
    
    findElements(selector, callback) {
      try {
        const elements = Array.from(document.querySelectorAll(selector));
        const elementInfo = elements.map((el, index) => ({
          index,
          tagName: el.tagName.toLowerCase(),
          id: el.id,
          className: el.className,
          textContent: el.textContent?.substring(0, 100),
          visible: this.isElementVisible(el),
          rect: el.getBoundingClientRect()
        }));
        
        callback({ success: true, elements: elementInfo, count: elements.length });
      } catch (error) {
        callback({ success: false, error: error.message });
      }
    }
    
    interactElement(selector, action, value, callback) {
      try {
        const element = document.querySelector(selector);
        if (!element) {
          throw new Error('Elemento não encontrado');
        }
        
        switch (action) {
          case 'click':
            element.click();
            break;
            
          case 'type':
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
              element.value = value;
              element.dispatchEvent(new Event('input', { bubbles: true }));
              element.dispatchEvent(new Event('change', { bubbles: true }));
            } else {
              element.textContent = value;
            }
            break;
            
          case 'focus':
            element.focus();
            break;
            
          case 'scroll':
            element.scrollIntoView({ behavior: 'smooth' });
            break;
            
          default:
            throw new Error('Ação não suportada: ' + action);
        }
        
        callback({ success: true, action, selector });
      } catch (error) {
        callback({ success: false, error: error.message });
      }
    }
    
    isElementVisible(element) {
      const rect = element.getBoundingClientRect();
      const style = window.getComputedStyle(element);
      
      return (
        rect.width > 0 &&
        rect.height > 0 &&
        style.visibility !== 'hidden' &&
        style.display !== 'none' &&
        style.opacity !== '0'
      );
    }
    
    injectAutomationUtils() {
      // Injeta utilitários globais para automação
      window.cleudocodeUtils = {
        // Função para aguardar elemento aparecer
        waitForElement: (selector, timeout = 5000) => {
          return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element) {
              resolve(element);
              return;
            }
            
            const observer = new MutationObserver(() => {
              const element = document.querySelector(selector);
              if (element) {
                observer.disconnect();
                resolve(element);
              }
            });
            
            observer.observe(document.body, {
              childList: true,
              subtree: true
            });
            
            setTimeout(() => {
              observer.disconnect();
              reject(new Error(`Elemento ${selector} não encontrado em ${timeout}ms`));
            }, timeout);
          });
        },
        
        // Função para aguardar carregamento da página
        waitForLoad: () => {
          return new Promise((resolve) => {
            if (document.readyState === 'complete') {
              resolve();
            } else {
              window.addEventListener('load', resolve, { once: true });
            }
          });
        },
        
        // Função para simular digitação humana
        humanType: async (element, text, delay = 100) => {
          element.focus();
          element.value = '';
          
          for (const char of text) {
            element.value += char;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(resolve => setTimeout(resolve, delay + Math.random() * 50));
          }
          
          element.dispatchEvent(new Event('change', { bubbles: true }));
        }
      };
    }
  }
  
  // Inicializa o content relay
  new CleudocodeContentRelay();
})();