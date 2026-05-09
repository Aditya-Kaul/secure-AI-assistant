import { useState } from 'react';
import { MessageSquare, BarChart2, Clock, RefreshCw, Film } from 'lucide-react';

const NAV = [
  { id: 'chat',      label: 'Assistant',  icon: MessageSquare },
  { id: 'analytics', label: 'Analytics',  icon: BarChart2 },
  { id: 'history',   label: 'History',    icon: Clock },
];

export default function Sidebar({ active, onNav, onIngest, ingesting }) {
  return (
    <aside style={styles.sidebar}>
      {/* Film-strip top decoration */}
      <div style={styles.filmStrip}>
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} style={styles.filmHole} />
        ))}
      </div>

      {/* Logo */}
      <div style={styles.logo}>
        <Film size={22} color="var(--gold)" />
        <div>
          <div style={styles.logoTitle}>CineVerse</div>
          <div style={styles.logoSub}>Analytics</div>
        </div>
      </div>

      <div style={styles.divider} />

      {/* Nav */}
      <nav style={styles.nav}>
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNav(id)}
            style={{
              ...styles.navBtn,
              ...(active === id ? styles.navBtnActive : {}),
            }}
          >
            <Icon size={16} />
            <span>{label}</span>
            {active === id && <div style={styles.navIndicator} />}
          </button>
        ))}
      </nav>

      <div style={{ flex: 1 }} />

      {/* Ingest button */}
      <button
        onClick={onIngest}
        disabled={ingesting}
        style={styles.ingestBtn}
        title="Reload all data sources"
      >
        <RefreshCw size={14} style={ingesting ? styles.spinning : {}} />
        <span>{ingesting ? 'Reloading...' : 'Reload Data'}</span>
      </button>

      {/* Film-strip bottom */}
      <div style={styles.filmStrip}>
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} style={styles.filmHole} />
        ))}
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: 200,
    minWidth: 200,
    background: 'var(--bg-surface)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  filmStrip: {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 3,
    padding: '6px 8px',
    background: '#0a0a0c',
  },
  filmHole: {
    width: 10, height: 8,
    borderRadius: 2,
    background: 'var(--bg-elevated)',
    border: '1px solid #2a2a30',
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '18px 16px 14px',
  },
  logoTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: 18, fontWeight: 700,
    color: 'var(--gold)', lineHeight: 1,
  },
  logoSub: {
    fontSize: 9, letterSpacing: '0.15em',
    textTransform: 'uppercase',
    color: 'var(--text-muted)',
  },
  divider: {
    height: 1, background: 'var(--border)', margin: '0 16px',
  },
  nav: {
    display: 'flex', flexDirection: 'column',
    gap: 2, padding: '12px 8px',
  },
  navBtn: {
    position: 'relative',
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '9px 12px',
    background: 'none', border: 'none',
    borderRadius: 'var(--radius)',
    color: 'var(--text-secondary)',
    cursor: 'pointer', fontSize: 13,
    fontFamily: 'var(--font-body)',
    transition: 'all 0.15s',
    textAlign: 'left', width: '100%',
  },
  navBtnActive: {
    background: 'var(--gold-glow)',
    color: 'var(--gold)',
    borderLeft: '2px solid var(--gold)',
  },
  navIndicator: {
    position: 'absolute', right: 8,
    width: 5, height: 5,
    borderRadius: '50%',
    background: 'var(--gold)',
  },
  ingestBtn: {
    display: 'flex', alignItems: 'center',
    justifyContent: 'center', gap: 8,
    margin: '8px 12px 12px',
    padding: '8px',
    background: 'none',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    color: 'var(--text-muted)',
    cursor: 'pointer', fontSize: 12,
    fontFamily: 'var(--font-body)',
    transition: 'all 0.2s',
  },
  spinning: {
    animation: 'spin 1s linear infinite',
  },
};