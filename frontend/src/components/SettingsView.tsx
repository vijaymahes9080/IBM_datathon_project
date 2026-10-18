import React, { useEffect, useState } from 'react';
import { Cpu, Database, Key, Server, Lock } from 'lucide-react';
import type { IBMZPosture } from '../types';

interface SettingsViewProps {
  currentRole: string;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ currentRole }) => {
  const [posture, setPosture] = useState<IBMZPosture | null>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/platform/ibm-z').then(r => r.json()),
      fetch(`/api/records?role=${currentRole}`).then(r => r.json())
    ])
      .then(([pData, rData]) => {
        setPosture(pData);
        setRecords(rData);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [currentRole]);

  if (loading) {
    return <div style={{ padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading platform configuration...</div>;
  }

  const isLocal = posture?.execution_mode === 'LOCAL_EMULATION';

  return (
    <div>
      {/* IBM Z Architecture Card */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <Cpu size={16} color="#a855f7" />
              IBM Z / LinuxONE Platform Posture
            </div>
            <div className="card-desc">
              Hardware cryptography adapters, confidential computing isolation, and enterprise identity
            </div>
          </div>
          <span className={`badge ${isLocal ? 'badge-purple' : 'badge-success'}`}>
            {posture?.execution_mode}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.85rem', marginTop: '0.4rem' }}>
          
          <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.35rem' }}>
              <Key size={15} color="#00b4d8" />
              <strong style={{ fontSize: '0.82rem' }}>CPACF Crypto</strong>
            </div>
            <div style={{ fontSize: '0.78rem', color: isLocal ? '#c4b5fd' : '#34d399', fontWeight: 600 }}>
              Status: {posture?.cpacf_hardware_crypto.status}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', lineHeight: 1.4 }}>
              Provider: {posture?.cpacf_hardware_crypto.provider}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Acceleration: {posture?.cpacf_hardware_crypto.acceleration}
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.35rem' }}>
              <Lock size={15} color="#a855f7" />
              <strong style={{ fontSize: '0.82rem' }}>Secure Execution Enclave</strong>
            </div>
            <div style={{ fontSize: '0.78rem', color: isLocal ? '#c4b5fd' : '#34d399', fontWeight: 600 }}>
              Status: {posture?.secure_execution_enclave.status}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', lineHeight: 1.4 }}>
              Tech: {posture?.secure_execution_enclave.technology}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Memory Encryption: {posture?.secure_execution_enclave.memory_encryption ? 'Hardware Active' : 'Software Emulated'}
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.35rem' }}>
              <Server size={15} color="#10b981" />
              <strong style={{ fontSize: '0.82rem' }}>Enterprise RACF Identity</strong>
            </div>
            <div style={{ fontSize: '0.78rem', color: '#34d399', fontWeight: 600 }}>
              Status: {posture?.enterprise_identity_mapper.status}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', lineHeight: 1.4 }}>
              Provider: {posture?.enterprise_identity_mapper.provider}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Mode: {posture?.enterprise_identity_mapper.passthrough_mode}
            </div>
          </div>

        </div>

        {/* Local vs Production Notice */}
        <div style={{ marginTop: '0.85rem', padding: '0.75rem', background: 'var(--status-ibm-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-ibm-border)', fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          <strong style={{ color: '#d8b4fe' }}>Environment distinction:</strong> On development workstations (x86_64 or ARM), SecureAgent AI runs with software emulation for cryptographic instructions and process sandboxing. On an s390x mainframe (z15, z16, or LinuxONE), the adapter engages native CPACF instructions (`KM`, `KMC`, `KLMD`) and Ultravisor guest memory encryption.
        </div>
      </div>

      {/* Synthetic Enterprise Records */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Database size={16} color="#3b82f6" />
              Synthetic Records (Filtered for Role: {currentRole})
            </div>
            <div className="card-desc">
              Demonstrates row and field-level permissions applied at database query time:
            </div>
          </div>
          <span className="badge badge-info">{records.length} records</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Customer</th>
                <th>Account #</th>
                <th>Level</th>
                <th>SSN Masked</th>
                <th>Balance</th>
                <th>Dept</th>
                <th>Internal Notes</th>
              </tr>
            </thead>
            <tbody>
              {records.map(rec => (
                <tr key={rec.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500, color: '#60a5fa' }}>{rec.id}</td>
                  <td style={{ fontWeight: 500 }}>{rec.customer_name}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{rec.account_number}</td>
                  <td>
                    <span className={`badge ${rec.classification === 'RESTRICTED' ? 'badge-danger' : (rec.classification === 'CONFIDENTIAL' ? 'badge-warning' : 'badge-info')}`}>
                      {rec.classification}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{rec.ssn_masked}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>
                    ${Number(rec.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td>{rec.department}</td>
                  <td style={{ fontSize: '0.74rem', color: rec.notes.includes('HIDDEN') ? '#f87171' : 'var(--text-muted)' }}>
                    {rec.notes}
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
