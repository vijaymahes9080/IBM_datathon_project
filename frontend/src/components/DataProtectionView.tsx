import React, { useState } from 'react';
import { ShieldCheck, Search, AlertCircle, FileLock, Copy } from 'lucide-react';
import type { RedactionResult } from '../types';

export const DataProtectionView: React.FC = () => {
  const [inputText, setInputText] = useState(
    'Employee Alice Vance (RACF-ADM02) processed account ACCT-984210 with SSN 000-12-3456 and credit card 4532-1234-5678-9012. Direct queries to security.auditor@enterprise.ibm.internal or call (555) 234-5678. Debug key: sk-live98410294820194820192.'
  );
  const [result, setResult] = useState<RedactionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleScan = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/redact/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      });
      const data: RedactionResult = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (txt: string) => {
    navigator.clipboard.writeText(txt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 1.2fr) minmax(320px, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Left Column: Interactive Scanner */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <ShieldCheck size={18} color="#10b981" />
                Interactive Sensitive Identifier Redactor
              </div>
              <div className="card-desc">Scan and anonymize PII using Microsoft Presidio and enterprise recognizers</div>
            </div>
            {result && (
              <span className={`badge ${result.classification === 'RESTRICTED' ? 'badge-danger' : (result.classification === 'CONFIDENTIAL' ? 'badge-warning' : 'badge-info')}`}>
                {result.classification}
              </span>
            )}
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '0.35rem' }}>
              RAW TEXT WITH SENSITIVE DATA
            </label>
            <textarea
              className="form-textarea"
              rows={6}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Paste raw text containing SSNs, cards, phones, emails, or IBM RACF credentials..."
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setInputText('')}
            >
              Clear Text
            </button>
            <button
              className="btn btn-primary"
              onClick={handleScan}
              disabled={loading || !inputText.trim()}
            >
              <Search size={16} />
              {loading ? 'Analyzing Entities...' : 'Run Presidio Redaction Scan'}
            </button>
          </div>

          {result && (
            <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: 600, textTransform: 'uppercase' }}>
                    Sanitized Text Output (Ready for Model Consumption):
                  </span>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem' }}
                    onClick={() => copyToClipboard(result.redacted_text)}
                  >
                    <Copy size={12} /> {copied ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div className="code-block" style={{ color: '#6ee7b7', whiteSpace: 'pre-wrap' }}>
                  {result.redacted_text}
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>ACTIVE REDACTION ENGINE</div>
                <div style={{ fontSize: '0.85rem', color: '#60a5fa', fontWeight: 600, marginTop: '0.15rem' }}>{result.engine_used}</div>
              </div>

              {/* Required Limitations Note */}
              <div style={{ background: 'rgba(245, 158, 11, 0.08)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#fbbf24', fontSize: '0.78rem', fontWeight: 600 }}>
                  <AlertCircle size={14} /> Explicit Detection Limitations
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.5 }}>
                  {result.limitations_note}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Taxonomy & Detected Entities */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          {/* Detected Entities Breakdown */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <FileLock size={18} color="#00b4d8" />
                Detected Sensitive Entities
              </div>
            </div>

            {result && Object.keys(result.entity_counts).length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(result.entity_counts).map(([type, count]) => (
                  <div key={type} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#60a5fa' }}>{type}</span>
                    <span className="badge badge-warning">{count} Found</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', padding: '1rem', textAlign: 'center' }}>
                {result ? 'No sensitive identifiers found in sample.' : 'Execute a scan to view entity counts.'}
              </div>
            )}
          </div>

          {/* Classification Taxonomy Reference */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Data Sensitivity Taxonomy</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
              <div style={{ padding: '0.5rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#f87171' }}>RESTRICTED:</strong> API Keys, private keys, high-value vault assets. Requires admin privilege and mandatory human sign-off.
              </div>
              <div style={{ padding: '0.5rem', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#fbbf24' }}>CONFIDENTIAL:</strong> SSN, credit cards, bank accounts, RACF IDs, medical record numbers. Gated to analyst/admin with strict masking.
              </div>
              <div style={{ padding: '0.5rem', background: 'rgba(15, 98, 254, 0.08)', border: '1px solid rgba(15, 98, 254, 0.25)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#60a5fa' }}>INTERNAL:</strong> Corporate email addresses, business phone numbers, non-sensitive internal telemetry.
              </div>
              <div style={{ padding: '0.5rem', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#34d399' }}>PUBLIC:</strong> General domain knowledge, public documentation, math metrics.
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
