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
      setActionMsg(`Policy ${policy_id} status updated.`);
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
        setActionMsg(`Ticket ${approval_id} has been marked as ${decision}.`);
        fetchData();
        setTimeout(() => setActionMsg(null), 4000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading enterprise policy engine...</div>;
  }

  const pendingApprovals = approvals.filter(a => a.status === 'PENDING');
  const pastApprovals = approvals.filter(a => a.status !== 'PENDING');

  return (
    <div>
      {actionMsg && (
        <div style={{ marginBottom: '1.25rem', padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--status-success)', borderRadius: 'var(--radius-sm)', color: '#34d399', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle2 size={16} /> {actionMsg}
        </div>
      )}

      {/* Human Approval Queue Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <AlertTriangle size={18} color="#f59e0b" />
              Human-In-The-Loop High-Risk Approval Queue
            </div>
            <div className="card-desc">Restricted actions suspended pending authorized administrator review</div>
          </div>
          <span className={`badge ${pendingApprovals.length > 0 ? 'badge-warning' : 'badge-success'}`}>
            {pendingApprovals.length} Pending
          </span>
        </div>

        {pendingApprovals.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {pendingApprovals.map(appr => (
              <div key={appr.approval_id} style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(245, 158, 11, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#fbbf24' }}>{appr.approval_id}</span>
                    <span className="badge badge-danger">Risk Score: {appr.risk_score}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Actor: {appr.actor}</span>
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
                    Action: {appr.action} (Target: {appr.target_resource})
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    Preview: "{appr.payload_preview}"
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ borderColor: 'var(--status-danger)', color: '#f87171' }}
                    onClick={() => handleDecideApproval(appr.approval_id, 'REJECTED')}
                  >
                    <X size={14} /> Reject
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    style={{ background: '#10b981' }}
                    onClick={() => handleDecideApproval(appr.approval_id, 'APPROVED')}
                  >
                    <Check size={14} /> Approve Execution
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No high-risk operations currently pending review. Trigger "Demo F" in the Secure AI Workspace to test this workflow.
          </div>
        )}

        {pastApprovals.length > 0 && (
          <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              Historical Decisions ({pastApprovals.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {pastApprovals.slice(0, 5).map(pa => (
                <div key={pa.approval_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', background: 'var(--bg-card)', padding: '0.4rem 0.6rem', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{pa.approval_id}</span>
                  <span>{pa.action}</span>
                  <span className={`badge ${pa.status === 'APPROVED' ? 'badge-success' : 'badge-danger'}`}>{pa.status}</span>
                  <span style={{ color: 'var(--text-muted)' }}>{pa.decided_by || 'Admin'}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Role-Based Access Control Matrix */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <Shield size={18} color="#0f62fe" />
              Role-Based Access Control Matrix
            </div>
            <div className="card-desc">Explicit permissions enforcing least privilege across allowlisted tools</div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Persona / Role</th>
                <th>Clearance Level</th>
                <th>Allowed Tools</th>
                <th>Restricted Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong style={{ color: '#94a3b8' }}>viewer</strong></td>
                <td><span className="badge badge-info">PUBLIC</span></td>
                <td>calculate_secure_metric, analyze_text_statistics</td>
                <td><span style={{ color: '#f87171' }}>Blocked from synthetic records & restricted exports</span></td>
              </tr>
              <tr>
                <td><strong style={{ color: '#60a5fa' }}>analyst</strong></td>
                <td><span className="badge badge-warning">CONFIDENTIAL</span></td>
                <td>calculate_secure_metric, analyze_text_statistics, lookup_synthetic_record</td>
                <td><span style={{ color: '#fbbf24' }}>Field-masked PII; blocked from restricted vault exports</span></td>
              </tr>
              <tr>
                <td><strong style={{ color: '#c4b5fd' }}>admin</strong></td>
                <td><span className="badge badge-danger">RESTRICTED</span></td>
                <td>All allowlisted tools + export_restricted_records</td>
                <td><span style={{ color: '#34d399' }}>Permitted with audited Human-In-The-Loop approval</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Configurable Policy Rules */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Configured Security Policies</div>
            <div className="card-desc">Deterministic rules evaluated by the security gateway outside the model</div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Policy ID</th>
                <th>Rule Name & Description</th>
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
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{p.name}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{p.description}</div>
                  </td>
                  <td><span className="badge badge-purple">{p.rule_type}</span></td>
                  <td>
                    <div className="code-block" style={{ fontSize: '0.7rem', padding: '0.35rem 0.5rem', maxWidth: 320 }}>
                      {JSON.stringify(p.config)}
                    </div>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleTogglePolicy(p.policy_id, p.is_enabled)}
                      style={{ padding: '0.25rem 0.5rem' }}
                    >
                      {p.is_enabled ? (
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <ToggleRight size={18} /> Active
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <ToggleLeft size={18} /> Disabled
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
