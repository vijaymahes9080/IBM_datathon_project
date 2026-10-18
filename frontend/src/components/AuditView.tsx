import React, { useEffect, useState } from 'react';
import { CheckCircle2, ShieldAlert, RefreshCw, Search, Lock } from 'lucide-react';
import type { AuditRecord, AuditVerificationReport } from '../types';

export const AuditView: React.FC = () => {
  const [logs, setLogs] = useState<AuditRecord[]>([]);
  const [report, setReport] = useState<AuditVerificationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRecord, setSelectedRecord] = useState<AuditRecord | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/audit?limit=100');
      const data: AuditRecord[] = await res.json();
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const res = await fetch('/api/audit/verify');
      const data: AuditVerificationReport = await res.json();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    handleVerify();
  }, []);

  if (loading && logs.length === 0) {
    return <div style={{ padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading audit entries...</div>;
  }

  const filteredLogs = logs.filter(l =>
    l.request_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.policy_outcome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      {/* Verification Card */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header" style={{ marginBottom: '0.5rem' }}>
          <div>
            <div className="card-title">
              <Lock size={16} color="#10b981" />
              Audit Integrity Check
            </div>
            <div className="card-desc">
              Events are linked with SHA-256 hashes: Hash_n = SHA256(Hash_n-1 || Entry)
            </div>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleVerify}
            disabled={verifying}
          >
            <RefreshCw size={13} className={verifying ? 'spin' : ''} />
            {verifying ? 'Verifying...' : 'Verify Hash Chain'}
          </button>
        </div>

        {report && (
          <div style={{
            background: report.is_valid ? 'var(--status-pass-bg)' : 'var(--status-fail-bg)',
            border: `1px solid ${report.is_valid ? 'var(--status-pass-border)' : 'var(--status-fail-border)'}`,
            borderRadius: 'var(--radius-sm)',
            padding: '0.75rem 0.85rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.65rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
              {report.is_valid ? (
                <CheckCircle2 size={18} color="#10b981" />
              ) : (
                <ShieldAlert size={18} color="#ef4444" />
              )}
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: report.is_valid ? '#34d399' : '#f87171' }}>
                  {report.is_valid ? 'Hash chain verified' : 'Integrity check failed'}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                  {report.verification_message}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center' }}>
              <span className="badge badge-info">{report.total_records} records</span>
              {report.latest_hash && (
                <span className="badge badge-purple" style={{ fontFamily: 'var(--font-mono)' }}>
                  {report.latest_hash.substring(0, 12)}...
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem', gap: '0.85rem' }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 360 }}>
          <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: 10, top: 10 }} />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: '2rem', fontSize: '0.8rem' }}
            placeholder="Filter by Request ID, Actor, or Action..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchLogs}>
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Log Table */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Request ID</th>
                <th>Time</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Risk</th>
                <th>Outcome</th>
                <th>Hash</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map(log => (
                <tr key={log.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>#{log.id}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500, color: '#60a5fa' }}>{log.request_id}</td>
                  <td style={{ fontSize: '0.74rem' }}>{new Date(log.timestamp).toLocaleTimeString()}</td>
                  <td>{log.actor}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{log.action}</td>
                  <td>
                    <span className={`badge ${log.risk_level === 'CRITICAL' || log.risk_level === 'HIGH' ? 'badge-danger' : (log.risk_level === 'MEDIUM' ? 'badge-warning' : 'badge-info')}`}>
                      {log.risk_level}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${log.policy_outcome === 'ALLOWED' ? 'badge-success' : (log.policy_outcome === 'PENDING_APPROVAL' ? 'badge-warning' : 'badge-danger')}`}>
                      {log.policy_outcome}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: '#c4b5fd' }}>
                    {log.entry_hash.substring(0, 14)}...
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.7rem', padding: '0.15rem 0.45rem' }}
                      onClick={() => setSelectedRecord(log)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Detail Drawer */}
      {selectedRecord && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 460,
          background: 'var(--bg-card)',
          borderLeft: '1px solid var(--border-subtle)',
          boxShadow: '0 0 24px rgba(0,0,0,0.5)',
          padding: '1.25rem',
          zIndex: 50,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.85rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.65rem' }}>
            <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Audit Record #{selectedRecord.id}
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setSelectedRecord(null)}>
              Close
            </button>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Request ID</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#60a5fa' }}>{selectedRecord.request_id}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Timestamp</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>{selectedRecord.timestamp}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Policy Outcome</div>
            <span className={`badge ${selectedRecord.policy_outcome === 'ALLOWED' ? 'badge-success' : 'badge-danger'}`} style={{ marginTop: '0.2rem' }}>
              {selectedRecord.policy_outcome} (risk: {selectedRecord.risk_level})
            </span>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Sanitized Details</div>
            <div className="code-block" style={{ maxHeight: 200, overflowY: 'auto' }}>
              {JSON.stringify(selectedRecord.details, null, 2)}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Previous Hash</div>
            <div className="code-block" style={{ fontSize: '0.7rem', color: 'var(--text-dim)', wordBreak: 'break-all' }}>
              {selectedRecord.previous_hash}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Entry Hash (SHA-256)</div>
            <div className="code-block" style={{ fontSize: '0.7rem', color: '#c4b5fd', wordBreak: 'break-all' }}>
              {selectedRecord.entry_hash}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
