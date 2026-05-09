import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, ChevronDown } from 'lucide-react';
import { sendChat } from '../api';
import SourcePanel from './SourcePanel';

const DEMO_QUESTIONS = [
  'Which titles performed best in 2025?',
  'Why is Stellar Run trending?',
  'Compare Dark Orbit vs Last Kingdom',
  'Which city had strongest engagement last month?',
  'What explains weak comedy performance?',
  'What recommendations for leadership next quarter?',
];

export default function ChatPanel({ filters }) {
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState('');
  const [loading, setLoading]     = useState(false);
  const [activeSources, setActiveSources] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const buildHistory = () =>
    messages.map(m => ({ role: m.role, content: m.content }));

  const send = async (text) => {
    const question = text || input.trim();
    if (!question || loading) return;
    setInput('');
    setActiveSources(null);

    const userMsg = { role: 'user', content: question, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const result = await sendChat(question, buildHistory());
      const assistantMsg = {
        role:       'assistant',
        content:    result.answer,
        sources:    result.sources,
        tool_calls: result.tool_calls,
        duration_ms: result.duration_ms,
        id:         Date.now() + 1,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ Could not reach the backend. Is the API running?',
        id: Date.now() + 1,
        error: true,
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Left — conversation */}
      <div style={styles.chatCol}>

        {/* Header */}
        <div style={styles.header}>
          <div>
            <div style={styles.headerTitle}>Analytics Assistant</div>
            <div style={styles.headerSub}>
              Ask anything about CineVerse performance data
            </div>
          </div>
          {messages.length > 0 && (
            <button
              style={styles.clearBtn}
              onClick={() => { setMessages([]); setActiveSources(null); }}
            >
              Clear
            </button>
          )}
        </div>

        {/* Messages */}
        <div style={styles.messages}>
          {messages.length === 0 && (
            <div style={styles.empty}>
              <div style={styles.emptyTitle}>
                Start with a question
              </div>
              <div style={styles.suggestions}>
                {DEMO_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    style={styles.suggestion}
                    onClick={() => send(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div
              key={msg.id}
              style={{
                ...styles.msgRow,
                ...(msg.role === 'user' ? styles.msgRowUser : {}),
              }}
            >
              <div style={styles.avatar}>
                {msg.role === 'user'
                  ? <User size={14} />
                  : <Bot size={14} color="var(--gold)" />
                }
              </div>
              <div style={styles.msgContent}>
                <div style={{
                  ...styles.bubble,
                  ...(msg.role === 'user' ? styles.bubbleUser : styles.bubbleBot),
                  ...(msg.error ? { borderColor: 'var(--accent-red)' } : {}),
                }}>
                  {/* Render newlines as breaks */}
                  {msg.content.split('\n').map((line, i) => (
                    <span key={i}>{line}{i < msg.content.split('\n').length - 1 && <br/>}</span>
                  ))}
                </div>

                {/* Source chips */}
                {msg.sources?.length > 0 && (
                  <div style={styles.chips}>
                    {msg.sources.map((s, i) => (
                      <span key={i} style={styles.chip}>{s}</span>
                    ))}
                    <button
                      style={styles.traceBtn}
                      onClick={() => setActiveSources(
                        activeSources?.id === msg.id ? null : { ...msg, id: msg.id }
                      )}
                    >
                      {activeSources?.id === msg.id ? 'Hide trace' : 'Show trace'}
                      <ChevronDown size={11} />
                    </button>
                    <span style={styles.duration}>
                      {(msg.duration_ms / 1000).toFixed(1)}s
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={styles.msgRow}>
              <div style={styles.avatar}><Bot size={14} color="var(--gold)" /></div>
              <div style={styles.typing}>
                <span style={{ ...styles.dot, animationDelay: '0s' }} />
                <span style={{ ...styles.dot, animationDelay: '0.2s' }} />
                <span style={{ ...styles.dot, animationDelay: '0.4s' }} />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={styles.inputRow}>
          <input
            style={styles.input}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            placeholder="Ask a business question..."
            disabled={loading}
          />
          <button
            style={{
              ...styles.sendBtn,
              ...((!input.trim() || loading) ? styles.sendBtnDisabled : {}),
            }}
            onClick={() => send()}
            disabled={!input.trim() || loading}
          >
            <Send size={16} />
          </button>
        </div>
      </div>

      {/* Right — source trace panel */}
      {activeSources && (
        <SourcePanel
          sources={activeSources.sources}
          toolCalls={activeSources.tool_calls}
          onClose={() => setActiveSources(null)}
        />
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex', flex: 1, height: '100%', overflow: 'hidden',
  },
  chatCol: {
    flex: 1, display: 'flex', flexDirection: 'column',
    height: '100%', overflow: 'hidden',
  },
  header: {
    padding: '20px 24px 16px',
    borderBottom: '1px solid var(--border)',
    display: 'flex', alignItems: 'flex-start',
    justifyContent: 'space-between',
    background: 'var(--bg-surface)',
    flexShrink: 0,
  },
  headerTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: 22, fontWeight: 600,
    color: 'var(--text-primary)',
  },
  headerSub: {
    fontSize: 12, color: 'var(--text-muted)', marginTop: 2,
  },
  clearBtn: {
    background: 'none', border: '1px solid var(--border)',
    borderRadius: 'var(--radius)', color: 'var(--text-muted)',
    padding: '4px 12px', cursor: 'pointer', fontSize: 12,
    fontFamily: 'var(--font-body)',
  },
  messages: {
    flex: 1, overflowY: 'auto',
    padding: '20px 24px', display: 'flex',
    flexDirection: 'column', gap: 20,
  },
  empty: {
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', gap: 20,
    marginTop: 60,
  },
  emptyTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: 24, color: 'var(--text-muted)',
  },
  suggestions: {
    display: 'grid', gridTemplateColumns: '1fr 1fr',
    gap: 8, maxWidth: 560, width: '100%',
  },
  suggestion: {
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    color: 'var(--text-secondary)',
    padding: '10px 14px', cursor: 'pointer',
    fontSize: 12, fontFamily: 'var(--font-body)',
    textAlign: 'left', transition: 'all 0.15s',
    lineHeight: 1.4,
  },
  msgRow: {
    display: 'flex', gap: 12, alignItems: 'flex-start',
  },
  msgRowUser: {
    flexDirection: 'row-reverse',
  },
  avatar: {
    width: 28, height: 28, borderRadius: '50%',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    display: 'flex', alignItems: 'center',
    justifyContent: 'center', flexShrink: 0,
    color: 'var(--text-muted)',
  },
  msgContent: {
    display: 'flex', flexDirection: 'column', gap: 6,
    maxWidth: '75%',
  },
  bubble: {
    padding: '12px 16px',
    borderRadius: 'var(--radius-lg)',
    border: '1px solid',
    lineHeight: 1.7, fontSize: 13,
  },
  bubbleUser: {
    background: 'var(--gold-glow)',
    borderColor: 'var(--border-strong)',
    color: 'var(--text-primary)',
  },
  bubbleBot: {
    background: 'var(--bg-elevated)',
    borderColor: 'var(--border)',
    color: 'var(--text-primary)',
  },
  chips: {
    display: 'flex', alignItems: 'center',
    flexWrap: 'wrap', gap: 6,
  },
  chip: {
    fontSize: 10, fontFamily: 'var(--font-mono)',
    background: 'var(--bg-base)',
    border: '1px solid var(--border)',
    borderRadius: 3, padding: '2px 7px',
    color: 'var(--gold)',
  },
  traceBtn: {
    display: 'flex', alignItems: 'center', gap: 3,
    background: 'none', border: 'none',
    color: 'var(--text-muted)', cursor: 'pointer',
    fontSize: 11, fontFamily: 'var(--font-body)',
  },
  duration: {
    fontSize: 10, color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
  typing: {
    display: 'flex', gap: 5, alignItems: 'center',
    padding: '14px 18px',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
  },
  dot: {
    display: 'inline-block',
    width: 6, height: 6, borderRadius: '50%',
    background: 'var(--gold)',
    animation: 'pulse 1.2s ease-in-out infinite',
  },
  inputRow: {
    display: 'flex', gap: 10,
    padding: '16px 24px',
    borderTop: '1px solid var(--border)',
    background: 'var(--bg-surface)',
    flexShrink: 0,
  },
  input: {
    flex: 1, padding: '11px 16px',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    color: 'var(--text-primary)',
    fontSize: 13, fontFamily: 'var(--font-body)',
    outline: 'none',
  },
  sendBtn: {
    width: 42, height: 42,
    background: 'var(--gold)',
    border: 'none', borderRadius: 'var(--radius)',
    color: '#0e0e10', cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0,
  },
  sendBtnDisabled: {
    background: 'var(--bg-elevated)',
    color: 'var(--text-muted)', cursor: 'not-allowed',
  },
};