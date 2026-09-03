// CLEUDOCODE - Modern Web Interface
// JavaScript para controlar a interface HTML moderna

class CleudoApp {
    constructor() {
        this.currentView = 'chat';
        this.messages = [];
        this.playgroundBlocks = [
            { role: 'system', content: 'You are a helpful AI assistant.' },
            { role: 'user', content: '' }
        ];

        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupChat();
        this.setupMemory();
        this.setupPlayground();
        this.setupSquad();
        this.setupPulse(); // New
        this.setupMarket(); // New
        this.setupCleudoPay(); // New
        this.setupTerminalTabs();
        this.loadInitialView();
        this.pollSentientStatus();
        this.pollSquadStatus();
        this.pollSystemPulse(); // New
        this.fetchLocalSkills(); // New
    }

    async pollSentientStatus() {
        const updateStatus = async () => {
            try {
                const res = await fetch('/api/sentient/status');
                const data = await res.json();
                const statusEl = document.getElementById('sentient-status');
                if (statusEl) {
                    const color = data.oml_loyalty === 'verified' ? 'text-indigo-400' : 'text-amber-400';
                    const dotColor = data.oml_loyalty === 'verified' ? 'bg-indigo-500' : 'bg-amber-500';
                    statusEl.innerHTML = `
                        <span class="w-1.5 h-1.5 ${dotColor} rounded-full"></span>
                        OML ${data.oml_loyalty.toUpperCase()} // ${data.node_id}
                    `;
                    statusEl.className = `flex items-center gap-1.5 text-[8px] font-bold uppercase tracking-widest ${color} mt-1`;
                }
            } catch (e) { console.error('Sentient Status Error:', e); }
        };
        updateStatus();
        setInterval(updateStatus, 10000);
    }

    async pollSquadStatus() {
        const updateSquad = async () => {
            try {
                const res = await fetch('/api/mission-control/status');
                const data = await res.json();
                this.renderSquadStatus(data);
            } catch (e) { console.error('Squad Status Error:', e); }
        };
        updateSquad();
        setInterval(updateSquad, 5000);
    }

    async pollSystemPulse() {
        const updatePulse = async () => {
            if (this.currentView !== 'pulse') return;
            try {
                const res = await fetch('/api/system/pulse');
                const data = await res.json();
                this.renderPulse(data);
            } catch (e) { console.error('Pulse Error:', e); }
        };
        updatePulse();
        setInterval(updatePulse, 3000);
    }

    renderPulse(data) {
        const cpuBar = document.getElementById('metric-cpu-bar');
        const cpuText = document.getElementById('metric-cpu-text');
        const ramBar = document.getElementById('metric-ram-bar');
        const ramText = document.getElementById('metric-ram-text');
        const ollamaStatus = document.getElementById('metric-ollama-status');
        const ollamaDot = document.getElementById('metric-ollama-dot');
        const uptimeEl = document.getElementById('pulse-uptime');

        if (cpuBar) {
            cpuBar.style.width = `${data.telemetry.cpu}%`;
            cpuText.textContent = `${data.telemetry.cpu}%`;
            if (data.telemetry.cpu > 80) cpuBar.className = 'h-full bg-red-500 transition-all duration-1000';
            else cpuBar.className = 'h-full bg-emerald-500 transition-all duration-1000';
        }

        if (ramBar) {
            ramBar.style.width = `${data.telemetry.ram}%`;
            ramText.textContent = `${data.telemetry.ram}%`;
        }

        if (ollamaStatus) {
            const isOnline = data.telemetry.ollama === 'running';
            ollamaStatus.textContent = data.telemetry.ollama;
            ollamaStatus.className = `text-xs font-mono uppercase ${isOnline ? 'text-emerald-400' : 'text-red-400'}`;
            ollamaDot.className = `w-4 h-4 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`;
        }

        if (uptimeEl) {
            uptimeEl.textContent = 'STABLE';
        }
    }

    async fetchLocalSkills() {
        try {
            const res = await fetch('/api/skills/local');
            const data = await res.json();
            this.renderLocalSkills(data.skills);
        } catch (e) {
            console.error('Local Skills Error:', e);
            const statusEl = document.getElementById('local-skills-status');
            if (statusEl) statusEl.textContent = 'Erro ao carregar habilidades localmente.';
        }
    }

    renderLocalSkills(skills) {
        const grid = document.getElementById('local-skills-grid');
        const statusEl = document.getElementById('local-skills-status');
        if (!grid) return;

        if (statusEl) statusEl.textContent = `${skills.length} Habilidades Encontradas`;

        grid.innerHTML = skills.map(skill => `
            <div class="p-8 rounded-[2rem] bg-white/5 border border-white/5 hover:border-indigo-500/30 transition-all group">
                <div class="flex items-center justify-between mb-6">
                    <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                        <span class="material-symbols-outlined">${skill.type === 'Core' ? 'memory' : 'auto_fix'}</span>
                    </div>
                    <span class="text-[8px] font-black uppercase tracking-widest text-slate-500">${skill.type}</span>
                </div>
                <h4 class="text-xl lg:text-3xl font-black text-white uppercase tracking-tighter mb-2">${skill.name}</h4>
                <p class="text-[10px] text-slate-500 font-mono mb-6">${skill.id}</p>
                <button class="w-full py-3 bg-white/5 rounded-xl text-[10px] font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all border border-white/10 hover:bg-white/10">Ver Código</button>
            </div>
        `).join('');
    }

    setupMarket() {
        console.log("Skill Marketplace initialized.");
    }

    renderSquadStatus(data) {
        const grid = document.getElementById('agent-grid');
        const log = document.getElementById('mission-log');
        const activeCountEl = document.getElementById('stat-active-agents');
        const totalCountEl = document.getElementById('stat-total-agents');

        if (!grid || !log) return;

        // Render Grid
        const agents = data.agents || {};
        const agentNames = Object.keys(agents);
        totalCountEl.textContent = agentNames.length;

        let activeCount = 0;
        grid.innerHTML = agentNames.map(name => {
            const status = agents[name];
            const isActive = status.state === 'busy';
            if (isActive) activeCount++;

            const colorClass = isActive ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-white/5 bg-white/[0.02]';
            const dotClass = isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700';

            return `
                <div class="p-6 rounded-3xl border ${colorClass} transition-all duration-300">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-2">
                             <div class="w-2 h-2 rounded-full ${dotClass}"></div>
                             <span class="text-[10px] font-black uppercase tracking-widest text-white">${name}</span>
                        </div>
                        <span class="text-[8px] font-bold uppercase ${isActive ? 'text-emerald-400' : 'text-slate-600'}">${status.state}</span>
                    </div>
                    <div class="text-[10px] text-slate-500 font-mono line-clamp-2 min-h-[32px]">
                        ${status.last_task || 'Waiting for mission...'}
                    </div>
                </div>
            `;
        }).join('');
        activeCountEl.textContent = activeCount;

        // Render Log
        const history = data.mission_history || [];
        if (history.length > 0) {
            log.innerHTML = history.reverse().map(m => `
                <div class="p-6 flex items-center justify-between hover:bg-white/[0.02] transition-colors">
                    <div class="flex items-center gap-4">
                        <div class="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center text-[#FF5F5F]">
                            <span class="material-symbols-outlined text-sm">rocket_launch</span>
                        </div>
                        <div>
                            <div class="text-[10px] font-black text-white uppercase tracking-widest">${m.task}</div>
                            <div class="text-[8px] font-medium text-slate-600 uppercase mt-0.5">Assigned to: ${m.agent} // Status: ${m.status}</div>
                        </div>
                    </div>
                    <div class="text-[8px] font-mono text-slate-700">${new Date(m.timestamp * 1000).toLocaleTimeString()}</div>
                </div>
            `).join('');
        }
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Real links (e.g. /comunidade) navigate normally; only SPA view links are intercepted
                const isViewLink = link.hasAttribute('data-view') || link.getAttribute('href') === '#';
                if (!isViewLink) return;

                e.preventDefault();
                const viewId = link.dataset.view || link.id.replace('nav-', '');
                this.switchView(viewId);

                // Update active state
                navLinks.forEach(l => l.classList.remove('active', 'border-b-2', 'border-[#FF5F5F]', 'text-[#FF5F5F]'));
                navLinks.forEach(l => l.classList.add('text-slate-500'));

                link.classList.remove('text-slate-500');
                link.classList.add('active', 'text-[#FF5F5F]');
                if (!link.dataset.view) {
                    link.classList.add('border-b-2', 'border-[#FF5F5F]');
                }
            });
        });
    }

    switchView(viewId) {
        // Hide all views
        const views = ['view-chat', 'view-squad', 'view-memory', 'view-playground', 'view-market', 'view-cleudopay', 'view-pulse', 'view-contato'];
        views.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.add('hidden');
            }
        });

        // Show selected view
        const targetView = document.getElementById(`view-${viewId}`);
        if (targetView) {
            targetView.classList.remove('hidden');
            this.currentView = viewId;
        }
    }

    setupChat() {
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('btn-send');
        const chatContainer = document.getElementById('chat-container');

        const sendMessage = () => {
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            this.addMessage('user', message);
            chatInput.value = '';

            // Simulate AI response
            setTimeout(async () => {
                const response = await this.generateResponse(message);
                this.addMessage('assistant', response);
            }, 1000);
        };

        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 128) + 'px';
        });
    }

    addMessage(role, content) {
        const chatContainer = document.getElementById('chat-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex gap-3 sm:gap-5 items-start';

        const isUser = role === 'user';
        const icon = isUser ? 'person' : 'smart_toy';
        const bgColor = isUser ? 'bg-[#FF5F5F]' : 'bg-emerald-500';

        messageDiv.innerHTML = `
            <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl ${bgColor} text-white flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-base sm:text-lg">${icon}</span>
            </div>
            <div class="bg-white/[0.03] border border-white/[0.05] p-4 sm:p-5 rounded-2xl sm:rounded-3xl ${isUser ? 'rounded-br-none' : 'rounded-tl-none'} text-slate-300 shadow-sm min-w-0 max-w-[85%] sm:max-w-[80%]">
                <div class="text-sm text-slate-300 leading-relaxed font-mono break-words">
                    ${this.formatMessage(content)}
                </div>
            </div>
        `;

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        this.messages.push({ role, content });
    }

    formatMessage(content) {
        // Basic formatting for code blocks and commands
        return content
            .replace(/`([^`]+)`/g, '<code class="bg-black/30 px-1 py-0.5 rounded text-[#FF5F5F]">$1</code>')
            .replace(/\n/g, '<br>');
    }

    async generateResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            return data.success ? data.response : 'Erro ao processar mensagem.';
        } catch (error) {
            console.error('Erro na API:', error);
            return 'Erro de conexão com o servidor.';
        }
    }

    setupMemory() {
        const dropArea = document.getElementById('drop-area-main');
        const fileInput = document.getElementById('file-input-main');
        const scrapeBtn = document.getElementById('btn-scrape');
        const scrapeUrl = document.getElementById('scraping-url');

        // File upload
        dropArea.addEventListener('click', () => fileInput.click());
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('border-[#FF5F5F]/50', 'bg-[#FF5F5F]/5');
        });
        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('border-[#FF5F5F]/50', 'bg-[#FF5F5F]/5');
        });
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('border-[#FF5F5F]/50', 'bg-[#FF5F5F]/5');
            this.handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // URL scraping
        scrapeBtn.addEventListener('click', () => {
            const url = scrapeUrl.value.trim();
            if (url) {
                this.scrapeUrl(url);
            }
        });
    }

    async handleFiles(files) {
        const statusEl = document.getElementById('scrape-status');
        statusEl.textContent = `Processando ${files.length} arquivo(s)...`;
        statusEl.classList.remove('hidden');

        try {
            const formData = new FormData();
            Array.from(files).forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/api/memory/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                statusEl.textContent = `✅ ${data.message}`;
                this.updateStats();
            } else {
                statusEl.textContent = `❌ ${data.message}`;
            }
        } catch (error) {
            statusEl.textContent = '❌ Erro ao processar arquivos';
            console.error('Erro:', error);
        }
    }

    async scrapeUrl(url) {
        const statusEl = document.getElementById('scrape-status');
        statusEl.textContent = 'Extraindo conteúdo da URL...';
        statusEl.classList.remove('hidden');

        try {
            const response = await fetch('/api/memory/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (data.success) {
                statusEl.textContent = `✅ ${data.message}`;
                this.updateStats();
            } else {
                statusEl.textContent = `❌ ${data.message}`;
            }
        } catch (error) {
            statusEl.textContent = '❌ Erro ao processar URL';
            console.error('Erro:', error);
        }
    }

    updateStats() {
        const docsEl = document.getElementById('stat-docs');
        const tokensEl = document.getElementById('stat-tokens');

        if (docsEl) {
            const currentDocs = parseInt(docsEl.textContent) || 0;
            docsEl.textContent = currentDocs + 1;
        }

        if (tokensEl) {
            const currentTokens = parseInt(tokensEl.textContent.replace('K', '')) || 0;
            tokensEl.textContent = (currentTokens + Math.floor(Math.random() * 50) + 10) + 'K';
        }
    }

    setupPlayground() {
        const runBtn = document.getElementById('btn-playground-run');
        const addBtn = document.getElementById('btn-add-block');
        const blocksContainer = document.getElementById('playground-blocks');
        const outputContainer = document.getElementById('playground-output');

        if (runBtn) {
            runBtn.addEventListener('click', () => this.runPlayground());
        }

        if (addBtn) {
            addBtn.addEventListener('click', () => this.addPlaygroundBlock());
        }

        this.renderPlaygroundBlocks();
    }

    renderPlaygroundBlocks() {
        const container = document.getElementById('playground-blocks');
        if (!container) return;

        container.innerHTML = '';

        this.playgroundBlocks.forEach((block, index) => {
            const blockDiv = document.createElement('div');
            blockDiv.className = 'bg-surface border border-white/10 rounded-2xl p-6';

            blockDiv.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <select class="bg-black border border-white/10 rounded-lg px-3 py-2 text-white text-sm" onchange="app.updateBlockRole(${index}, this.value)">
                        <option value="system" ${block.role === 'system' ? 'selected' : ''}>System</option>
                        <option value="user" ${block.role === 'user' ? 'selected' : ''}>User</option>
                        <option value="assistant" ${block.role === 'assistant' ? 'selected' : ''}>Assistant</option>
                    </select>
                    <button onclick="app.removePlaygroundBlock(${index})" class="text-slate-500 hover:text-red-400 transition-colors">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>
                <textarea 
                    class="w-full h-32 bg-black border border-white/10 rounded-lg p-4 text-white text-sm font-mono resize-none focus:ring-2 focus:ring-[#FF5F5F]/50 outline-none"
                    placeholder="Digite o conteúdo da mensagem..."
                    onchange="app.updateBlockContent(${index}, this.value)"
                >${block.content}</textarea>
            `;

            container.appendChild(blockDiv);
        });
    }

    updateBlockRole(index, role) {
        this.playgroundBlocks[index].role = role;
    }

    updateBlockContent(index, content) {
        this.playgroundBlocks[index].content = content;
    }

    addPlaygroundBlock() {
        this.playgroundBlocks.push({ role: 'user', content: '' });
        this.renderPlaygroundBlocks();
    }

    removePlaygroundBlock(index) {
        this.playgroundBlocks.splice(index, 1);
        this.renderPlaygroundBlocks();
    }

    async runPlayground() {
        const outputContainer = document.getElementById('playground-output');
        if (!outputContainer) return;

        outputContainer.innerHTML = `
            <span class="text-slate-700 font-bold uppercase tracking-widest text-[10px]">OUTPUT CONSOLE //</span>
            <div class="mt-4 text-[#FF5F5F]">Executando prompt...</div>
        `;

        try {
            const response = await fetch('/api/playground/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ blocks: this.playgroundBlocks })
            });

            const data = await response.json();

            if (data.success) {
                outputContainer.innerHTML = `
                    <span class="text-slate-700 font-bold uppercase tracking-widest text-[10px]">OUTPUT CONSOLE //</span>
                    <div class="mt-4 text-white leading-relaxed">${data.response}</div>
                `;
            } else {
                outputContainer.innerHTML = `
                    <span class="text-slate-700 font-bold uppercase tracking-widest text-[10px]">OUTPUT CONSOLE //</span>
                    <div class="mt-4 text-red-400">Erro: ${data.message}</div>
                `;
            }
        } catch (error) {
            outputContainer.innerHTML = `
                <span class="text-slate-700 font-bold uppercase tracking-widest text-[10px]">OUTPUT CONSOLE //</span>
                <div class="mt-4 text-red-400">Erro de conexão com o servidor</div>
            `;
            console.error('Erro:', error);
        }
    }

    generatePlaygroundResponse() {
        return `Olá! Analisei seu prompt e estou pronto para ajudar.

Com base nas mensagens fornecidas, posso:
• Executar comandos e scripts
• Analisar e criar código
• Gerenciar projetos e automações
• Acessar documentação indexada

Como posso ser mais útil para você hoje?`;
    }

    setupSquad() {
        console.log("Mission Control Dashboard Initialized");
    }

    setupPulse() {
        console.log("Kernel Pulse Monitoring Initialized");
    }

    setupCleudoPay() {
        // Billing toggle (mensal / anual)
        const toggle = document.getElementById('billing-toggle');
        const knob = document.getElementById('billing-knob');
        const priceIA = document.getElementById('price-ia');
        const billingNote = document.getElementById('billing-note');
        const labelMonthly = document.getElementById('billing-label-monthly');
        const labelYearly = document.getElementById('billing-label-yearly');

        if (toggle && knob && priceIA && billingNote) {
            const update = (yearly) => {
                toggle.setAttribute('aria-checked', String(yearly));
                knob.style.transform = yearly ? 'translateX(24px)' : 'translateX(0)';
                if (yearly) {
                    priceIA.textContent = 'R$ 23';
                    billingNote.textContent = 'Cobrado anualmente (R$ 276/ano)';
                    labelMonthly?.classList.remove('text-white');
                    labelMonthly?.classList.add('text-slate-500');
                    labelYearly?.classList.remove('text-slate-500');
                    labelYearly?.classList.add('text-white');
                } else {
                    priceIA.textContent = 'R$ 29';
                    billingNote.textContent = 'Cobrado mensalmente';
                    labelMonthly?.classList.remove('text-slate-500');
                    labelMonthly?.classList.add('text-white');
                    labelYearly?.classList.remove('text-white');
                    labelYearly?.classList.add('text-slate-500');
                }
            };
            toggle.addEventListener('click', () => {
                update(toggle.getAttribute('aria-checked') !== 'true');
            });
        }

        // Smooth scroll + scrollspy das seções da Landing Page Financeira
        const view = document.getElementById('view-cleudopay');
        if (!view) return;

        const sectionIds = ['cleudopay-features', 'cleudopay-pricing', 'cleudopay-faq', 'cleudopay-social'];
        const sections = sectionIds.map(id => document.getElementById(id)).filter(Boolean);
        const links = Array.from(view.querySelectorAll('.cleudopay-nav-link'));

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.getElementById(link.dataset.target);
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });

        const updateScrollspy = () => {
            const offset = 200;
            let current = null;
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top <= offset) current = section.id;
            });
            links.forEach(link => {
                const active = link.dataset.target === current;
                link.classList.toggle('text-[#FF5F5F]', active);
                link.classList.toggle('text-slate-500', !active);
            });
        };

        const scrollTargets = [window, document.querySelector('main')].filter(Boolean);
        scrollTargets.forEach(target => {
            target.addEventListener('scroll', updateScrollspy, { passive: true });
        });
        window.addEventListener('resize', updateScrollspy);
        updateScrollspy();
    }

    setupTerminalTabs() {
        const promptTab = document.getElementById('term-prompt');
        const logsTab = document.getElementById('term-logs');
        const memoryTab = document.getElementById('term-memory');
        const chatContainer = document.getElementById('chat-container');
        const logsContainer = document.getElementById('logs-container');

        const tabs = [promptTab, logsTab, memoryTab];
        const containers = [chatContainer, logsContainer];

        tabs.forEach(tab => {
            if (tab) {
                tab.addEventListener('click', () => {
                    // Reset all tabs
                    tabs.forEach(t => {
                        if (t) {
                            t.classList.remove('text-[#FF5F5F]', 'border-b-2', 'border-[#FF5F5F]');
                            t.classList.add('text-slate-500');
                        }
                    });

                    // Activate clicked tab
                    tab.classList.remove('text-slate-500');
                    tab.classList.add('text-[#FF5F5F]', 'border-b-2', 'border-[#FF5F5F]');

                    // Show/hide containers
                    if (tab.id === 'term-logs') {
                        chatContainer?.classList.add('hidden');
                        logsContainer?.classList.remove('hidden');
                    } else {
                        chatContainer?.classList.remove('hidden');
                        logsContainer?.classList.add('hidden');
                    }
                });
            }
        });
    }

    loadInitialView() {
        // Start with chat view
        this.switchView('chat');

        // Add welcome message
        setTimeout(() => {
            this.addMessage('assistant', 'Seja bem-vindo ao Cleudocode! Sou seu assistente de IA para desenvolvimento e automação. Como posso ajudar você hoje?');
        }, 500);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CleudoApp();
});

// Global functions for playground (needed for inline event handlers)
function updateBlockRole(index, role) {
    if (window.app) {
        window.app.updateBlockRole(index, role);
    }
}

function updateBlockContent(index, content) {
    if (window.app) {
        window.app.updateBlockContent(index, content);
    }
}

function removePlaygroundBlock(index) {
    if (window.app) {
        window.app.removePlaygroundBlock(index);
    }
}