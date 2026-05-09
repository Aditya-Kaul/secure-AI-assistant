import { useState } from 'react';
import Sidebar    from './components/Sidebar';
import ChatPanel  from './components/ChatPanel';
import ChartView  from './components/ChartView';
import HistoryPanel from './components/HistoryPanel';
import { runIngest } from './api';

// Keyframe styles injected once
const keyframes = `
  @keyframes pulse {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50%       { opacity: 1;   transform: scale(1);   }
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
  }
  button:hover { opacity: 0.85; }
`;

export default function App() {
  const [view, setView]         = useState('chat');
  const [ingesting, setIngesting] = useState(false);
  const [toast, setToast]       = useState(null);

  const handleIngest = async () => {
    setIngesting(true);
    try {
      await runIngest();
      showToast('Data reloaded successfully', 'ok');
    } catch {
      showToast('Reload failed — check API', 'error');
    } finally {
      setIngesting(false);
    }
  };

  const showToast = (msg, type) => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <>
      <style>{keyframes}</style>

      <div style={styles.app}>
        <Sidebar
          active={view}
          onNav={setView}
          onIngest={handleIngest}
          ingesting={ingesting}
        />

        <main style={styles.main}>
          {view === 'chat'      && <ChatPanel />}
          {view === 'analytics' && <ChartView />}
          {view === 'history'   && <HistoryPanel />}
        </main>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          ...styles.toast,
          borderColor: toast.type === 'ok'
            ? 'var(--accent-green)' : 'var(--accent-red)',
        }}>
          {toast.msg}
        </div>
      )}
    </>
  );
}

const styles = {
  app: {
    display: 'flex', height: '100vh',
    overflow: 'hidden', background: 'var(--bg-base)',
  },
  main: {
    flex: 1, display: 'flex',
    overflow: 'hidden',
  },
  toast: {
    position: 'fixed', bottom: 24, right: 24,
    background: 'var(--bg-elevated)',
    border: '1px solid',
    borderRadius: 'var(--radius)',
    padding: '10px 18px',
    fontSize: 12, fontFamily: 'var(--font-mono)',
    color: 'var(--text-primary)',
    zIndex: 1000,
    animation: 'fadeIn 0.2s ease',
  },
};