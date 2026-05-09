import { useEffect, useState } from 'react';
import { Clock, ChevronDown, ChevronRight } from 'lucide-react';
import { getHistory } from '../api';

export default function HistoryPanel() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    getHistory(30)
      .then(d => setHistory(d.history || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => setExpanded(expanded === id ? null : id);

  if (loading) return (
    <div style={styles.state}>Loading history...</div>
  );

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div style={styles.title}>Query History</div>
        <div style={styles.sub}>{history.length} past queries</div>
      </div>

      {history.length === 0 && (
        <div style={styles.empty}>
          No queries yet — ask the assistant something.
        </div>
      )}

      <div style={styles.list}>
        {history.map((item) => (
          <div key={item.id} style={styles.item}>
            {/* Row */}
            <button
              style={styles.itemHeader}
              onClick={() => toggle(item.id)}
            >
              <Clock size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              <div style={styles.itemQuestion}>{item.question}</div>
              <div style={styles.itemMeta}>
                <span style={styles.metaChip}>
                  {item.sources?.length || 0} sources
                </span>
                <span style={styles.metaTime}>
                  {new Date(item.created_at).toLocaleTimeString()}
                </span>
                {expanded === item.id
                  ? <ChevronDown size={13} />
                  : <ChevronRight size={13} />
                }
              </div>
            </button>

            {/* Expanded */}
            {expanded === item.id && (
              <div style={styles.itemBody}>
                <div style={styles.bodyLabel}>Answer</div>
                <div style={styles.bodyAnswer}>{item.answer}</div>

                <div style={styles.bodyLabel}>Sources</div>
                <div style={styles.chips}>
                  {(item.sources || []).map((s, i) => (
                    <span key={i} style={styles.chip}>{s}</span>
                  ))}
                </div>

                <div style={styles.bodyLabel}>
                  Tool calls ({item.tool_calls?.length || 0})
                </div>
                {(item.tool_calls || []).map((tc, i) => (
                  <div key={i} style={styles.toolRow}>
                    <span style={styles.toolName}>{tc.tool}</span>
                    <span style={styles.toolInput}>
                      {JSON.stringify(tc.input).slice(0, 80)}…
                    </span>
                  </div>
                ))}

                <div style={styles.duration}>
                  {(item.duration_ms / 1000).toFixed(1)}s response time
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  page: {
    flex: 1, overflowY: 'auto',
    padding: '24px', background: 'var(--bg-base)',
  },
  state: {
    flex: 1, display: 'flex',
    alignItems: 'center', justifyContent: 'center',
    color: 'var(--text-muted)',
  },
  header: { marginBottom: 20 },
  title: {
    fontFamily: 'var(--font-display)',
    fontSize: 26, fontWeight: 600,
    color: 'var(--text-primary)',
  },
  sub: { fontSize: 12, color: 'var(--text-muted)', marginTop: 4 },
  empty: {
    color: 'var(--text-muted)', fontSize: 13,
    fontFamily: 'var(--font-mono)',
  },
  list: { display: 'flex', flexDirection: 'column', gap: 8 },
  item: {
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    overflow: 'hidden',
  },
  itemHeader: {
    display: 'flex', alignItems: 'center',
    gap: 12, width: '100%',
    padding: '12px 16px',
    background: 'none', border: 'none',
    cursor: 'pointer', textAlign: 'left',
    color: 'var(--text-primary)',
    fontFamily: 'var(--font-body)',
  },
  itemQuestion: {
    flex: 1, fontSize: 13,
    color: 'var(--text-primary)',
  },
  itemMeta: {
    display: 'flex', alignItems: 'center',
    gap: 8, flexShrink: 0,
    color: 'var(--text-muted)',
  },
  metaChip: {
    fontSize: 10, fontFamily: 'var(--font-mono)',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border)',
    borderRadius: 3, padding: '2px 6px',
    color: 'var(--gold)',
  },
  metaTime: {
    fontSize: 10, fontFamily: 'var(--font-mono)',
    color: 'var(--text-muted)',
  },
  itemBody: {
    borderTop: '1px solid var(--border)',
    padding: '14px 16px',
    display: 'flex', flexDirection: 'column', gap: 8,
    background: 'var(--bg-elevated)',
  },
  bodyLabel: {
    fontSize: 9, textTransform: 'uppercase',
    letterSpacing: '0.1em', color: 'var(--text-muted)',
    marginTop: 4,
  },
  bodyAnswer: {
    fontSize: 12, color: 'var(--text-secondary)',
    lineHeight: 1.6, fontFamily: 'var(--font-body)',
  },
  chips: { display: 'flex', flexWrap: 'wrap', gap: 5 },
  chip: {
    fontSize: 10, fontFamily: 'var(--font-mono)',
    background: 'var(--bg-base)',
    border: '1px solid var(--border-strong)',
    borderRadius: 3, padding: '2px 7px', color: 'var(--gold)',
  },
  toolRow: {
    display: 'flex', gap: 10, alignItems: 'baseline',
    fontFamily: 'var(--font-mono)', fontSize: 11,
  },
  toolName: { color: 'var(--accent-blue)', flexShrink: 0 },
  toolInput: { color: 'var(--text-muted)', wordBreak: 'break-all' },
  duration: {
    fontSize: 10, color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)', marginTop: 4,
  },
};