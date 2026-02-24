import { app, safeStorage } from 'electron';
import crypto from 'crypto';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { URL } from 'url';

const REDIRECT_PORT = 18901;
const AUTHORIZE_URL = 'https://auth.openai.com/oauth/authorize';
const TOKEN_URL = 'https://auth.openai.com/oauth/token';

let server = null;
let currentCodeVerifier = null;

const getTokensPath = () => path.join(app.getPath('userData'), 'codex_tokens.enc');

export const loadTokens = () => {
    const tokenPath = getTokensPath();
    if (!fs.existsSync(tokenPath)) return null;

    try {
        const encryptedData = fs.readFileSync(tokenPath);
        if (!safeStorage.isEncryptionAvailable()) return null;
        const decryptedString = safeStorage.decryptString(encryptedData);
        return JSON.parse(decryptedString);
    } catch (error) {
        console.error('Failed to load or decrypt tokens:', error);
        return null;
    }
};

const saveTokens = (tokens) => {
    const tokenPath = getTokensPath();
    try {
        if (!safeStorage.isEncryptionAvailable()) {
            console.warn('SafeStorage not available; storing tokens unencrypted (not recommended for production).');
            fs.writeFileSync(tokenPath, JSON.stringify(tokens));
            return;
        }
        const encryptedData = safeStorage.encryptString(JSON.stringify(tokens));
        fs.writeFileSync(tokenPath, encryptedData);
    } catch (error) {
        console.error('Failed to save tokens:', error);
    }
};

const exchangeCodeForTokens = async (code, codeVerifier, clientId) => {
    const response = await fetch(TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: clientId,
            code,
            redirect_uri: `http://localhost:${REDIRECT_PORT}/auth/callback`,
            code_verifier: codeVerifier,
        }),
    });

    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Token exchange failed: ${errText}`);
    }

    const tokenData = await response.json();

    // Extract account_id from JWT id_token
    const parts = tokenData.id_token.split('.');
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString());
    const accountId = payload['https://api.openai.com/auth.chatgpt_account_id'];

    const tokens = {
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token,
        id_token: tokenData.id_token,
        expires_at: Date.now() + (tokenData.expires_in * 1000),
        account_id: accountId,
        client_id: clientId // Persiste o Client ID para Refresh Automático
    };

    saveTokens(tokens);
    return tokens;
};

export const refreshAccessToken = async (refreshToken, clientId) => {
    const response = await fetch(TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            grant_type: 'refresh_token',
            client_id: clientId,
            refresh_token: refreshToken
        })
    });

    if (!response.ok) {
        throw new Error('Failed to refresh token');
    }
    const tokenData = await response.json();

    const parts = tokenData.id_token.split('.');
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString());
    const accountId = payload['https://api.openai.com/auth.chatgpt_account_id'];

    return {
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token || refreshToken, // fallback caso provider não emita novo refresh token
        id_token: tokenData.id_token,
        expires_at: Date.now() + (tokenData.expires_in * 1000),
        account_id: accountId,
        client_id: clientId
    };
};

export const getValidAccessToken = async () => {
    const tokens = loadTokens();
    if (!tokens) return null;

    const isExpired = Date.now() >= (tokens.expires_at - 60000);
    if (!isExpired) {
        return {
            access_token: tokens.access_token,
            account_id: tokens.account_id,
        };
    }

    if (!tokens.refresh_token || !tokens.client_id) return null;

    try {
        const refreshed = await refreshAccessToken(tokens.refresh_token, tokens.client_id);
        const updated = { ...tokens, ...refreshed };
        saveTokens(updated);
        return {
            access_token: updated.access_token,
            account_id: updated.account_id
        };
    } catch (error) {
        console.error('Error refreshing token:', error);
        return null;
    }
};

export const startAuthFlow = (clientId) => {
    return new Promise((resolve, reject) => {
        if (!clientId) {
            return resolve({ success: false, error: "Client ID cannot be empty." });
        }

        // 1. Generate PKCE
        const codeVerifier = crypto.randomBytes(96).toString('base64url');
        currentCodeVerifier = codeVerifier;

        const codeChallenge = crypto.createHash('sha256').update(codeVerifier).digest('base64url');
        const state = crypto.randomBytes(32).toString('base64url');

        // 2. Start Local Server
        if (server) {
            server.close();
        }

        server = http.createServer(async (req, res) => {
            const url = new URL(req.url, `http://localhost:${REDIRECT_PORT}`);
            if (url.pathname === '/auth/callback') {
                if (url.searchParams.get('state') !== state) {
                    res.writeHead(400);
                    res.end('State mismatch - request may have been tampered with');
                    return;
                }

                const code = url.searchParams.get('code');
                const error = url.searchParams.get('error');

                if (error) {
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end(`<h1>Login Failed</h1><p>${error}</p>`);
                    server.close();
                    resolve({ success: false, error });
                    return;
                }

                try {
                    const tokens = await exchangeCodeForTokens(code, codeVerifier, clientId);
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end('<h1>Login Successful!</h1><p>You can close this tab and return to the Cleudocode app.</p><script>window.close()</script>');
                    server.close();
                    resolve({ success: true, account_id: tokens.account_id });
                } catch (exchError) {
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end(`<h1>Exchange Failed</h1><p>${exchError.message}</p>`);
                    server.close();
                    resolve({ success: false, error: exchError.message });
                }
            }
        });

        server.listen(REDIRECT_PORT, () => {
            // 3. Open Browser
            const authUrl = `${AUTHORIZE_URL}?response_type=code&client_id=${clientId}&redirect_uri=http://localhost:${REDIRECT_PORT}/auth/callback&scope=offline_access%20openid%20profile%20email&state=${state}&code_challenge=${codeChallenge}&code_challenge_method=S256`;
            import('electron').then(({ shell }) => shell.openExternal(authUrl));
        });
    });
};

export const logout = () => {
    const tokenPath = getTokensPath();
    if (fs.existsSync(tokenPath)) {
        fs.unlinkSync(tokenPath);
    }
};
