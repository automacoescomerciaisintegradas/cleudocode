import { useState, useCallback, useEffect } from 'react';

export const useCodexAuth = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState({ authenticated: false, account_id: null, client_id: null });

    const checkStatus = useCallback(async () => {
        try {
            const currentStatus = await window.electronAPI.codexAuth.getStatus();
            setStatus(currentStatus);
        } catch (err) {
            console.error("Failed to check status", err);
        }
    }, []);

    useEffect(() => {
        checkStatus();
    }, [checkStatus]);

    const startAuth = useCallback(async (clientId) => {
        setLoading(true);
        setError(null);
        try {
            const result = await window.electronAPI.codexAuth.start(clientId);
            if (result.success) {
                setStatus({ authenticated: true, account_id: result.account_id, client_id: clientId });
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        await window.electronAPI.codexAuth.logout();
        setStatus({ authenticated: false, account_id: null, client_id: null });
    }, []);

    return { status, loading, error, startAuth, logout, checkStatus };
};
