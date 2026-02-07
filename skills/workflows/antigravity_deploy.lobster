name: "Antigravity Deploy"
description: "Deploy automatizado do sistema Antigravity"
version: "1.0"
author: "Cleudocode Team"

variables:
  antigravity_repo: "https://github.com/automacoescomerciaisintegradas/antigravity.git"
  deploy_path: "/opt/antigravity"
  backup_path: "./backups/deploy_{{ datetime }}"
  branch: "main"
  service_name: "antigravity"
  health_check_url: "http://localhost:8080/health"
  max_rollback_attempts: 3

steps:
  - name: "Criar diretório de backup para rollback"
    skill: "filesystem"
    action: "create_directory"
    params:
      path: "{{ backup_path }}"

  - name: "Verificar se o serviço está rodando"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl is-active {{ service_name }}"
      timeout: 10
    continue_on_error: true

  - name: "Fazer backup da versão atual"
    skill: "shell"
    action: "execute"
    params:
      command: "cp -r {{ deploy_path }}/* {{ backup_path }}/ 2>/dev/null || echo 'Primeira instalação'"
      timeout: 120

  - name: "Obter versão atual (se existir)"
    skill: "shell"
    action: "execute"
    params:
      command: "cd {{ deploy_path }} && git rev-parse HEAD 2>/dev/null || echo 'N/A'"
      timeout: 10
    continue_on_error: true

  - name: "Executar testes pré-deploy"
    skill: "shell"
    action: "execute"
    params:
      command: |
        echo "Executando testes pré-deploy..."
        # Verificar conectividade com repositório
        git ls-remote {{ antigravity_repo }} {{ branch }} > /dev/null
        echo "✅ Repositório acessível"
        
        # Verificar espaço em disco
        AVAILABLE=$(df -BG {{ deploy_path }} | tail -1 | awk '{print $4}' | sed 's/G//')
        if [ "$AVAILABLE" -lt 1 ]; then
          echo "❌ Espaço insuficiente"
          exit 1
        fi
        echo "✅ Espaço suficiente: ${AVAILABLE}GB"
        
        # Verificar permissões
        if [ ! -w "{{ deploy_path }}" ]; then
          echo "❌ Sem permissão de escrita"
          exit 1
        fi
        echo "✅ Permissões OK"
      timeout: 60

  - name: "Parar serviço para deploy"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl stop {{ service_name }} && sleep 3"
      timeout: 30
    continue_on_error: true

  - name: "Fazer clone/pull do repositório"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ -d "{{ deploy_path }}/.git" ]; then
          echo "Atualizando repositório existente..."
          cd {{ deploy_path }}
          git fetch origin
          git checkout {{ branch }}
          git pull origin {{ branch }}
        else
          echo "Clonando repositório..."
          rm -rf {{ deploy_path }}/*
          git clone -b {{ branch }} {{ antigravity_repo }} {{ deploy_path }}
        fi
      timeout: 300

  - name: "Obter nova versão"
    skill: "shell"
    action: "execute"
    params:
      command: "cd {{ deploy_path }} && git rev-parse HEAD"
      timeout: 10

  - name: "Instalar/atualizar dependências"
    skill: "shell"
    action: "execute"
    params:
      command: |
        cd {{ deploy_path }}
        if [ -f "requirements.txt" ]; then
          pip3 install -r requirements.txt
        elif [ -f "package.json" ]; then
          npm install
        elif [ -f "Cargo.toml" ]; then
          cargo build --release
        else
          echo "Nenhum arquivo de dependências encontrado"
        fi
      timeout: 600

  - name: "Executar build (se necessário)"
    skill: "shell"
    action: "execute"
    params:
      command: |
        cd {{ deploy_path }}
        if [ -f "Makefile" ]; then
          make build
        elif [ -f "build.sh" ]; then
          chmod +x build.sh && ./build.sh
        elif [ -f "package.json" ] && grep -q "build" package.json; then
          npm run build
        else
          echo "Nenhum processo de build necessário"
        fi
      timeout: 600
    continue_on_error: true

  - name: "Aplicar configurações"
    skill: "shell"
    action: "execute"
    params:
      command: |
        cd {{ deploy_path }}
        if [ -f "config/production.conf" ]; then
          cp config/production.conf /etc/{{ service_name }}/
        fi
        if [ -f "scripts/setup.sh" ]; then
          chmod +x scripts/setup.sh && ./scripts/setup.sh
        fi
        echo "Configurações aplicadas"
      timeout: 120
    continue_on_error: true

  - name: "Iniciar serviço"
    skill: "shell"
    action: "execute"
    params:
      command: "systemctl start {{ service_name }} && sleep 5"
      timeout: 60

  - name: "Aguardar inicialização"
    skill: "shell"
    action: "execute"
    params:
      command: |
        echo "Aguardando inicialização do serviço..."
        for i in {1..30}; do
          if systemctl is-active {{ service_name }} > /dev/null; then
            echo "Serviço ativo após ${i} tentativas"
            break
          fi
          sleep 2
        done
      timeout: 70

  - name: "Executar health check"
    skill: "shell"
    action: "execute"
    params:
      command: |
        echo "Executando health check..."
        for i in {1..10}; do
          RESPONSE=$(curl -s -o /dev/null -w '%{http_code}' {{ health_check_url }} 2>/dev/null || echo '000')
          if [ "$RESPONSE" = "200" ]; then
            echo "✅ Health check passou (tentativa $i)"
            exit 0
          fi
          echo "⏳ Health check falhou (tentativa $i): $RESPONSE"
          sleep 5
        done
        echo "❌ Health check falhou após 10 tentativas"
        exit 1
      timeout: 60
    retry: 2
    retry_delay: 10

  - name: "Executar testes pós-deploy"
    skill: "shell"
    action: "execute"
    params:
      command: |
        cd {{ deploy_path }}
        if [ -f "tests/smoke_test.sh" ]; then
          chmod +x tests/smoke_test.sh && ./tests/smoke_test.sh
        elif [ -f "package.json" ] && grep -q "test" package.json; then
          npm test
        else
          echo "✅ Nenhum teste específico configurado"
        fi
      timeout: 300
    continue_on_error: true

  - name: "Verificar se rollback é necessário"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ "{{ step_14_result.success }}" = "true" ] && [ "{{ step_15_result.success }}" = "true" ]; then
          echo "✅ Deploy bem-sucedido"
          exit 0
        else
          echo "❌ Deploy falhou - rollback necessário"
          exit 1
        fi
      timeout: 5
    continue_on_error: true

  - name: "Executar rollback (se necessário)"
    skill: "shell"
    action: "execute"
    params:
      command: |
        if [ "{{ step_16_result.success }}" = "false" ]; then
          echo "🔄 Iniciando rollback..."
          systemctl stop {{ service_name }}
          rm -rf {{ deploy_path }}/*
          cp -r {{ backup_path }}/* {{ deploy_path }}/
          systemctl start {{ service_name }}
          sleep 5
          if systemctl is-active {{ service_name }}; then
            echo "✅ Rollback concluído com sucesso"
          else
            echo "❌ Rollback falhou - intervenção manual necessária"
            exit 1
          fi
        else
          echo "✅ Rollback não necessário"
        fi
      timeout: 120
    continue_on_error: true

  - name: "Gerar relatório de deploy"
    skill: "filesystem"
    action: "write_file"
    params:
      filepath: "reports/deploy_{{ datetime }}.txt"
      content: |
        # Relatório de Deploy - Antigravity
        Data/Hora: {{ datetime }}
        
        ## Informações do Deploy
        Repositório: {{ antigravity_repo }}
        Branch: {{ branch }}
        Versão anterior: {{ step_3_result.stdout }}
        Versão nova: {{ step_7_result.stdout }}
        
        ## Status do Deploy
        {% if step_16_result.success %}✅ DEPLOY BEM-SUCEDIDO{% else %}❌ DEPLOY FALHOU{% endif %}
        {% if step_17_result.success == false %}🔄 ROLLBACK EXECUTADO{% endif %}
        
        ## Etapas Executadas
        Testes pré-deploy: {% if step_4_result.success %}✅ Passou{% else %}❌ Falhou{% endif %}
        Backup criado: {% if step_2_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Código atualizado: {% if step_6_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Dependências: {% if step_8_result.success %}✅ Instaladas{% else %}⚠️ Problemas{% endif %}
        Build: {% if step_9_result.success %}✅ Sucesso{% else %}⚠️ Não necessário ou falha{% endif %}
        Serviço iniciado: {% if step_11_result.success %}✅ Sim{% else %}❌ Falha{% endif %}
        Health check: {% if step_14_result.success %}✅ Passou{% else %}❌ Falhou{% endif %}
        Testes pós-deploy: {% if step_15_result.success %}✅ Passou{% else %}⚠️ Não executado ou falha{% endif %}
        
        ## Status Final do Serviço
        Serviço ativo: $(systemctl is-active {{ service_name }})
        Health check: $(curl -s -o /dev/null -w '%{http_code}' {{ health_check_url }} 2>/dev/null || echo 'N/A')
        
        ## Backup para Rollback
        Localização: {{ backup_path }}
        Disponível até: $(date -d '+7 days' '+%Y-%m-%d')
        
        ---
        Relatório gerado pelo Cleudocode Workflow Engine
      overwrite: true

  - name: "Notificar resultado do deploy"
    skill: "telegram"
    action: "send_message"
    params:
      message: |
        🚀 *Antigravity Deploy Completo*
        
        📊 *Status:* {% if step_16_result.success %}✅ Sucesso{% else %}❌ Falhou{% endif %}
        {% if step_17_result.success == false %}🔄 *Rollback executado*{% endif %}
        
        🔄 *Versões:*
        • Anterior: `{{ step_3_result.stdout }}`
        • Nova: `{{ step_7_result.stdout }}`
        
        🧪 *Testes:*
        • Pré-deploy: {% if step_4_result.success %}✅ OK{% else %}❌ Falha{% endif %}
        • Health check: {% if step_14_result.success %}✅ OK{% else %}❌ Falha{% endif %}
        • Pós-deploy: {% if step_15_result.success %}✅ OK{% else %}⚠️ N/A{% endif %}
        
        🔧 *Serviço:* $(systemctl is-active {{ service_name }})
        🌐 *API:* $(curl -s -o /dev/null -w '%{http_code}' {{ health_check_url }} 2>/dev/null || echo 'N/A')
        
        📄 *Relatório:* `reports/deploy_{{ datetime }}.txt`
        💾 *Backup:* `{{ backup_path }}`
    continue_on_error: true