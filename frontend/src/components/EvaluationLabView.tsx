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
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header" style={{ marginBottom: '0.65rem' }}>
          <div>
            <div className="card-title">
              <FlaskConical size={18} color="#0f62fe" />
              Empirical Evaluation Lab & Benchmark Runner
            </div>
            <div className="card-desc">
              Execute standardized adversarial and compliance scenarios live to measure true accuracy, latency, and false positive rates.
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleRunBenchmarks}
            disabled={running}
          >
            <Play size={16} />
            {running ? 'Executing 16 Scenarios Live...' : 'Run Full Benchmark Suite'}
          </button>
        </div>

        <div style={{ background: 'var(--bg-input)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Scientific Assurance:</strong> All displayed counts, confusion matrices, and latency numbers are computed dynamically from actual execution through the full gateway and policy pipeline. Zero hardcoded results.
        </div>
      </div>

      {errorMsg && (
        <div style={{ marginBottom: '1.5rem', padding: '0.85rem', background: 'var(--status-danger-bg)', border: '1px solid var(--status-danger)', borderRadius: 'var(--radius-sm)', color: '#f87171', fontSize: '0.85rem' }}>
          {errorMsg}
        </div>
      )}

      {/* Metrics Row (Derived from Live Run) */}
      {report && (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <div>
                <div className="metric-title">Test Pass Rate</div>
                <div className="metric-val" style={{ color: report.pass_rate_pct >= 90 ? '#34d399' : '#fbbf24' }}>
                  {report.pass_rate_pct}%
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                  {report.passed_tests} of {report.total_tests} passed
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#10b981' }}>
                <CheckCircle2 size={20} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">Accuracy & F1-Score</div>
                <div className="metric-val" style={{ color: '#60a5fa' }}>
                  {(report.metrics.f1_score * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                  Prec: {report.metrics.precision} | Rec: {report.metrics.recall}
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'rgba(15, 98, 254, 0.15)', color: '#60a5fa' }}>
                <BarChart3 size={20} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">False Positive Count</div>
                <div className="metric-val" style={{ color: report.confusion_matrix.false_positive === 0 ? '#34d399' : '#f87171' }}>
                  {report.confusion_matrix.false_positive}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                  Legitimate queries preserved
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'rgba(0, 180, 216, 0.12)', color: '#00b4d8' }}>
                <AlertCircle size={20} />
              </div>
            </div>

            <div className="metric-card">
              <div>
                <div className="metric-title">Mean Execution Latency</div>
                <div className="metric-val" style={{ color: '#c4b5fd' }}>
                  {report.mean_latency_ms} ms
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                  Per-request gateway transit
                </div>
              </div>
              <div className="metric-icon-wrap" style={{ background: 'rgba(139, 92, 246, 0.12)', color: '#8b5cf6' }}>
                <Clock size={20} />
              </div>
            </div>
          </div>

          {/* Confusion Matrix & Category Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(360px, 1.2fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
            
            {/* Confusion Matrix */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">Confusion Matrix (Empirical Gate Data)</div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TRUE POSITIVES (Blocked)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#34d399', marginTop: '0.25rem' }}>
                    {report.confusion_matrix.true_positive}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FALSE POSITIVES (Over-blocked)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: report.confusion_matrix.false_positive === 0 ? '#34d399' : '#f87171', marginTop: '0.25rem' }}>
                    {report.confusion_matrix.false_positive}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>FALSE NEGATIVES (Missed)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: report.confusion_matrix.false_negative === 0 ? '#34d399' : '#f87171', marginTop: '0.25rem' }}>
                    {report.confusion_matrix.false_negative}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TRUE NEGATIVES (Allowed)</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#34d399', marginTop: '0.25rem' }}>
                    {report.confusion_matrix.true_negative}
                  </div>
                </div>
              </div>
            </div>

            {/* Category Summary */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">Category Performance Breakdown</div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {Object.entries(report.category_summary).map(([cat, data]) => {
                  const pct = Math.round((data.passed / data.total) * 100);
                  return (
                    <div key={cat} style={{ background: 'var(--bg-input)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{cat}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{data.avg_latency_ms} ms</span>
                          <span className={`badge ${pct === 100 ? 'badge-success' : 'badge-warning'}`}>
                            {data.passed}/{data.total} ({pct}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Test-by-Test Results Table */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Detailed Scenario Results</div>
            </div>

            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Test ID</th>
                    <th>Scenario Name</th>
                    <th>Category</th>
                    <th>Policy Outcome</th>
                    <th>Threat Score</th>
                    <th>Latency</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {report.results.map(t => (
                    <tr key={t.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{t.id}</td>
                      <td style={{ fontWeight: 600 }}>{t.name}</td>
                      <td><span className="badge badge-purple">{t.category}</span></td>
                      <td>
                        <span className={`badge ${t.actual_outcome === 'ALLOWED' ? 'badge-success' : (t.actual_outcome === 'PENDING_APPROVAL' ? 'badge-warning' : 'badge-danger')}`}>
                          {t.actual_outcome}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{t.actual_threat_score}</td>
                      <td>{t.latency_ms} ms</td>
                      <td>
                        {t.passed ? (
                          <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 600 }}>
                            <CheckCircle2 size={14} /> PASS
                          </span>
                        ) : (
                          <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: 600 }}>
                            <XCircle size={14} /> FAIL
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
        <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Click "Run Full Benchmark Suite" above to initiate live automated evaluation of all 16 scenarios.
        </div>
      )}
    </div>
  );
};
