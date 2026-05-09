import { useEffect, useState } from 'react';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { getAnalytics } from '../api';

const GOLD    = '#c9a84c';
const DIM     = '#5a5650';
const COLORS  = ['#c9a84c','#5f9fd4','#4caf82','#d45f5f','#9b7fe0','#d48c5f'];

const fmt = (n) => n >= 1e7
  ? `₹${(n/1e7).toFixed(1)}Cr`
  : n >= 1e5
    ? `₹${(n/1e5).toFixed(0)}L`
    : n;

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={ttStyles.box}>
      <div style={ttStyles.label}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={ttStyles.row}>
          <span style={{ color: p.color }}>{p.name}</span>
          <span style={ttStyles.val}>
            {typeof p.value === 'number' && p.value > 1e5 ? fmt(p.value) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const ttStyles = {
  box: {
    background: '#1e1e24', border: '1px solid rgba(201,168,76,0.3)',
    borderRadius: 6, padding: '10px 14px', fontSize: 11,
    fontFamily: 'var(--font-mono)',
  },
  label: { color: '#f0ece0', marginBottom: 6, fontWeight: 500 },
  row: { display: 'flex', justifyContent: 'space-between', gap: 16 },
  val: { color: '#c9a84c' },
};

function Card({ title, subtitle, children, span = 1 }) {
  return (
    <div style={{ ...styles.card, gridColumn: `span ${span}` }}>
      <div style={styles.cardHeader}>
        <div style={styles.cardTitle}>{title}</div>
        {subtitle && <div style={styles.cardSub}>{subtitle}</div>}
      </div>
      {children}
    </div>
  );
}

export default function ChartView() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={styles.state}>Loading analytics...</div>;
  if (error)   return <div style={{ ...styles.state, color: 'var(--accent-red)' }}>
    Error: {error}
  </div>;

  const topMovies     = data.top_movies     || [];
  const genreSummary  = data.genre_summary  || [];
  const cityEngagement = data.city_engagement || [];
  const releases2025  = data.releases_2025  || [];

  return (
    <div style={styles.page}>
      <div style={styles.pageHeader}>
        <div style={styles.pageTitle}>Analytics Dashboard</div>
        <div style={styles.pageSub}>Live data from CineVerse database</div>
      </div>

      <div style={styles.grid}>

        {/* Top movies by revenue */}
        <Card title="Top Titles by Revenue" subtitle="All time" span={2}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topMovies} margin={{ left: 10, right: 10 }}>
              <XAxis
                dataKey="title"
                tick={{ fill: DIM, fontSize: 10, fontFamily: 'var(--font-mono)' }}
                tickFormatter={t => t.length > 14 ? t.slice(0,13)+'…' : t}
              />
              <YAxis
                tick={{ fill: DIM, fontSize: 9, fontFamily: 'var(--font-mono)' }}
                tickFormatter={fmt}
                width={60}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="revenue_inr" name="Revenue" radius={[3,3,0,0]}>
                {topMovies.map((_, i) => (
                  <Cell key={i} fill={i === 0 ? GOLD : '#2e2e38'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Genre completion rates */}
        <Card title="Genre Health" subtitle="Avg completion %">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={genreSummary}
              layout="vertical"
              margin={{ left: 10, right: 20 }}
            >
              <XAxis
                type="number" domain={[0, 100]}
                tick={{ fill: DIM, fontSize: 9, fontFamily: 'var(--font-mono)' }}
              />
              <YAxis
                type="category" dataKey="genre" width={60}
                tick={{ fill: DIM, fontSize: 10, fontFamily: 'var(--font-mono)' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="avg_completion_pct" name="Completion %" radius={[0,3,3,0]}>
                {genreSummary.map((d, i) => (
                  <Cell
                    key={i}
                    fill={d.avg_completion_pct >= 80 ? '#4caf82'
                      : d.avg_completion_pct >= 65 ? GOLD
                      : '#d45f5f'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* City engagement */}
        <Card title="City Engagement Scores" subtitle="Peak scores by city">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={cityEngagement} margin={{ left: 0, right: 10 }}>
              <XAxis
                dataKey="city"
                tick={{ fill: DIM, fontSize: 10, fontFamily: 'var(--font-mono)' }}
              />
              <YAxis
                domain={[0, 10]}
                tick={{ fill: DIM, fontSize: 9, fontFamily: 'var(--font-mono)' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="peak_engagement" name="Engagement" radius={[3,3,0,0]}>
                {cityEngagement.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* 2025 releases table */}
        <Card title="2025 Releases" subtitle="Performance at a glance" span={2}>
          <div style={styles.table}>
            <div style={styles.thead}>
              {['Title','Genre','Revenue','Rating','Completion','ROI'].map(h => (
                <div key={h} style={styles.th}>{h}</div>
              ))}
            </div>
            {releases2025.map((r, i) => (
              <div key={i} style={{
                ...styles.trow,
                ...(i % 2 === 0 ? { background: 'rgba(255,255,255,0.02)' } : {}),
              }}>
                <div style={styles.td}>{r.title}</div>
                <div style={styles.td}>
                  <span style={styles.genreTag}>{r.genre}</span>
                </div>
                <div style={{ ...styles.td, color: 'var(--gold)' }}>
                  {fmt(r.revenue_inr)}
                </div>
                <div style={styles.td}>{r.rating}</div>
                <div style={{
                  ...styles.td,
                  color: r.avg_completion_pct >= 80
                    ? 'var(--accent-green)' : 'var(--accent-red)',
                }}>
                  {r.avg_completion_pct ? `${r.avg_completion_pct}%` : '—'}
                </div>
                <div style={{
                  ...styles.td,
                  color: r.roi >= 1 ? 'var(--accent-green)' : 'var(--accent-red)',
                }}>
                  {r.roi != null ? `${r.roi}x` : '—'}
                </div>
              </div>
            ))}
          </div>
        </Card>

      </div>
    </div>
  );
}

const styles = {
  page: {
    flex: 1, overflowY: 'auto',
    padding: '24px',
    background: 'var(--bg-base)',
  },
  pageHeader: { marginBottom: 24 },
  pageTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: 26, fontWeight: 600,
    color: 'var(--text-primary)',
  },
  pageSub: { fontSize: 12, color: 'var(--text-muted)', marginTop: 4 },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 16,
  },
  card: {
    background: 'var(--bg-surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '16px',
    overflow: 'hidden',
  },
  cardHeader: { marginBottom: 14 },
  cardTitle: {
    fontFamily: 'var(--font-display)',
    fontSize: 16, fontWeight: 600,
    color: 'var(--text-primary)',
  },
  cardSub: { fontSize: 11, color: 'var(--text-muted)', marginTop: 2 },
  state: {
    flex: 1, display: 'flex',
    alignItems: 'center', justifyContent: 'center',
    color: 'var(--text-muted)', fontFamily: 'var(--font-mono)',
    fontSize: 13,
  },
  table: { fontSize: 12, fontFamily: 'var(--font-mono)' },
  thead: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 1fr 0.7fr 1fr 0.7fr',
    padding: '6px 10px',
    borderBottom: '1px solid var(--border)',
    marginBottom: 4,
  },
  th: {
    fontSize: 9, textTransform: 'uppercase',
    letterSpacing: '0.08em', color: 'var(--text-muted)',
  },
  trow: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 1fr 0.7fr 1fr 0.7fr',
    padding: '7px 10px',
    borderRadius: 4,
  },
  td: { color: 'var(--text-secondary)', fontSize: 11 },
  genreTag: {
    fontSize: 9, padding: '2px 6px',
    background: 'var(--bg-elevated)',
    borderRadius: 3, color: 'var(--text-muted)',
    border: '1px solid var(--border)',
  },
};