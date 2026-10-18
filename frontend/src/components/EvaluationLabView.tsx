import React, { useState } from 'react';
import { FlaskConical, Play, CheckCircle2, XCircle, Clock, BarChart3, AlertCircle } from 'lucide-react';
import type { BenchmarkReport } from '../types';

export const EvaluationLabView: React.FC = () => {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [running, setRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRunBenchmarks = async () => {
    setRunning(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/evaluation/run', {
        method: 'POST'
      });
      if (!res.ok) {
        throw new Error(`Evaluation failed with HTTP ${res.status}`);
      }
      const data: BenchmarkReport = await res.json();
      setReport(data);
    } catch (err: any) {
      setErrorMsg(err.message || 'Benchmark execution error');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      {/* Benchmark Action Header */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header" style={{ marginBottom: '0.5rem' }}>
          <div>
            <div className="card-title">
              <FlaskConical size={16} color="#3b82f6" />
              Security Evaluation Suite
            </div>
            <div className="card-desc">
              Executes 16 standardized test cases across PII leakage, prompt injection, and role authorization.
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleRunBenchmarks}
            disabled={running}
          >
            <Play size={14} />
            {running ? 'Running 16 Scenarios...' : 'Run Benchmark Suite'}
          </button>
        </div>

        <div style={{ background: 'var(--bg-input)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          <strong style={{ color: 'var(--text-main)' }}>Live Execution:</strong> Results, latencies, and confusion matrix are derived directly from actual gateway processing during the run.
        </div>
      </div>

      {errorMsg && (
        <div style={{ marginBottom: '1.25rem', padding: '0.75rem', background: 'var(--status-fail-bg)', border: '1px solid var(--status-fail-border)', borderRadius: 'var(--radius-sm)', color: '#f87171', fontSize: '0.8rem' }}>
          {errorMsg}
        </div>
      )}

      {/* Metrics Row */}
      {report && (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <div>
                <div className="metric-title">Pass Rate</div>
                <div className="metric-val" style={{ color: report.pass_rate_pct >= 90 ? '#34d399' : '#fbbf24' }}>
                  {report.pass_rate_pct}%
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
                  {report.passed_tests} of {report.total_tests} passed
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'var(--status-pass-bg)', color: 'var(--status-pass)' }}>
                <CheckCircle2 size={18} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">F1 Score</div>
                <div className="metric-val" style={{ color: '#60a5fa' }}>
                  {report.metrics.f1_score}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
                  P: {report.metrics.precision} · R: {report.metrics.recall}
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'var(--accent-dim)', color: '#60a5fa' }}>
                <BarChart3 size={18} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">False Positives</div>
                <div className="metric-val" style={{ color: report.confusion_matrix.false_positive === 0 ? '#34d399' : '#f87171' }}>
                  {report.confusion_matrix.false_positive}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
                  Benign queries blocked
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'rgba(0, 180, 216, 0.1)', color: '#00b4d8' }}>
                <AlertCircle size={18} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">Average Latency</div>
                <div className="metric-val" style={{ color: '#c4b5fd' }}>
                  {report.mean_latency_ms} ms
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
                  Per request through gateway
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'var(--status-ibm-bg)', color: 'var(--status-ibm)' }}>
                <Clock size={18} />
              </div>
            </div>
          </div>

          {/* Matrix & Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) minmax(340px, 1.2fr)', gap: '1.25rem', marginBottom: '1.25rem' }}>
            
            <div className="card">
              <div className="card-header">
                <div className="card-title">Confusion Matrix</div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.65rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-pass-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>True Positives</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#34d399', marginTop: '0.15rem' }}>
                    {report.confusion_matrix.true_positive}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-fail-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>False Positives</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: report.confusion_matrix.false_positive === 0 ? '#34d399' : '#f87171', marginTop: '0.15rem' }}>
                    {report.confusion_matrix.false_positive}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-fail-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>False Negatives</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: report.confusion_matrix.false_negative === 0 ? '#34d399' : '#f87171', marginTop: '0.15rem' }}>
                    {report.confusion_matrix.false_negative}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-pass-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>True Negatives</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#34d399', marginTop: '0.15rem' }}>
                    {report.confusion_matrix.true_negative}
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">Performance by Category</div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(report.category_summary).map(([cat, data]) => {
                  const pct = Math.round((data.passed / data.total) * 100);
                  return (
                    <div key={cat} style={{ background: 'var(--bg-input)', padding: '0.55rem 0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)' }}>{cat}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{data.avg_latency_ms} ms</span>
                          <span className={`badge ${pct === 100 ? 'badge-success' : 'badge-warning'}`}>
                            {data.passed}/{data.total}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Test Table */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Scenario Run Log</div>
            </div>

            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Test ID</th>
                    <th>Scenario</th>
                    <th>Category</th>
                    <th>Outcome</th>
                    <th>Threat Score</th>
                    <th>Latency</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {report.results.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{t.id}</td>
                      <td style={{ fontWeight: 500 }}>{t.name}</td>
                      <td><span className="badge badge-purple">{t.category}</span></td>
                      <td>
                        <span className={`badge ${t.actual_outcome === 'ALLOWED' ? 'badge-success' : (t.actual_outcome === 'PENDING_APPROVAL' ? 'badge-warning' : 'badge-danger')}`}>
                          {t.actual_outcome}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{t.actual_threat_score}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{t.latency_ms} ms</td>
                      <td>
                        {t.passed ? (
                          <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.2rem', fontWeight: 600 }}>
                            <CheckCircle2 size={13} /> pass
                          </span>
                        ) : (
                          <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.2rem', fontWeight: 600 }}>
                            <XCircle size={13} /> fail
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {!report && !running && (
        <div className="card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.82rem' }}>
          Click "Run Benchmark Suite" above to execute all 16 scenarios live against the gateway.
        </div>
      )}
    </div>
  );
};
