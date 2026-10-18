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
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading security operations posture...</div>;
  }

  const isLocal = metrics?.ibm_z_posture.execution_mode === 'LOCAL_EMULATION';

  return (
    <div>
      {/* Top Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div>
            <div className="metric-title">Audit Ledger Entries</div>
            <div className="metric-val">{metrics?.total_audit_events ?? 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--status-success)', marginTop: '0.25rem' }}>
              SHA-256 Hash Chained
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#10b981' }}>
            <FileText size={20} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Blocked Adversarial Events</div>
            <div className="metric-val" style={{ color: '#f87171' }}>{metrics?.blocked_security_events ?? 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Outer Gateway Defense
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'rgba(239, 68, 68, 0.12)', color: '#ef4444' }}>
            <ShieldAlert size={20} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Pending Human Approvals</div>
            <div className="metric-val" style={{ color: '#fbbf24' }}>{metrics?.pending_human_approvals ?? 0}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              HITL High-Risk Gating
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b' }}>
            <Activity size={20} />
          </div>
        </div>

        <div className="metric-card">
          <div>
            <div className="metric-title">Active Security Policies</div>
            <div className="metric-val">{metrics?.active_policies_count ?? 4}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
              Deterministic Outside-LLM
            </div>
          </div>
          <div className="metric-icon-wrap" style={{ background: 'rgba(15, 98, 254, 0.15)', color: '#60a5fa' }}>
            <Shield size={20} />
          </div>
        </div>
      </div>

      {/* Main Grid: Architecture Status & Recent Audit Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Platform Adapter Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Cpu size={18} color="#8b5cf6" />
                IBM Z & LinuxONE Architecture Adapter
              </div>
              <div className="card-desc">Hardware security integration & confidential computing readiness</div>
            </div>
            <span className={`badge ${isLocal ? 'badge-purple' : 'badge-success'}`}>
              {metrics?.ibm_z_posture.execution_mode}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginTop: '0.5rem' }}>
            <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Host Architecture</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.2rem' }}>
                {metrics?.ibm_z_posture.architecture} ({metrics?.ibm_z_posture.operating_system})
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                {metrics?.ibm_z_posture.notes}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CPACF Crypto Acceleration</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: isLocal ? '#c4b5fd' : '#34d399', marginTop: '0.2rem' }}>
                  {metrics?.ibm_z_posture.cpacf_hardware_crypto.status}
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Secure Execution Enclave</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: isLocal ? '#c4b5fd' : '#34d399', marginTop: '0.2rem' }}>
                  {metrics?.ibm_z_posture.secure_execution_enclave.status}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
              <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('settings')}>
                Inspect Hardware Config <ArrowRight size={14} />
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => onNavigate('evaluation')}>
                Run Evaluation Suite <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>

        {/* Security Core Value Proposition */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Shield size={18} color="#0f62fe" />
                Deterministic Outer Security Perimeter
              </div>
              <div className="card-desc">Zero Trust AI Architecture — Never Trust LLM Output as Authorization</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="#10b981" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Presidio PII Redaction Before Model Dispatch</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>All identifiers (SSN, cards, keys, RACF IDs) are masked before leaving outer gateway perimeter.</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="#10b981" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Fail-Closed Policy Enforcement</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Policy decisions are evaluated in deterministic Python outside the model; high threat scores halt execution immediately.</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="#10b981" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Cryptographic SHA-256 Chained Audit Trail</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Every decision, prompt classification, and tool invocation is recorded into a mathematically verifiable tamper-evident hash chain.</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="#10b981" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Mandatory Human-In-The-Loop Approval</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Restricted exports and high-risk actions are suspended until authorized by an administrator.</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Recent Activity Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Activity size={18} color="#00b4d8" />
              Recent Gateway Activity Feed
            </div>
            <div className="card-desc">Real-time decisions logged to hash-chained tamper-evident store</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('audit')}>
            View Full Audit Trail <ArrowRight size={14} />
          </button>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Risk Level</th>
                <th>Policy Outcome</th>
                <th>Hash Digest</th>
              </tr>
            </thead>
            <tbody>
              {metrics?.recent_activity.map(row => (
                <tr key={row.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{row.request_id}</td>
                  <td style={{ fontSize: '0.78rem' }}>{new Date(row.timestamp).toLocaleTimeString()}</td>
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
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
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
