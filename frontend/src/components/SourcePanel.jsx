import { X, Database, FileText, Table } from 'lucide-react';

const TOOL_ICONS = {
  query_database:   { icon: Database,  color: '#5f9fd4', label: 'SQL' },
  search_documents: { icon: FileText,  color: '#c9a84c', label: 'PDF' },
  analyze_csv:      { icon: Table,     color: '#4caf82', label: 'CSV' },
};

export default function SourcePanel({ sources, toolCalls, onClose }) {
  return (
    <div style={styles.panel}>
      <div style={styles.header}>
        <span style={styles.title}>Source Trace</span>
        <button style={styles.close} onClick={onClose}>
          <X size={14} />
        </button>
      </div>

      {/* Sources summary */}
      <div style={styles.section}>
        <div style={styles.label}>Sources used</div>
        <div style={styles.sourceList}>
          {sources.map((s, i) => (
            <span key={i} style={styles.sourceChip}>{s}</span>
          ))}
        </div>
      </div>

      <div style={styles.divider} />

      {/* Tool call trace */}
      <div style={styles.section}>
        <div style={styles.label}>Tool calls ({toolCalls.length})</div>
        <div style={styles.traceList}>
          {toolCalls.map((tc, i) => {
            const meta = TOOL_ICONS[tc.tool] || { icon: Database, color: '#888', label: tc.tool };
            const Icon = meta.icon;
            return (
              <div key={i} style={styles.traceItem}>
                {/* Tool header */}
                <div style={styles.traceHeader}>
                  <div style={{ ...styles.traceIcon, color: meta.color }}>
                    <Icon size={12} />
                  </div>
                  <span style={{ ...styles.toolName, color: meta.color }}>
                    {meta.label}
                  </span>
                  <span style={styles.roundBadge}>round {tc.round}</span>
                  <span style={{
                    ...styles.statusDot,
                    background: tc.output?.success === false
                      ? 'var(--accent-red)' : 'var(--accent-green)',
                  }} />
                </div>

                {/* Input */}
                <div style={styles.traceBlock}>
                  <div style={styles.blockLabel}>Input</div>
                  <pre style={styles.pre}>
                    {JSON.stringify(tc.input, null, 2)}
                  </pre>
                </div>

                {/* Output summary */}
                <div style={styles.traceBlock}>
                  <div style={styles.blockLabel}>Result</div>
                  <pre style={styles.pre}>
                    {tc.output?.error
                      ? `Error: ${tc.output.error}`
                      : tc.output?.row_count !== undefined
                        ? `${tc.output.row_count} rows returned`
                        : tc.output?.result_count !== undefined
                          ? `${tc.output.result_count} documents`
                          : tc.output?.row_count !== undefined
                            ? `${tc.output.row_count} rows`
                            : JSON.stringify(tc.output).slice(0, 120) + '…'
                    }
                  </pre>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

const styles = {
  panel: {
    width: 320, flexShrink: 0,
    borderLeft: '1px solid var(--border)',
    background: 'var(--bg-surface)',
    display: 'flex', flexDirection: 'column',
    overflowY: 'auto',
  },
  header: {
    display: 'flex', alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 16px 12px',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  title: {
    fontFamily: 'var(--font-display)',
    fontSize: 16, fontWeight: 600,
    color: 'var(--gold)',
  },
  close: {
    background: 'none', border: 'none',
    color: 'var(--text-muted)', cursor: 'pointer',
    display: 'flex', alignItems: 'center',
  },
  section: { padding: '12px 16px' },
  label: {
    fontSize: 10, letterSpacing: '0.1em',
    textTransform: 'uppercase',
    color: 'var(--text-muted)', marginBottom: 8,
  },
  sourceList: { display: 'flex', flexWrap: 'wrap', gap: 6 },
  sourceChip: {
    fontSize: 11, fontFamily: 'var(--font-mono)',
    background: 'var(--bg-elevated)',
    border: '1px solid var(--border-strong)',
    borderRadius: 3, padding: '3px 8px',
    color: 'var(--gold)',
  },
  divider: { height: 1, background: 'var(--border)', margin: '0 16px' },
  traceList: { display: 'flex', flexDirection: 'column', gap: 12 },
  traceItem: {
    background: 'var(--bg-elevated)',
    borderRadius: 'var(--radius)',
    border: '1px solid var(--border)',
    overflow: 'hidden',
  },
  traceHeader: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '8px 12px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-base)',
  },
  traceIcon: { display: 'flex', alignItems: 'center' },
  toolName: {
    fontSize: 11, fontFamily: 'var(--font-mono)',
    fontWeight: 500,
  },
  roundBadge: {
    marginLeft: 'auto',
    fontSize: 9, color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
  statusDot: {
    width: 6, height: 6, borderRadius: '50%',
  },
  traceBlock: { padding: '8px 12px' },
  blockLabel: {
    fontSize: 9, textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: 'var(--text-muted)', marginBottom: 4,
  },
  pre: {
    fontFamily: 'var(--font-mono)',
    fontSize: 10, color: 'var(--text-secondary)',
    whiteSpace: 'pre-wrap', wordBreak: 'break-all',
    lineHeight: 1.5,
  },
};