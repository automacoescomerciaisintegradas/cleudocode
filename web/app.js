
// State
let currentChatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    // DOM Elements
    const viewDashboard = document.getElementById('view-dashboard');
    const viewChat = document.getElementById('view-chat');
    const viewPlayground = document.getElementById('view-playground');
    const viewLock = document.getElementById('view-lock');

    const btnNavChat = document.getElementById('nav-chat');
    const btnNavMemory = document.getElementById('nav-memory');
    const btnNavPlayground = document.getElementById('nav-playground');
    const btnNewChat = document.getElementById('btn-new-chat');

    // Header Auth Elements
    const btnLoginHeader = document.getElementById('btn-login-header');
    const userProfileGroup = document.getElementById('user-profile-group');

    const chatContainer = document.getElementById('chat-container');
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');

    // All nav buttons for easier management
    const allNavButtons = [btnNavChat, btnNavMemory, btnNavPlayground];
    const allViews = [viewDashboard, viewChat, viewPlayground];

    // View Switching
    function switchView(viewName) {
        // Hide all views
        allViews.forEach(v => {
            if (v) {
                v.classList.add('hidden');
                v.classList.remove('flex');
            }
        });

        // Reset all nav buttons
        allNavButtons.forEach(btn => {
            if (btn) {
                btn.classList.remove('text-primary', 'border-b-2', 'border-primary', 'font-semibold');
                btn.classList.add('text-slate-500', 'dark:text-slate-400');
            }
        });

        // Show selected view and highlight nav
        if (viewName === 'chat') {
            viewChat.classList.remove('hidden');
            viewChat.classList.add('flex');
            btnNavChat.classList.add('text-primary', 'border-b-2', 'border-primary', 'font-semibold');
            btnNavChat.classList.remove('text-slate-500', 'dark:text-slate-400');
        } else if (viewName === 'playground') {
            viewPlayground.classList.remove('hidden');
            btnNavPlayground.classList.add('text-primary', 'border-b-2', 'border-primary', 'font-semibold');
            btnNavPlayground.classList.remove('text-slate-500', 'dark:text-slate-400');
        } else {
            // dashboard (memory)
            viewDashboard.classList.remove('hidden');
            btnNavMemory.classList.add('text-primary', 'border-b-2', 'border-primary', 'font-semibold');
            btnNavMemory.classList.remove('text-slate-500', 'dark:text-slate-400');
        }
    }

    // Event Listeners for Nav
    btnNavChat.addEventListener('click', (e) => { e.preventDefault(); switchView('chat'); });
    btnNavMemory.addEventListener('click', (e) => { e.preventDefault(); switchView('dashboard'); });
    if (btnNavPlayground) {
        btnNavPlayground.addEventListener('click', (e) => { e.preventDefault(); switchView('playground'); });
    }
    btnNewChat.addEventListener('click', (e) => {
        e.preventDefault();
        switchView('chat');
        resetChat();
    });

    // Chat Logic
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // UI Optimistic Update
        addMessageToUI('user', text);
        chatInput.value = '';

        // Show Loading
        const loadingId = addLoadingIndicator();

        try {
            const systemPrompt = document.getElementById('system-prompt').value;
            const useRag = true; // Defaulting to on for now, or add toggle

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    use_rag: useRag,
                    system_prompt: systemPrompt
                })
            });

            const data = await response.json();

            // Remove Loading
            removeMessage(loadingId);

            if (data.reply) {
                addMessageToUI('assistant', data.reply);
                if (data.context) {
                    console.log("RAG Context:", data.context);
                }
            } else {
                addMessageToUI('assistant', 'Erro: ' + (data.error || 'Desconhecido'));
            }

        } catch (error) {
            removeMessage(loadingId);
            addMessageToUI('assistant', 'Erro de conexão: ' + error.message);
        }
    }

    // Enter Key to Send
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    btnSend.addEventListener('click', sendMessage);

    // --- ATTACH FILE IN CHAT ---
    const btnAttachChat = document.getElementById('btn-attach-chat');
    const chatFileInput = document.getElementById('chat-file-input');

    if (btnAttachChat && chatFileInput) {
        btnAttachChat.addEventListener('click', () => chatFileInput.click());

        chatFileInput.addEventListener('change', async (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const formData = new FormData();
                formData.append('file', file);

                // Show uploading state
                addMessageToUI('user', `📎 Enviando arquivo: ${file.name}...`);

                try {
                    const res = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();

                    if (data.filename) {
                        addMessageToUI('assistant', `✅ Arquivo "${data.filename}" indexado com sucesso! Agora você pode fazer perguntas sobre ele.`);
                    } else {
                        addMessageToUI('assistant', `❌ Erro ao processar arquivo: ${data.error}`);
                    }
                } catch (err) {
                    addMessageToUI('assistant', `❌ Erro de conexão: ${err.message}`);
                }

                chatFileInput.value = '';
            }
        });
    }

    // --- VOICE INPUT (SPEECH-TO-TEXT) ---
    const btnMic = document.getElementById('btn-mic');
    let isListening = false;
    let recognition = null;

    // Check if browser supports Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR';
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = () => {
            isListening = true;
            btnMic.classList.add('bg-rose-500', 'text-white');
            btnMic.classList.remove('text-slate-400');
            btnMic.innerHTML = '<span class="material-symbols-outlined animate-pulse">mic</span>';
            chatInput.placeholder = '🎤 Ouvindo... Fale agora!';
        };

        recognition.onend = () => {
            isListening = false;
            btnMic.classList.remove('bg-rose-500', 'text-white');
            btnMic.classList.add('text-slate-400');
            btnMic.innerHTML = '<span class="material-symbols-outlined">mic</span>';
            chatInput.placeholder = 'Digite sua mensagem... (Enter para enviar)';
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            chatInput.value = transcript;

            // Auto-resize textarea
            chatInput.style.height = 'auto';
            chatInput.style.height = chatInput.scrollHeight + 'px';
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'not-allowed') {
                alert('Permissão de microfone negada. Por favor, permita o acesso ao microfone nas configurações do navegador.');
            }
        };

        btnMic.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        // Browser doesn't support speech recognition
        btnMic.addEventListener('click', () => {
            alert('Seu navegador não suporta reconhecimento de voz. Tente usar Chrome ou Edge.');
        });
        btnMic.title = 'Navegador não suportado';
    }


    // Helper: Add Message
    function addMessageToUI(role, content) {
        const div = document.createElement('div');
        const isUser = role === 'user';

        div.className = `flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`;

        const avatar = document.createElement('div');
        avatar.className = `w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-indigo-500 text-white' : 'bg-emerald-500 text-white'}`;
        avatar.innerHTML = `<span class="material-symbols-outlined text-sm">${isUser ? 'person' : 'smart_toy'}</span>`;

        const bubble = document.createElement('div');
        bubble.className = `max-w-[80%] rounded-2xl p-4 ${isUser ? 'bg-indigo-500 text-white rounded-br-none' : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-bl-none shadow-sm'}`;

        // Markdown parsing could go here, for now plain text
        bubble.innerHTML = `<div class="prose ${isUser ? 'prose-invert' : 'dark:prose-invert'} text-sm max-w-none">${content.replace(/\n/g, '<br>')}</div>`;

        div.appendChild(avatar);
        div.appendChild(bubble);

        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return div;
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = `flex gap-4`;
        div.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-sm animate-spin">sync</span>
            </div>
            <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-4 rounded-bl-none shadow-sm">
                <div class="flex gap-1">
                    <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-75"></div>
                    <div class="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150"></div>
                </div>
            </div>
        `;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function resetChat() {
        chatContainer.innerHTML = '';
        // Could call API to reset history too
        fetch('/api/reset', { method: 'POST' });
        addMessageToUI('assistant', 'Olá! Como posso ajudar você hoje com seus projetos?');
    }

    // --- FEATURES RESTORATION ---

    // 1. Load Agents
    const agentSelect = document.getElementById('agent-select');
    const systemPromptArea = document.getElementById('system-prompt');

    async function loadAgents() {
        if (!agentSelect) return;
        try {
            const res = await fetch('/api/agents');
            const data = await res.json();

            // Clear except first option
            agentSelect.innerHTML = '<option value="custom">Personalizado</option>';

            data.agents.forEach(agent => {
                const opt = document.createElement('option');
                opt.value = agent;
                opt.textContent = agent; // e.g., "qa.md"
                agentSelect.appendChild(opt);
            });
        } catch (e) {
            console.error("Erro ao carregar agentes:", e);
        }
    }

    // Agent Selection Event
    if (agentSelect) {
        agentSelect.addEventListener('change', async (e) => {
            const val = e.target.value;
            if (val === 'custom') return;

            try {
                const res = await fetch(`/api/agent/${val}`);
                const data = await res.json();
                if (data.content) {
                    systemPromptArea.value = data.content;
                    // Optional: Notify user
                    const originalText = systemPromptArea.getAttribute('placeholder');
                    systemPromptArea.setAttribute('placeholder', `Agente ${val} carregado...`);
                    setTimeout(() => systemPromptArea.setAttribute('placeholder', originalText), 2000);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // 2. Button Logic (Save & Clear)
    const btnSaveHistory = document.getElementById('btn-save-history');
    if (btnSaveHistory) {
        btnSaveHistory.addEventListener('click', async () => {
            const res = await fetch('/api/history', { method: 'POST' });
            const data = await res.json();
            alert(data.message || data.error);
        });
    }

    const btnClearChat = document.getElementById('btn-clear-chat');
    if (btnClearChat) {
        btnClearChat.addEventListener('click', () => {
            if (confirm("Tem certeza que deseja limpar toda a conversa?")) {
                resetChat();
            }
        });
    }

    // 3. Update Memory Stats (Real) on Dashboard Load
    async function updateStats() {
        try {
            const res = await fetch('/api/memory/stats');
            const data = await res.json();

            // Update UI elements if they exist (We need IDs in HTML)
            const elDocs = document.getElementById('stat-docs');
            const elTokens = document.getElementById('stat-tokens');

            if (elDocs) elDocs.textContent = data.documents;
            if (elTokens) elTokens.textContent = data.tokens_approx;
        } catch (e) { console.warn(e); }
    }

    // Nav Click triggers stats update
    btnNavMemory.addEventListener('click', updateStats);

    // 4. NotebookLM Export
    const btnExportNotebook = document.getElementById('btn-export-notebooklm');
    if (btnExportNotebook) {
        btnExportNotebook.addEventListener('click', async () => {
            const originalText = btnExportNotebook.innerHTML;
            btnExportNotebook.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Gerando...';
            btnExportNotebook.disabled = true;

            try {
                const res = await fetch('/api/integrations/notebooklm', { method: 'POST' });
                const data = await res.json();
                alert(data.message || data.error);
            } catch (err) {
                alert('Erro ao exportar: ' + err.message);
            }

            btnExportNotebook.innerHTML = originalText;
            btnExportNotebook.disabled = false;
        });
    }

    // 5. Scraping Logic
    const btnScrape = document.getElementById('btn-scrape');
    const scrapingUrlInput = document.getElementById('scraping-url');
    const scrapeStatus = document.getElementById('scrape-status');

    if (btnScrape && scrapingUrlInput) {
        btnScrape.addEventListener('click', async () => {
            const url = scrapingUrlInput.value.trim();
            if (!url) {
                alert('Insira uma URL válida');
                return;
            }

            // Show status
            if (scrapeStatus) {
                scrapeStatus.classList.remove('hidden', 'text-emerald-500', 'text-rose-500');
                scrapeStatus.textContent = 'Processando URL...';
            }

            const originalText = btnScrape.innerHTML;
            btnScrape.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Processando...';
            btnScrape.disabled = true;

            try {
                const res = await fetch('/api/scrape', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await res.json();

                if (scrapeStatus) {
                    if (data.message) {
                        scrapeStatus.textContent = "✓ Sucesso: " + data.message;
                        scrapeStatus.classList.add('text-emerald-500');
                        scrapingUrlInput.value = ''; // Clear input on success
                    } else {
                        scrapeStatus.textContent = "✗ Erro: " + (data.error || 'Desconhecido');
                        scrapeStatus.classList.add('text-rose-500');
                    }
                }
            } catch (err) {
                if (scrapeStatus) {
                    scrapeStatus.textContent = "✗ Erro de conexão: " + err.message;
                    scrapeStatus.classList.add('text-rose-500');
                }
            }

            // Restore button
            btnScrape.innerHTML = originalText;
            btnScrape.disabled = false;

            // Refresh stats
            updateStats();
        });
    }

    // 6. Main Area Upload Logic (Drag & Drop + Button)
    const dropAreaMain = document.getElementById('drop-area-main');
    const fileInputMain = document.getElementById('file-input-main');
    const btnProcessFiles = document.getElementById('btn-process-files');

    // Reusable Upload Function
    async function handleFileUpload(files) {
        if (files.length === 0) return;

        const originalText = dropAreaMain.innerHTML;
        dropAreaMain.innerHTML = '<div class="flex flex-col items-center"><span class="material-symbols-outlined text-4xl animate-spin text-primary">sync</span><p class="mt-2 text-slate-500">Processando ' + files.length + ' arquivo(s)...</p></div>';

        let successCount = 0;
        let failCount = 0;

        for (let i = 0; i < files.length; i++) {
            const formData = new FormData();
            formData.append('file', files[i]);

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.filename) successCount++;
                else failCount++;
            } catch (e) { failCount++; }
        }

        // Feedback
        dropAreaMain.innerHTML = `<div class="flex flex-col items-center"><span class="material-symbols-outlined text-4xl text-emerald-500">check_circle</span><p class="mt-2 text-slate-600 font-bold">Concluído!</p><p class="text-xs text-slate-400">${successCount} sucesso(s), ${failCount} falha(s).</p></div>`;

        // Refresh Stats
        updateStats();

        // Reset UI after 3s
        setTimeout(() => {
            dropAreaMain.innerHTML = originalText;
        }, 3000);

        fileInputMain.value = ''; // Reset input
    }

    if (dropAreaMain && fileInputMain) {
        // Click behavior
        dropAreaMain.addEventListener('click', () => fileInputMain.click());

        // Button behavior
        if (btnProcessFiles) {
            btnProcessFiles.addEventListener('click', () => fileInputMain.click());
        }

        // File Input Change
        fileInputMain.addEventListener('change', (e) => {
            handleFileUpload(e.target.files);
        });

        // Drag & Drop Events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropAreaMain.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropAreaMain.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropAreaMain.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropAreaMain.classList.add('border-primary', 'bg-slate-50', 'dark:bg-slate-700');
            dropAreaMain.classList.remove('border-slate-300', 'dark:border-slate-600');
        }

        function unhighlight(e) {
            dropAreaMain.classList.remove('border-primary', 'bg-slate-50', 'dark:bg-slate-700');
            dropAreaMain.classList.add('border-slate-300', 'dark:border-slate-600');
        }

        dropAreaMain.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFileUpload(files);
        });
    }

    // Initial Load
    loadAgents();
    updateStats();

    // Upload Logic (Existing...)
    const uploadBtn = document.getElementById('btn-upload-trigger');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.multiple = true;
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            const formData = new FormData();
            formData.append('file', e.target.files[0]);

            const originalText = uploadBtn.innerHTML;
            uploadBtn.innerHTML = '<span class="material-symbols-outlined text-3xl animate-spin">sync</span><p class="text-xs">Enviando...</p>';

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.filename) {
                    alert('Arquivo ' + data.filename + ' indexado com sucesso!');
                } else {
                    alert('Erro: ' + data.error);
                }
            } catch (err) {
                alert('Erro no upload: ' + err.message);
            }

            uploadBtn.innerHTML = originalText;
            fileInput.value = ''; // Reset
        }
    });

    // ===== PLAYGROUND LOGIC =====
    const playgroundBlocks = document.getElementById('playground-blocks');
    const btnAddBlock = document.getElementById('btn-add-block');
    const btnPlaygroundRun = document.getElementById('btn-playground-run');
    const btnPlaygroundReset = document.getElementById('btn-playground-reset');
    const playgroundOutput = document.getElementById('playground-output');
    const paramTemperature = document.getElementById('param-temperature');
    const paramMaxTokens = document.getElementById('param-max-tokens');
    const paramTopP = document.getElementById('param-top-p');
    const tempValue = document.getElementById('temp-value');
    const toppValue = document.getElementById('topp-value');

    // Update slider display values
    if (paramTemperature && tempValue) {
        paramTemperature.addEventListener('input', () => {
            tempValue.textContent = parseFloat(paramTemperature.value).toFixed(2);
        });
    }
    if (paramTopP && toppValue) {
        paramTopP.addEventListener('input', () => {
            toppValue.textContent = parseFloat(paramTopP.value).toFixed(2);
        });
    }

    // Add Block
    if (btnAddBlock && playgroundBlocks) {
        btnAddBlock.addEventListener('click', () => {
            const newBlock = document.createElement('div');
            newBlock.className = 'playground-block bg-slate-800 rounded-xl border border-slate-700 p-4';
            newBlock.dataset.role = 'user';
            newBlock.innerHTML = `
                <div class="flex items-center gap-3 mb-3">
                    <select class="block-role bg-slate-700 text-white text-sm rounded-lg px-3 py-1.5 border-none focus:ring-primary">
                        <option value="system">system</option>
                        <option value="user" selected>user</option>
                        <option value="assistant">assistant</option>
                    </select>
                    <button class="btn-delete-block p-1.5 text-slate-500 hover:text-rose-500 hover:bg-slate-700 rounded-lg transition-colors">
                        <span class="material-symbols-outlined text-lg">delete</span>
                    </button>
                </div>
                <textarea class="block-content w-full bg-slate-900 text-slate-100 rounded-lg p-4 border border-slate-600 focus:ring-2 focus:ring-primary/50 resize-y min-h-[100px] text-sm font-mono" placeholder="Digite a mensagem..."></textarea>
            `;
            playgroundBlocks.appendChild(newBlock);
            attachDeleteListener(newBlock.querySelector('.btn-delete-block'));
        });
    }

    // Delete Block Function
    function attachDeleteListener(btn) {
        if (btn) {
            btn.addEventListener('click', () => {
                btn.closest('.playground-block').remove();
            });
        }
    }

    // Attach delete listeners to initial blocks
    document.querySelectorAll('.btn-delete-block').forEach(attachDeleteListener);

    // Execute Playground
    if (btnPlaygroundRun && playgroundBlocks && playgroundOutput) {
        btnPlaygroundRun.addEventListener('click', async () => {
            // Collect messages
            const blocks = playgroundBlocks.querySelectorAll('.playground-block');
            const messages = [];

            blocks.forEach(block => {
                const role = block.querySelector('.block-role').value;
                const content = block.querySelector('.block-content').value.trim();
                if (content) {
                    messages.push({ role, content });
                }
            });

            if (messages.length === 0) {
                alert('Adicione pelo menos uma mensagem com conteúdo.');
                return;
            }

            // Get parameters
            const temperature = paramTemperature ? parseFloat(paramTemperature.value) : 0.7;
            const maxTokens = paramMaxTokens ? parseInt(paramMaxTokens.value) : 2048;
            const topP = paramTopP ? parseFloat(paramTopP.value) : 0.9;

            // Update UI
            const originalBtnText = btnPlaygroundRun.innerHTML;
            btnPlaygroundRun.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Executando...';
            btnPlaygroundRun.disabled = true;
            playgroundOutput.innerHTML = '<span class="text-amber-400">⏳ Gerando resposta...</span>';

            try {
                const res = await fetch('/api/playground', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        messages,
                        options: { temperature, num_predict: maxTokens, top_p: topP }
                    })
                });
                const data = await res.json();

                if (data.reply) {
                    playgroundOutput.innerHTML = data.reply.replace(/\n/g, '<br>');
                } else {
                    playgroundOutput.innerHTML = '<span class="text-rose-400">❌ Erro: ' + (data.error || 'Desconhecido') + '</span>';
                }
            } catch (err) {
                playgroundOutput.innerHTML = '<span class="text-rose-400">❌ Erro de conexão: ' + err.message + '</span>';
            }

            btnPlaygroundRun.innerHTML = originalBtnText;
            btnPlaygroundRun.disabled = false;
        });
    }

    // Reset Playground
    if (btnPlaygroundReset && playgroundBlocks && playgroundOutput) {
        btnPlaygroundReset.addEventListener('click', () => {
            // Reset to default blocks
            playgroundBlocks.innerHTML = `
                <div class="playground-block bg-slate-800 rounded-xl border border-slate-700 p-4" data-role="system">
                    <div class="flex items-center gap-3 mb-3">
                        <select class="block-role bg-slate-700 text-white text-sm rounded-lg px-3 py-1.5 border-none focus:ring-primary">
                            <option value="system" selected>system</option>
                            <option value="user">user</option>
                            <option value="assistant">assistant</option>
                        </select>
                        <button class="btn-delete-block p-1.5 text-slate-500 hover:text-rose-500 hover:bg-slate-700 rounded-lg transition-colors">
                            <span class="material-symbols-outlined text-lg">delete</span>
                        </button>
                    </div>
                    <textarea class="block-content w-full bg-slate-900 text-slate-100 rounded-lg p-4 border border-slate-600 focus:ring-2 focus:ring-primary/50 resize-y min-h-[100px] text-sm font-mono" placeholder="Conteúdo da mensagem...">You are a helpful AI assistant.</textarea>
                </div>
                <div class="playground-block bg-slate-800 rounded-xl border border-slate-700 p-4" data-role="user">
                    <div class="flex items-center gap-3 mb-3">
                        <select class="block-role bg-slate-700 text-white text-sm rounded-lg px-3 py-1.5 border-none focus:ring-primary">
                            <option value="system">system</option>
                            <option value="user" selected>user</option>
                            <option value="assistant">assistant</option>
                        </select>
                        <button class="btn-delete-block p-1.5 text-slate-500 hover:text-rose-500 hover:bg-slate-700 rounded-lg transition-colors">
                            <span class="material-symbols-outlined text-lg">delete</span>
                        </button>
                    </div>
                    <textarea class="block-content w-full bg-slate-900 text-slate-100 rounded-lg p-4 border border-slate-600 focus:ring-2 focus:ring-primary/50 resize-y min-h-[100px] text-sm font-mono" placeholder="Digite a mensagem do usuário..."></textarea>
                </div>
            `;

            // Re-attach delete listeners
            document.querySelectorAll('.btn-delete-block').forEach(attachDeleteListener);

            // Reset output
            playgroundOutput.innerHTML = '<span class="text-slate-500 italic">A resposta aparecerá aqui...</span>';

            // Reset parameters
            if (paramTemperature) { paramTemperature.value = 0.7; tempValue.textContent = '0.70'; }
            if (paramMaxTokens) paramMaxTokens.value = 2048;
            if (paramTopP) { paramTopP.value = 0.9; toppValue.textContent = '0.90'; }
        });
    }

    // ===== AUTHENTICATION LOGIC =====
    let currentUser = null;

    async function checkAuth() {
        try {
            const res = await fetch('/api/user');
            if (res.ok) {
                const user = await res.json();
                currentUser = user;

                // Show Main Interface
                if (viewLock) viewLock.classList.add('hidden');
                if (viewDashboard) viewDashboard.classList.remove('hidden'); // Default view

                // Header: Show Profile, Hide Login
                if (btnLoginHeader) btnLoginHeader.classList.add('hidden');
                if (userProfileGroup) userProfileGroup.classList.remove('hidden');

                // Update UI with User Info
                updateUserProfile(user);

                console.log("Logged in as:", user.email);
            } else {
                // Show Lock Screen (Guest)
                if (viewLock) viewLock.classList.remove('hidden');

                // Hide other views (Security)
                [viewDashboard, viewChat, viewPlayground].forEach(v => v && v.classList.add('hidden'));

                // Header: Show Login, Hide Profile
                if (btnLoginHeader) btnLoginHeader.classList.remove('hidden');
                if (userProfileGroup) userProfileGroup.classList.add('hidden');
            }
        } catch (e) {
            console.error("Auth check failed", e);
            // Default to Lock Screen on error
            if (viewLock) viewLock.classList.remove('hidden');
            [viewDashboard, viewChat, viewPlayground].forEach(v => v && v.classList.add('hidden'));
        }
    }

    function updateUserProfile(user) {
        // Find avatar elements and update them
        // This assumes generic selectors or you might need to add IDs to HTML first
        // For now, let's console log, or find the "JD" circle
        const avatarCircles = document.querySelectorAll('.rounded-full.bg-primary.text-white');
        avatarCircles.forEach(el => {
            if (el.textContent.trim() === 'JD') {
                if (user.picture) {
                    el.innerHTML = `<img src="${user.picture}" class="w-full h-full rounded-full object-cover">`;
                    el.classList.remove('bg-primary', 'text-white'); // Remove fallback styles
                } else {
                    el.textContent = user.name ? user.name.charAt(0).toUpperCase() : 'U';
                }
            }
        });

        // Update Name/Email in dropdown
        const emailEl = document.getElementById('user-profile-email');
        if (emailEl) emailEl.textContent = user.email;
    }

    // Run Auth Check immediately
    checkAuth();

    // ===== SETTINGS MODAL LOGIC (New) =====
    const settingsModal = document.getElementById('settings-modal');
    const btnSettings = document.getElementById('btn-settings');
    const btnCloseSettings = document.getElementById('btn-close-settings');
    const settingsBackdrop = document.getElementById('settings-backdrop');
    const btnSaveSettings = document.getElementById('btn-save-settings');
    const btnResetSettings = document.getElementById('btn-reset-settings');

    if (btnSettings) {
        btnSettings.addEventListener('click', () => {
            if (settingsModal) settingsModal.classList.remove('hidden');
        });
    }

    if (btnCloseSettings) {
        btnCloseSettings.addEventListener('click', () => {
            if (settingsModal) settingsModal.classList.add('hidden');
        });
    }

    if (settingsBackdrop) {
        settingsBackdrop.addEventListener('click', () => {
            if (settingsModal) settingsModal.classList.add('hidden');
        });
    }

    // Temperature Slider in Settings
    const settingTemperature = document.getElementById('setting-temperature');
    const settingTempValue = document.getElementById('setting-temp-value');
    if (settingTemperature && settingTempValue) {
        settingTemperature.addEventListener('input', () => {
            settingTempValue.textContent = parseFloat(settingTemperature.value).toFixed(1);
        });
    }

    // Save Settings
    if (btnSaveSettings) {
        btnSaveSettings.addEventListener('click', () => {
            const settings = {
                ollamaUrl: document.getElementById('setting-ollama-url')?.value,
                model: document.getElementById('setting-model')?.value,
                temperature: document.getElementById('setting-temperature')?.value,
            };
            localStorage.setItem('llm-p2p-settings', JSON.stringify(settings));

            btnSaveSettings.innerHTML = '<span class="material-symbols-outlined">check</span> Salvo!';
            btnSaveSettings.classList.add('bg-emerald-600');
            setTimeout(() => {
                btnSaveSettings.innerHTML = 'Salvar Alterações';
                btnSaveSettings.classList.remove('bg-emerald-600');
                if (settingsModal) settingsModal.classList.add('hidden');
            }, 1500);
        });
    }

    // Reset Settings
    if (btnResetSettings) {
        btnResetSettings.addEventListener('click', () => {
            if (confirm('Restaurar configurações padrão?')) {
                localStorage.removeItem('llm-p2p-settings');
                alert('Configurações restauradas!');
            }
        });
    }

});

