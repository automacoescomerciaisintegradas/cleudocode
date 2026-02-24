import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
    codexAuth: {
        start: (clientId) => ipcRenderer.invoke('codex-auth:start', clientId),
        getStatus: () => ipcRenderer.invoke('codex-auth:get-status'),
        getToken: () => ipcRenderer.invoke('codex-auth:get-token'),
        logout: () => ipcRenderer.invoke('codex-auth:logout'),
        codexApi: {
            streamRequest: (payload) => ipcRenderer.invoke('codex-api:stream-request', payload),
            onStreamChunk: (callback) => {
                const listener = (_event, data) => callback(data);
                ipcRenderer.on('codex-api:stream-chunk', listener);
                return () => ipcRenderer.removeListener('codex-api:stream-chunk', listener);
            },
            onStreamEnd: (callback) => {
                const listener = (_event, data) => callback(data);
                ipcRenderer.on('codex-api:stream-end', listener);
                return () => ipcRenderer.removeListener('codex-api:stream-end', listener);
            },
        }
    }
});
