import React, { useEffect, useState } from 'react';
import { Shield, ShieldAlert, FileText, CheckCircle2, Cpu, ArrowRight, Activity } from 'lucide-react';
import type { OverviewMetrics } from '../types';

interface OverviewViewProps {
  onNavigate: (view: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/overview')
      .then(r => r.json())
      .then(d => {
        setMetrics(d);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load overview:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading system posture...</div>;
  }

  const isLocal = metrics?.ibm_z_posture.execution_mode === 'LOCAL_EMULATION';

  return (
    <div>
      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div>
            <div className="metric-title">Audit Log Entries</div>
            <div className="metric-val">{metrics?.total_audit_events ?? 0}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--status-pass)', marginTop: '0.2rem', fontFamily: 'var(--font-mono)' }}>
              SHA-256 chained
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'var(--status-pass-bg)', color: 'var(--status-pass)' }}>
            <FileText size={18} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Blocked Injections</div>
            <div className="metric-val" style={{ color: 'var(--status-fail)' }}>{metrics?.blocked_security_events ?? 0}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Policy perimeter stops
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'var(--status-fail-bg)', color: 'var(--status-fail)' }}>
            <ShieldAlert size={18} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Pending Approvals</div>
            <div className="metric-val" style={{ color: 'var(--status-warn)' }}>{metrics?.pending_human_approvals ?? 0}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Restricted data actions
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'var(--status-warn-bg)', color: 'var(--status-warn)' }}>
            <Activity size={18} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Active Rules</div>
            <div className="metric-val">{metrics?.active_policies_count ?? 4}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              RBAC and sensitivity gates
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'var(--accent-dim)', color: '#60a5fa' }}>
            <Shield size={18} />
          </div>
        </div>
      </div>

      {/* Main Grid: Architecture Status & Core Guardrails */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* IBM Z Platform Adapter */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Cpu size={16} color="#a855f7" />
                IBM Z Adapter Posture
              </div>
              <div className="card-desc">Hardware security status and deployment target</div>
            </div>
            <span className={`badge ${isLocal ? 'badge-purple' : 'badge-success'}`}>
              {metrics?.ibm_z_posture.execution_mode}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 600 }}>Host Platform</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.15rem' }}>
                {metrics?.ibm_z_posture.architecture} ({metrics?.ibm_z_posture.operating_system})
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {metrics?.ibm_z_posture.notes}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.65rem' }}>
              <div style={{ background: 'var(--bg-input)', padding: '0.65rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>CPACF Crypto</div>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: isLocal ? '#c4b5fd' : '#34d399', marginTop: '0.15rem' }}>
                  {metrics?.ibm_z_posture.cpacf_hardware_crypto.status}
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '0.65rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>Secure Execution</div>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: isLocal ? '#c4b5fd' : '#34d399', marginTop: '0.15rem' }}>
                  {metrics?.ibm_z_posture.secure_execution_enclave.status}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
              <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('settings')}>
                Deployment Details <ArrowRight size={13} />
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => onNavigate('evaluation')}>
                Run Benchmark Suite <ArrowRight size={13} />
              </button>
            </div>
          </div>
        </div>

        {/* Security Guardrails */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Shield size={16} color="#3b82f6" />
                Active Security Guardrails
              </div>
              <div className="card-desc">Deterministic enforcement independent of language model output</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={15} color="#10b981" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
              <div>
                <strong style={{ color: 'var(--text-main)' }}>Presidio Ingress Redaction:</strong> Sensitive identifiers (SSNs, card numbers, RACF IDs, emails) are scrubbed before prompt data reaches any reasoning adapter.
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={15} color="#10b981" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
              <div>
                <strong style={{ color: 'var(--text-main)' }}>Fail-Closed Policy Engine:</strong> Authorizations are evaluated in Python code outside the model. Requests with high threat scores or missing permissions fail immediately.
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={15} color="#10b981" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
              <div>
                <strong style={{ color: 'var(--text-main)' }}>Cryptographic Audit Ledger:</strong> Every decision and tool call is appended to an unbroken SHA-256 hash chain with live integrity validation.
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={15} color="#10b981" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
              <div>
                <strong style={{ color: 'var(--text-main)' }}>Restricted Action Gating:</strong> Operations on restricted records cannot execute directly. They require an explicit approval ticket from a security administrator.
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Activity Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Activity size={16} color="#38bdf8" />
              Recent Gateway Activity
            </div>
            <div className="card-desc">Live decisions recorded in the local cryptographic ledger</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('audit')}>
            View Full Audit Log <ArrowRight size={13} />
          </button>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Time</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Risk</th>
                <th>Policy Outcome</th>
                <th>Chained Hash</th>
              </tr>
            </thead>
            <tbody>
              {metrics?.recent_activity.map(row => (
                <tr key={row.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{row.request_id}</td>
                  <td style={{ fontSize: '0.74rem' }}>{new Date(row.timestamp).toLocaleTimeString()}</td>
                  <td>{row.actor}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{row.action}</td>
                  <td>
                    <span className={`badge ${row.risk_level === 'CRITICAL' || row.risk_level === 'HIGH' ? 'badge-danger' : (row.risk_level === 'MEDIUM' ? 'badge-warning' : 'badge-info')}`}>
                      {row.risk_level}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${row.policy_outcome === 'ALLOWED' ? 'badge-success' : (row.policy_outcome === 'PENDING_APPROVAL' ? 'badge-warning' : 'badge-danger')}`}>
                      {row.policy_outcome}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    {row.entry_hash}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
