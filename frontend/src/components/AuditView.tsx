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
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading tamper-evident audit ledger...</div>;
  }

  const filteredLogs = logs.filter(l =>
    l.request_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.policy_outcome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      {/* Integrity Verification Header Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header" style={{ marginBottom: '0.65rem' }}>
          <div>
            <div className="card-title">
              <Lock size={18} color="#10b981" />
              Tamper-Evident SHA-256 Audit Trail
            </div>
            <div className="card-desc">
              Every gateway event is cryptographically linked to the previous entry hash: Hash_n = SHA256(Hash_n-1 || Details)
            </div>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleVerify}
            disabled={verifying}
          >
            <RefreshCw size={14} className={verifying ? 'spin' : ''} />
            {verifying ? 'Recomputing Hashes...' : 'Verify Cryptographic Integrity'}
          </button>
        </div>

        {report && (
          <div style={{
            background: report.is_valid ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
            border: `1px solid ${report.is_valid ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'}`,
            borderRadius: 'var(--radius-sm)',
            padding: '0.85rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              {report.is_valid ? (
                <CheckCircle2 size={20} color="#10b981" />
              ) : (
                <ShieldAlert size={20} color="#ef4444" />
              )}
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: report.is_valid ? '#34d399' : '#f87171' }}>
                  {report.is_valid ? 'Cryptographic Hash Chain Intact & Valid' : 'Ledger Tampering Detected!'}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  {report.verification_message}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span className="badge badge-info">{report.total_records} Verified Records</span>
              {report.latest_hash && (
                <span className="badge badge-purple" style={{ fontFamily: 'var(--font-mono)' }}>
                  Head: {report.latest_hash.substring(0, 12)}...
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', gap: '1rem' }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 400 }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 10, top: 11 }} />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: '2.2rem' }}
            placeholder="Search by Request ID, Actor, Action, or Outcome..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchLogs}>
          <RefreshCw size={14} /> Refresh Logs
        </button>
      </div>

      {/* Audit Log Table */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Request ID</th>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Risk</th>
                <th>Outcome</th>
                <th>Chained Hash (SHA-256)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map(log => (
                <tr key={log.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>#{log.id}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#60a5fa' }}>{log.request_id}</td>
                  <td style={{ fontSize: '0.78rem' }}>{new Date(log.timestamp).toLocaleTimeString()}</td>
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
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.74rem', color: '#c4b5fd' }}>
                    {log.entry_hash.substring(0, 16)}...
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem' }}
                      onClick={() => setSelectedRecord(log)}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Audit Record Detail Drawer */}
      {selectedRecord && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 500,
          background: 'var(--bg-card)',
          borderLeft: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-md)',
          padding: '1.5rem',
          zIndex: 50,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              Audit Record #{selectedRecord.id}
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setSelectedRecord(null)}>
              Close
            </button>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>REQUEST IDENTIFIER</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#60a5fa' }}>{selectedRecord.request_id}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>TIMESTAMP</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>{selectedRecord.timestamp}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>POLICY DECISION</div>
            <span className={`badge ${selectedRecord.policy_outcome === 'ALLOWED' ? 'badge-success' : 'badge-danger'}`}>
              {selectedRecord.policy_outcome} (Risk: {selectedRecord.risk_level})
            </span>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>SANITIZED DETAILS (NO RAW SECRETS)</div>
            <div className="code-block" style={{ maxHeight: 220, overflowY: 'auto' }}>
              {JSON.stringify(selectedRecord.details, null, 2)}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>PREVIOUS HASH DIGEST</div>
            <div className="code-block" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', wordBreak: 'break-all' }}>
              {selectedRecord.previous_hash}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>ENTRY HASH DIGEST (SHA-256)</div>
            <div className="code-block" style={{ fontSize: '0.72rem', color: '#c4b5fd', wordBreak: 'break-all' }}>
              {selectedRecord.entry_hash}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
