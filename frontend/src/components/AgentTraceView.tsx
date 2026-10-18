import React, { useEffect, useState } from 'react';
import { Activity, Shield, Cpu, Lock, CheckCircle2, Layers } from 'lucide-react';
import type { AuditRecord } from '../types';

export const AgentTraceView: React.FC = () => {
  const [recentRuns, setRecentRuns] = useState<AuditRecord[]>([]);
  const [selectedRun, setSelectedRun] = useState<AuditRecord | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/audit?limit=15')
      .then(r => r.json())
      .then((data: AuditRecord[]) => {
        setRecentRuns(data);
        if (data.length > 0) {
          setSelectedRun(data[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading multi-agent execution pipeline...</div>;
  }

  const PIPELINE_STAGES = [
    {
      num: 1,
      name: 'Threat Defense Agent',
      desc: 'Inspects prompt for adversarial injections, instruction overrides, and command tampering',
      icon: <Shield size={16} color="#ef4444" />
    },
    {
      num: 2,
      name: 'Protected Data Processor',
      desc: 'Presidio PII recognition & data sensitivity classification (PUBLIC to RESTRICTED)',
      icon: <Lock size={16} color="#10b981" />
    },
    {
      num: 3,
      name: 'Task Planner Agent',
      desc: 'Decomposes request and proposes required safe allowlisted tool actions',
      icon: <Layers size={16} color="#00b4d8" />
    },
    {
      num: 4,
      name: 'Policy Evaluator Agent',
      desc: 'Deterministic outer security barrier enforcing RBAC and fail-closed rules',
      icon: <Shield size={16} color="#0f62fe" />
    },
    {
      num: 5,
      name: 'Authorized Tool Executor',
      desc: 'Server-side execution of allowlisted safe tools with argument validation',
      icon: <Cpu size={16} color="#8b5cf6" />
    },
    {
      num: 6,
      name: 'Model Reasoning Adapter',
      desc: 'Processes only redacted text through local offline engine or hardware enclave',
      icon: <CheckCircle2 size={16} color="#34d399" />
    }
  ];

  return (
    <div>
      {/* Visual Pipeline Stage Architecture */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header" style={{ marginBottom: '1rem' }}>
          <div>
            <div className="card-title">
              <Layers size={18} color="#0f62fe" />
              Secure Multi-Agent Pipeline Architecture
            </div>
            <div className="card-desc">Every request traverses discrete, bounded agent stages with explicit inputs, outputs, and permissions:</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
          {PIPELINE_STAGES.map((st) => (
            <div key={st.num} style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.85rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>STAGE 0{st.num}</span>
                  {st.icon}
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                  {st.name}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {st.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Trace Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(400px, 1.5fr)', gap: '1.5rem' }}>
        
        {/* Left: Request History List */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Recent Pipeline Executions</div>
            <span className="badge badge-info">{recentRuns.length} Runs</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: 520, overflowY: 'auto' }}>
            {recentRuns.map(run => {
              const isSelected = selectedRun?.id === run.id;
              return (
                <div
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  style={{
                    padding: '0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    background: isSelected ? 'rgba(15, 98, 254, 0.15)' : 'var(--bg-input)',
                    border: `1px solid ${isSelected ? 'rgba(15, 98, 254, 0.4)' : 'var(--border-subtle)'}`,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', fontWeight: 600, color: '#60a5fa' }}>
                      {run.request_id}
                    </span>
                    <span className={`badge ${run.policy_outcome === 'ALLOWED' ? 'badge-success' : (run.policy_outcome === 'PENDING_APPROVAL' ? 'badge-warning' : 'badge-danger')}`}>
                      {run.policy_outcome}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                    Action: {run.action}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.35rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    <span>Actor: {run.actor}</span>
                    <span>{new Date(run.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Selected Run Detail & Audited Snapshot */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Activity size={18} color="#10b981" />
              Audited Execution Record
            </div>
            {selectedRun && (
              <span className="badge badge-purple" style={{ fontFamily: 'var(--font-mono)' }}>
                Ledger ID #{selectedRun.id}
              </span>
            )}
          </div>

          {selectedRun ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>REQUEST IDENTIFIER</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#60a5fa', marginTop: '0.15rem' }}>{selectedRun.request_id}</div>
                </div>
                <div style={{ background: 'var(--bg-input)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>POLICY OUTCOME</div>
                  <div style={{ fontWeight: 600, color: selectedRun.policy_outcome === 'ALLOWED' ? '#34d399' : '#f87171', marginTop: '0.15rem' }}>
                    {selectedRun.policy_outcome} (Risk: {selectedRun.risk_level})
                  </div>
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                  Sanitized Execution Details:
                </div>
                <div className="code-block" style={{ maxHeight: 200, overflowY: 'auto' }}>
                  {JSON.stringify(selectedRun.details, null, 2)}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                  Redaction Entity Counts:
                </div>
                <div className="code-block" style={{ color: '#34d399' }}>
                  {JSON.stringify(selectedRun.redaction_summary, null, 2)}
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>TAMPER-EVIDENT SHA-256 HASH</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: '#c4b5fd', wordBreak: 'break-all', marginTop: '0.2rem' }}>
                  {selectedRun.entry_hash}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                  Chained from: <span style={{ fontFamily: 'var(--font-mono)' }}>{selectedRun.previous_hash.substring(0, 24)}...</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a run from the history to inspect its audited trace record.
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
