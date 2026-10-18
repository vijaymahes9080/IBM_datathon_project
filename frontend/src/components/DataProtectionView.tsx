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
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(380px, 1.2fr) minmax(300px, 1fr)', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* Left Column: Interactive Scanner */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <ShieldCheck size={16} color="#10b981" />
                Data Redaction & PII Scanner
              </div>
              <div className="card-desc">Scan and mask identifiers with Presidio and regex recognizers</div>
            </div>
            {result && (
              <span className={`badge ${result.classification === 'RESTRICTED' ? 'badge-danger' : (result.classification === 'CONFIDENTIAL' ? 'badge-warning' : 'badge-info')}`}>
                {result.classification}
              </span>
            )}
          </div>

          <div style={{ marginBottom: '0.85rem' }}>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.3rem', textTransform: 'uppercase' }}>
              Text with Potential Identifiers
            </label>
            <textarea
              className="form-textarea"
              rows={6}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Paste raw text containing SSNs, card numbers, phones, emails, or RACF IDs..."
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setInputText('')}
            >
              Clear
            </button>
            <button
              className="btn btn-primary"
              onClick={handleScan}
              disabled={loading || !inputText.trim()}
            >
              <Search size={14} />
              {loading ? 'Scanning...' : 'Scan & Redact'}
            </button>
          </div>

          {result && (
            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <span style={{ fontSize: '0.7rem', color: '#34d399', fontWeight: 600, textTransform: 'uppercase' }}>
                    Redacted Output:
                  </span>
                  <button
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '0.7rem', padding: '0.15rem 0.45rem' }}
                    onClick={() => copyToClipboard(result.redacted_text)}
                  >
                    <Copy size={11} /> {copied ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div className="code-block" style={{ color: '#6ee7b7', whiteSpace: 'pre-wrap' }}>
                  {result.redacted_text}
                </div>
              </div>

              <div style={{ background: 'var(--bg-input)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>Active Engine</div>
                <div style={{ fontSize: '0.8rem', color: '#93c5fd', fontWeight: 500, marginTop: '0.1rem' }}>{result.engine_used}</div>
              </div>

              {/* Honest Limitations Note */}
              <div style={{ background: 'var(--status-warn-bg)', padding: '0.65rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--status-warn-border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#fbbf24', fontSize: '0.75rem', fontWeight: 600 }}>
                  <AlertCircle size={13} /> Limitations Notice
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem', lineHeight: 1.45 }}>
                  {result.limitations_note}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Taxonomy & Counts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <FileLock size={16} color="#00b4d8" />
                Detected Identifiers
              </div>
            </div>

            {result && Object.keys(result.entity_counts).length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                {Object.entries(result.entity_counts).map(([type, count]) => (
                  <div key={type} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.45rem 0.65rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#60a5fa' }}>{type}</span>
                    <span className="badge badge-warning">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', padding: '0.85rem', textAlign: 'center' }}>
                {result ? 'No sensitive identifiers found.' : 'Run a scan to view detected entities.'}
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">Sensitivity Levels</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.76rem' }}>
              <div style={{ padding: '0.45rem 0.65rem', background: 'var(--status-fail-bg)', border: '1px solid var(--status-fail-border)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#f87171' }}>RESTRICTED:</strong> API keys, credentials, high-value vault assets. Requires admin privilege and human sign-off.
              </div>
              <div style={{ padding: '0.45rem 0.65rem', background: 'var(--status-warn-bg)', border: '1px solid var(--status-warn-border)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#fbbf24' }}>CONFIDENTIAL:</strong> SSNs, credit cards, bank accounts, RACF IDs, MRNs. Requires analyst or admin clearance.
              </div>
              <div style={{ padding: '0.45rem 0.65rem', background: 'rgba(37, 99, 235, 0.08)', border: '1px solid rgba(37, 99, 235, 0.2)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#93c5fd' }}>INTERNAL:</strong> Work emails, business phone numbers, non-sensitive internal records.
              </div>
              <div style={{ padding: '0.45rem 0.65rem', background: 'var(--status-pass-bg)', border: '1px solid var(--status-pass-border)', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ color: '#34d399' }}>PUBLIC:</strong> Math expressions, public documentation, general information.
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
