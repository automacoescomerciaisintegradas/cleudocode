/**
 * Cleudocode OAuth + Webhook Backend Server
 * ========================================
 * Handles OAuth2 callbacks (Instagram) and Telegram Webhooks.
 */

require('dotenv').config({ path: '../../.env' });
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.CLEUDOCODE_OAUTH_PORT || 18903;
const GATEWAY_URL = process.env.CLEUDOCODE_GATEWAY_URL || 'http://localhost:18900';
const GATEWAY_TOKEN = process.env.CLEUDOCODE_GATEWAY_TOKEN;

app.use(cors());
app.use(express.json());

const TOKEN_STORAGE = path.join(__dirname, '../config/tokens.json');

const saveToken = (provider, data) => {
    let tokens = {};
    if (fs.existsSync(TOKEN_STORAGE)) {
        tokens = JSON.parse(fs.readFileSync(TOKEN_STORAGE));
    }
    tokens[provider] = { ...data, updated_at: new Date().toISOString() };
    fs.writeFileSync(TOKEN_STORAGE, JSON.stringify(tokens, null, 2));
};

/**
 * Health Check
 */
app.get('/health', (req, res) => {
    res.json({ status: 'online', service: 'Cleudocode OAuth & Webhook Server' });
});

/**
 * TELEGRAM WEBHOOK ENDPOINT
 * Recebe mensagens do Bot do Telegram e encaminha para o Orquestrador
 */
app.post('/webhook/telegram', async (req, res) => {
    const update = req.body;

    // AIDEV-NOTE: Registra o log básico da mensagem
    if (update.message && update.message.text) {
        const chatId = update.message.chat.id;
        const text = update.message.text;

        console.log(`📩 Webhook Telegram [${chatId}]: ${text.substring(0, 50)}...`);

        // Encaminha para o Orquestrador via Gateway
        try {
            await axios.post(`${GATEWAY_URL}/api/process-offer`, {
                source: 'telegram',
                chat_id: chatId,
                text: text
            }, {
                headers: { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }
            });
            console.log('✅ Mensagem enviada para o Orquestrador.');
        } catch (err) {
            console.error('❌ Erro ao enviar para o Orquestrador:', err.message);
        }
    }

    res.sendStatus(200); // Responde OK para o Telegram
});

/**
 * INSTAGRAM OAUTH FLOW
 */
app.get('/oauth/instagram/login', (req, res) => {
    const clientId = process.env.INSTAGRAM_CLIENT_ID;
    const redirectUri = process.env.INSTAGRAM_REDIRECT_URI;
    const authUrl = `https://api.instagram.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=user_profile,user_media&response_type=code`;
    res.redirect(authUrl);
});

app.get('/oauth/instagram/callback', async (req, res) => {
    const { code } = req.query;
    try {
        const response = await axios.post('https://api.instagram.com/oauth/access_token', new URLSearchParams({
            client_id: process.env.INSTAGRAM_CLIENT_ID,
            client_secret: process.env.INSTAGRAM_CLIENT_SECRET,
            grant_type: 'authorization_code',
            redirect_uri: process.env.INSTAGRAM_REDIRECT_URI,
            code: code
        }).toString());

        const shortToken = response.data.access_token;
        const longLivedResponse = await axios.get('https://graph.instagram.com/access_token', {
            params: {
                grant_type: 'ig_exchange_token',
                client_secret: process.env.INSTAGRAM_CLIENT_SECRET,
                access_token: shortToken
            }
        });

        saveToken('instagram', longLivedResponse.data);
        res.send('<h1>✅ Instagram Conectado!</h1>');
    } catch (err) {
        res.status(500).json({ error: 'OAuth Fail', details: err.message });
    }
});

/**
 * API TOKENS (Para Agente Python)
 */
app.get('/api/tokens/:provider', (req, res) => {
    const { provider } = req.params;
    const authHeader = req.headers.authorization;

    if (!authHeader || authHeader !== `Bearer ${GATEWAY_TOKEN}`) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    if (fs.existsSync(TOKEN_STORAGE)) {
        const tokens = JSON.parse(fs.readFileSync(TOKEN_STORAGE));
        if (tokens[provider]) return res.json(tokens[provider]);
    }
    res.status(404).json({ error: 'Not found' });
});

app.listen(PORT, () => {
    console.log(`🚀 Cleudocode Backend (OAuth + Webhook) rodando em http://localhost:${PORT}`);
});
