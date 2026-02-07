
#!/bin/bash
#############################################
# Script de Configuração do Servidor LLM
# Debian 13 + Ollama + Llama 2 13B
# Projeto SRISM - Mestrado em Cibersegurança
#############################################

set -e

echo "=== Iniciando configuração do Servidor LLM ==="

# Atualizar sistema
echo "[1/10] Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "[2/10] Instalando dependências..."
apt install -y curl wget git ufw fail2ban python3 python3-pip python3-venv nginx

# Configurar firewall local
echo "[3/10] Configurando UFW..."
ufw default deny incoming
ufw default allow outgoing
ufw allow from 10.0.30.0/24 to any port 443 proto tcp  # LAN Users
ufw allow from 10.0.40.0/24 to any port 443 proto tcp  # Wi-Fi
ufw allow from 10.0.10.0/24 to any port 2222 proto tcp # SSH Gestão
ufw --force enable

# Instalar Ollama
echo "[4/10] Instalando Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Configurar serviço Ollama
echo "[5/10] Configurando serviço Ollama..."
systemctl enable ollama
systemctl start ollama

# Download do modelo Llama 2 13B
echo "[6/10] Baixando modelo Llama 2 13B (pode demorar)..."
ollama pull llama2:13b

# Criar ambiente Python para API
echo "[7/10] Configurando API REST..."
mkdir -p /opt/llm-api
cd /opt/llm-api
python3 -m venv venv
source venv/bin/activate
pip install flask flask-jwt-extended flask-limiter cryptography

# Criar aplicação API
cat > /opt/llm-api/app.py << 'EOF'
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import re

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'CHANGE_THIS_IN_PRODUCTION'
jwt = JWTManager(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

def sanitize_input(text):
    # Remover padrões suspeitos de prompt injection
    patterns = [
        r'ignore\s+(previous|all)\s+instructions',
        r'system\s*:',
        r'<\|im_start\|>',
        r'###\s*instruction',
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Suspicious input detected")
    return text[:2000]  # Limitar tamanho

@app.route('/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # Implementar autenticação real aqui
    if username == "demo" and password == "demo123":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad credentials"}), 401

@app.route('/chat', methods=['POST'])
@jwt_required()
@limiter.limit("100 per minute")
def chat():
    try:
        message = request.json.get('message', '')
        message = sanitize_input(message)
        
        # Chamar Ollama
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'llama2:13b',
            'prompt': message,
            'stream': False
        })
        
        return jsonify(response.json())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
EOF

# Configurar Nginx como reverse proxy
echo "[8/10] Configurando Nginx..."
cat > /etc/nginx/sites-available/llm-api << 'EOF'
server {
    listen 443 ssl http2;
    server_name llm-server.local;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    server_tokens off;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/llm-api /etc/nginx/sites-enabled/

# Gerar certificados SSL self-signed (substituir por Let's Encrypt em produção)
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=PT/ST=Porto/L=Porto/O=ESTG/CN=llm-server.local"

# Configurar Fail2ban
echo "[9/10] Configurando Fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 2222
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 300
bantime = 3600
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Hardening adicional
echo "[10/10] Aplicando hardening..."
# Desativar SSH root
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Configurar unattended-upgrades
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

echo ""
echo "=== Configuração concluída! ==="
echo "Próximos passos:"
echo "1. Configurar chaves SSH para acesso"
echo "2. Atualizar credenciais JWT em /opt/llm-api/app.py"
echo "3. Configurar certificados SSL válidos"
echo "4. Testar API: curl -k https://localhost/auth"
echo ""
