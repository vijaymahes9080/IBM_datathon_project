import React, { useEffect, useState } from 'react';
import { Shield, Check, X, AlertTriangle, ToggleLeft, ToggleRight, CheckCircle2 } from 'lucide-react';
import type { PolicyItem, ApprovalTicket } from '../types';

export const PolicyView: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [approvals, setApprovals] = useState<ApprovalTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [pRes, aRes] = await Promise.all([
        fetch('/api/policies'),
        fetch('/api/approvals')
      ]);
      const pData = await pRes.json();
      const aData = await aRes.json();
      setPolicies(pData);
      setApprovals(aData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTogglePolicy = async (policy_id: string, currentStatus: boolean) => {
    try {
      await fetch('/api/policies/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy_id, is_enabled: !currentStatus })
      });
      setPolicies(policies.map(p => p.policy_id === policy_id ? { ...p, is_enabled: !currentStatus } : p));
      setActionMsg(`Policy ${policy_id} updated.`);
      setTimeout(() => setActionMsg(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDecideApproval = async (approval_id: string, decision: 'APPROVED' | 'REJECTED') => {
    try {
      const res = await fetch(`/api/approvals/${approval_id}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          decided_by: 'admin_secops',
          rejection_reason: decision === 'REJECTED' ? 'Administrative security policy denial' : undefined
        })
      });
      if (res.ok) {
        setActionMsg(`Ticket ${approval_id} ${decision.toLowerCase()}.`);
        fetchData();
        setTimeout(() => setActionMsg(null), 3000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div style={{ padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading policies...</div>;
  }

  const pendingApprovals = approvals.filter(a => a.status === 'PENDING');
  const pastApprovals = approvals.filter(a => a.status !== 'PENDING');

  return (
    <div>
      {actionMsg && (
        <div style={{ marginBottom: '1rem', padding: '0.65rem 0.85rem', background: 'var(--status-pass-bg)', border: '1px solid var(--status-pass-border)', borderRadius: 'var(--radius-sm)', color: '#34d399', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <CheckCircle2 size={15} /> {actionMsg}
        </div>
      )}

      {/* Human Approval Queue */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <AlertTriangle size={16} color="#f59e0b" />
              Approval Queue (Human-In-The-Loop)
            </div>
            <div className="card-desc">Restricted actions suspended pending administrative review</div>
          </div>
          <span className={`badge ${pendingApprovals.length > 0 ? 'badge-warning' : 'badge-success'}`}>
            {pendingApprovals.length} pending
          </span>
        </div>

        {pendingApprovals.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {pendingApprovals.map(appr => (
              <div key={appr.approval_id} style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.85rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#fbbf24', fontSize: '0.82rem' }}>{appr.approval_id}</span>
                    <span className="badge badge-danger">Risk: {appr.risk_score}</span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Actor: {appr.actor}</span>
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.25rem' }}>
                    Action: {appr.action} (Target: {appr.target_resource})
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    "{appr.payload_preview}"
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.45rem' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ borderColor: 'var(--status-fail)', color: '#f87171' }}
                    onClick={() => handleDecideApproval(appr.approval_id, 'REJECTED')}
                  >
                    <X size={13} /> Reject
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ background: '#10b981', borderColor: '#059669' }}
                    onClick={() => handleDecideApproval(appr.approval_id, 'APPROVED')}
                  >
                    <Check size={13} /> Approve
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '1.25rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
            No high-risk operations currently pending review. Trigger "Restricted Export" in the workspace to test.
          </div>
        )}

        {pastApprovals.length > 0 && (
          <div style={{ marginTop: '0.85rem', paddingTop: '0.65rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.45rem' }}>
              Past Decisions ({pastApprovals.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              {pastApprovals.slice(0, 5).map(pa => (
                <div key={pa.approval_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.74rem', background: '#090e15', padding: '0.35rem 0.55rem', borderRadius: 'var(--radius-xs)' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{pa.approval_id}</span>
                  <span>{pa.action}</span>
                  <span className={`badge ${pa.status === 'APPROVED' ? 'badge-success' : 'badge-danger'}`}>{pa.status}</span>
                  <span style={{ color: 'var(--text-dim)' }}>{pa.decided_by || 'Admin'}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Role Matrix */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <Shield size={16} color="#3b82f6" />
              Role Access Matrix
            </div>
            <div className="card-desc">Allowed actions per role evaluated outside the model</div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Role</th>
                <th>Clearance</th>
                <th>Allowed Tools</th>
                <th>Restrictions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong style={{ color: 'var(--text-muted)' }}>viewer</strong></td>
                <td><span className="badge badge-info">PUBLIC</span></td>
                <td>calculate_secure_metric, analyze_text_statistics</td>
                <td><span style={{ color: '#f87171' }}>Synthetic records and exports blocked</span></td>
              </tr>
              <tr>
                <td><strong style={{ color: '#60a5fa' }}>analyst</strong></td>
                <td><span className="badge badge-warning">CONFIDENTIAL</span></td>
                <td>calculate_secure_metric, analyze_text_statistics, lookup_synthetic_record</td>
                <td><span style={{ color: '#fbbf24' }}>Field-masked PII; vault export blocked</span></td>
              </tr>
              <tr>
                <td><strong style={{ color: '#c4b5fd' }}>admin</strong></td>
                <td><span className="badge badge-danger">RESTRICTED</span></td>
                <td>All tools + export_restricted_records</td>
                <td><span style={{ color: '#34d399' }}>Restricted exports require approval ticket</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Policies */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Policy Rules</div>
            <div className="card-desc">Deterministic rules executed at the gateway</div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Policy ID</th>
                <th>Rule Name</th>
                <th>Type</th>
                <th>Parameters</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {policies.map(p => (
                <tr key={p.policy_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{p.policy_id}</td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{p.name}</div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>{p.description}</div>
                  </td>
                  <td><span className="badge badge-purple">{p.rule_type}</span></td>
                  <td>
                    <div className="code-block" style={{ fontSize: '0.68rem', padding: '0.3rem 0.45rem', maxWidth: 300 }}>
                      {JSON.stringify(p.config)}
                    </div>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleTogglePolicy(p.policy_id, p.is_enabled)}
                      style={{ padding: '0.2rem 0.45rem' }}
                    >
                      {p.is_enabled ? (
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <ToggleRight size={16} /> Active
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <ToggleLeft size={16} /> Disabled
                        </span>
                      )}
                    </button>
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
