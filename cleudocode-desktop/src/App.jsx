import { useState, useEffect, useRef } from 'react';
import { useCodexAuth } from './hooks/useCodexAuth';

function App() {
  const { status, loading, error, startAuth, logout } = useCodexAuth();
  const [clientIdInput, setClientIdInput] = useState('');

  const [prompt, setPrompt] = useState('Create a hello world in Python and explain the code.');
  const [model, setModel] = useState('gpt-4o');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const streamEndListenerRef = useRef(null);
  const streamChunkListenerRef = useRef(null);

  useEffect(() => {
    if (window.electronAPI) {
      streamChunkListenerRef.current = window.electronAPI.codexAuth.codexApi.onStreamChunk((data) => {
        setResponse((prev) => prev + data.chunk);
      });
      streamEndListenerRef.current = window.electronAPI.codexAuth.codexApi.onStreamEnd(() => {
        setIsStreaming(false);
      });
    }

    return () => {
      if (streamChunkListenerRef.current) streamChunkListenerRef.current();
      if (streamEndListenerRef.current) streamEndListenerRef.current();
    };
  }, []);

  const handleLogin = () => {
    if (!clientIdInput.trim()) {
      alert("Please enter a valid OpenAI Client ID string (e.g., app_xyz).");
      return;
    }
    startAuth(clientIdInput.trim());
  };

  const handleTestApi = async () => {
    if (!status.authenticated) return;
    setResponse('');
    setIsStreaming(true);

    const payload = {
      model: model,
      input: [
        { role: 'system', content: 'You are a helpful coding assistant.' },
        { role: 'user', content: prompt }
      ]
    };

    const result = await window.electronAPI.codexAuth.codexApi.streamRequest(payload);
    if (result.error) {
      setResponse(`Error: ${result.message}`);
      setIsStreaming(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', maxWidth: 800, margin: '0 auto', color: '#333' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        🚀 Cleudocode Native Client
      </h1>

      {/* AUTHENTICATION SECTION */}
      <div style={{ padding: '1.5rem', border: '1px solid #ddd', borderRadius: 12, marginBottom: '2rem', background: '#f8f9fa', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        <h2>Authentication</h2>

        {loading && <p>Loading authentication flow...</p>}
        {error && <p style={{ color: '#d9534f', padding: '10px', background: '#fdf3f2', borderRadius: '5px' }}>Error: {error}</p>}

        {status.authenticated ? (
          <div>
            <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
              <p style={{ color: '#2e7d32', fontWeight: 'bold', margin: '0 0 10px 0' }}>✅ Assinado via PKCE</p>
              <div style={{ fontSize: '0.9rem', color: '#555' }}>
                <p style={{ margin: '5px 0' }}><strong>Account ID:</strong> {status.account_id}</p>
                <p style={{ margin: '5px 0' }}><strong>Active Client ID:</strong> {status.client_id}</p>
              </div>
            </div>
            <button onClick={logout} style={btnStyle('#d9534f')}>Disconnect / Logout</button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <p style={{ color: '#666', fontSize: '0.95rem', margin: 0 }}>This client connects directly point-to-point to the undocumented ChatGPT backend APIs securely using OS keychains. Please input your Client ID below to authorize.</p>

            <div>
              <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '5px' }}>Client ID</label>
              <input
                type="text"
                placeholder="e.g. app_AxxYbbZcc..."
                value={clientIdInput}
                onChange={(e) => setClientIdInput(e.target.value)}
                style={inputStyle}
              />
            </div>

            <button onClick={handleLogin} style={btnStyle('#0d6efd', !clientIdInput.trim())} disabled={!clientIdInput.trim() || loading}>
              Login to ChatGPT
            </button>
          </div>
        )}
      </div>

      {/* CHAT/TEST SECTION */}
      {status.authenticated && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', animation: 'fadeIn 0.5s' }}>
          <h2>Test Codex API (Streaming)</h2>

          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '5px' }}>Model</label>
            <select value={model} onChange={(e) => setModel(e.target.value)} style={inputStyle}>
              <option value="gpt-4o">GPT-4o (Default Fast)</option>
              <option value="gpt-4">GPT-4 Legacy</option>
              <option value="o1-preview">o1-preview (Reasoning)</option>
              <option value="o1-mini">o1-mini (Fast Reasoning)</option>
              <option value="chatgpt-4o-latest">ChatGPT-4o-Latest</option>
            </select>
          </div>

          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '5px' }}>Prompt Input</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              rows={4}
              disabled={isStreaming}
              style={{ ...inputStyle, resize: 'vertical' }}
            />
          </div>

          <div>
            <button onClick={handleTestApi} disabled={isStreaming || !prompt.trim()} style={btnStyle('#198754', isStreaming || !prompt.trim())}>
              {isStreaming ? 'Generating Stream...' : 'Send Prompt'}
            </button>
          </div>

          <div style={{
            marginTop: '10px',
            padding: '20px',
            background: '#1e1e1e',
            color: '#d4d4d4',
            borderRadius: 10,
            whiteSpace: 'pre-wrap',
            minHeight: 200,
            overflowY: 'auto',
            maxHeight: '400px',
            fontFamily: 'monospace',
            lineHeight: '1.5',
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)'
          }}>
            {response || (isStreaming ? 'Waiting for stream connection...' : 'Stream response will be appended block-by-block here...')}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Styles
const inputStyle = {
  width: '100%',
  padding: '12px',
  boxSizing: 'border-box',
  borderRadius: '6px',
  border: '1px solid #ccc',
  fontSize: '1rem',
  outline: 'none',
  transition: 'border-color 0.2s',
};

const btnStyle = (bg, disabled = false) => ({
  backgroundColor: disabled ? '#ccc' : bg,
  color: disabled ? '#666' : 'white',
  border: 'none',
  padding: '12px 20px',
  borderRadius: 6,
  cursor: disabled ? 'not-allowed' : 'pointer',
  fontWeight: 'bold',
  fontSize: '1rem',
  transition: 'background-color 0.2s, transform 0.1s',
  boxShadow: disabled ? 'none' : '0 2px 4px rgba(0,0,0,0.1)'
});

export default App;
