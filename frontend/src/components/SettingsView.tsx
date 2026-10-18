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
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading system configuration...</div>;
  }

  const isLocal = posture?.execution_mode === 'LOCAL_EMULATION';

  return (
    <div>
      {/* IBM Z Hardware Architecture Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <Cpu size={18} color="#8b5cf6" />
              IBM Z / LinuxONE Platform Integration Architecture
            </div>
            <div className="card-desc">
              Hardware-assisted security adapters, confidential computing isolation, and enterprise identity federation
            </div>
          </div>
          <span className={`badge ${isLocal ? 'badge-purple' : 'badge-success'}`}>
            {posture?.execution_mode}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginTop: '0.5rem' }}>
          
          <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <Key size={16} color="#00b4d8" />
              <strong style={{ fontSize: '0.85rem' }}>CPACF Hardware Crypto</strong>
            </div>
            <div style={{ fontSize: '0.8rem', color: isLocal ? '#c4b5fd' : '#34d399', fontWeight: 600 }}>
              Status: {posture?.cpacf_hardware_crypto.status}
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.4 }}>
              Provider: {posture?.cpacf_hardware_crypto.provider}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Acceleration: {posture?.cpacf_hardware_crypto.acceleration}
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <Lock size={16} color="#8b5cf6" />
              <strong style={{ fontSize: '0.85rem' }}>Secure Execution Enclave</strong>
            </div>
            <div style={{ fontSize: '0.8rem', color: isLocal ? '#c4b5fd' : '#34d399', fontWeight: 600 }}>
              Status: {posture?.secure_execution_enclave.status}
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.4 }}>
              Tech: {posture?.secure_execution_enclave.technology}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Memory Encryption: {posture?.secure_execution_enclave.memory_encryption ? 'Hardware Active' : 'Software Emulated'}
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <Server size={16} color="#10b981" />
              <strong style={{ fontSize: '0.85rem' }}>Enterprise RACF Identity</strong>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>
              Status: {posture?.enterprise_identity_mapper.status}
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.4 }}>
              Provider: {posture?.enterprise_identity_mapper.provider}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Mode: {posture?.enterprise_identity_mapper.passthrough_mode}
            </div>
          </div>

        </div>

        {/* Local vs Production Transparency Notice */}
        <div style={{ marginTop: '1rem', padding: '0.85rem', background: 'rgba(139, 92, 246, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(139, 92, 246, 0.25)', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          <strong style={{ color: '#c4b5fd' }}>Deployment Reality Distinction:</strong> When running on non-s390x hardware (x86_64 / ARM development laptops), SecureAgent AI transparently activates its local emulation adapter. Cryptographic operations and confidential computing primitives are fully functional via software emulation. Production deployment to an IBM z15/z16 or LinuxONE host automatically engages native CPACF hardware instructions (KM/KMC/KLMD) and Ultravisor guest memory protection.
        </div>
      </div>

      {/* Synthetic Enterprise Records Explorer */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <Database size={18} color="#0f62fe" />
              Synthetic Enterprise Database (Access Gated by Active Role: {currentRole.toUpperCase()})
            </div>
            <div className="card-desc">
              Demonstrates row and field-level security boundaries applied before data leaves database layer:
            </div>
          </div>
          <span className="badge badge-info">{records.length} Synthetic Records</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Customer Name</th>
                <th>Account #</th>
                <th>Classification</th>
                <th>SSN Masked</th>
                <th>Balance</th>
                <th>Department</th>
                <th>Internal Notes</th>
              </tr>
            </thead>
            <tbody>
              {records.map(rec => (
                <tr key={rec.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#60a5fa' }}>{rec.id}</td>
                  <td style={{ fontWeight: 600 }}>{rec.customer_name}</td>
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
                  <td style={{ fontSize: '0.78rem', color: rec.notes.includes('HIDDEN') ? '#f87171' : 'var(--text-secondary)' }}>
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
