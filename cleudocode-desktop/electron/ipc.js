import { ipcMain } from 'electron';
import { startAuthFlow, getValidAccessToken, logout, loadTokens } from './codexAuth.js';

export const setupIpc = () => {
    ipcMain.handle('codex-auth:start', async (event, clientId) => {
        return await startAuthFlow(clientId);
    });

    ipcMain.handle('codex-auth:get-status', () => {
        const tokens = loadTokens();
        if (tokens && tokens.access_token) {
            return {
                authenticated: true,
                account_id: tokens.account_id,
                client_id: tokens.client_id
            };
        }
        return { authenticated: false };
    });

    ipcMain.handle('codex-auth:get-token', async () => {
        const tokenResult = await getValidAccessToken();
        return tokenResult ? tokenResult.access_token : null;
    });

    ipcMain.handle('codex-auth:logout', () => {
        logout();
        return true;
    });

    ipcMain.handle('codex-api:stream-request', async (event, payload) => {
        const tokenResult = await getValidAccessToken();
        if (!tokenResult) {
            return { error: true, status: 401, message: 'Not authenticated' };
        }

        let instructions = '';
        const transformedInput = [];

        for (const item of payload.input) {
            if (item.role === 'system') {
                instructions = item.content;
            } else {
                transformedInput.push({
                    type: 'message',
                    role: item.role,
                    content: item.content,
                });
            }
        }

        try {
            const response = await fetch('https://chatgpt.com/backend-api/codex/responses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${tokenResult.access_token}`,
                    'Chatgpt-Account-Id': tokenResult.account_id,
                },
                body: JSON.stringify({
                    model: payload.model || 'gpt-4o',
                    instructions,
                    input: transformedInput,
                    stream: true,
                    store: false,
                }),
            });

            if (!response.ok) {
                throw new Error(`Codex API Error: ${response.status} ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');

            while (true) {
                const { value, done } = await reader.read();

                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    event.sender.send('codex-api:stream-chunk', { chunk });
                }

                if (done) break;
            }

            event.sender.send('codex-api:stream-end', {});
            return { success: true };
        } catch (e) {
            return { error: true, message: e.message };
        }
    });
};
