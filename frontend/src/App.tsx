import { useState } from 'react';
import {
  LayoutDashboard,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Sliders,
  Activity,
  FileText,
  FlaskConical,
  Settings,
  Cpu,
  UserCheck,
  Play,
  X
} from 'lucide-react';

import { OverviewView } from './components/OverviewView';
import { WorkspaceView } from './components/WorkspaceView';
import { DataProtectionView } from './components/DataProtectionView';
import { ThreatDetectionView } from './components/ThreatDetectionView';
import { PolicyView } from './components/PolicyView';
import { AgentTraceView } from './components/AgentTraceView';
import { AuditView } from './components/AuditView';
import { EvaluationLabView } from './components/EvaluationLabView';
import { SettingsView } from './components/SettingsView';

export function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentRole, setCurrentRole] = useState('analyst');
  const [showVideoModal, setShowVideoModal] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={16} /> },
    { id: 'workspace', label: 'AI Workspace', icon: <Shield size={16} /> },
    { id: 'data_protection', label: 'Data Protection', icon: <ShieldCheck size={16} /> },
    { id: 'threat_detection', label: 'Threat Detection', icon: <ShieldAlert size={16} /> },
    { id: 'policy', label: 'Policy Management', icon: <Sliders size={16} /> },
    { id: 'traces', label: 'Pipeline Traces', icon: <Activity size={16} /> },
    { id: 'audit', label: 'Audit Log', icon: <FileText size={16} /> },
    { id: 'evaluation', label: 'Evaluation Suite', icon: <FlaskConical size={16} /> },
    { id: 'settings', label: 'Platform & IBM Z', icon: <Settings size={16} /> },
  ];

  const getPersonaName = (role: string) => {
    switch (role) {
      case 'viewer': return 'viewer_guest (Read-Only)';
      case 'admin': return 'admin_secops (Full Admin)';
      case 'analyst':
      default: return 'analyst_alice (Operations)';
    }
  };

  const getHeading = () => {
    const item = navItems.find(i => i.id === activeTab);
    return item ? item.label : 'Overview';
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-section">
          <div className="brand-logo">
            <Cpu size={18} />
          </div>
          <div>
            <div className="brand-title">SecureAgent AI</div>
            <div className="brand-sub">IBM Z Security Gateway</div>
          </div>
        </div>

        <nav className="nav-list">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="platform-badge">
            <span>Adapter:</span>
            <span style={{ color: '#93c5fd' }}>s390x / Local</span>
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
            v1.0.0
          </div>
        </div>
      </aside>

      {/* Main Execution Shell */}
      <div className="main-wrapper">
        <header className="top-header">
          <div className="header-title-area">
            <h1 className="view-heading">{getHeading()}</h1>
          </div>

          <div className="header-actions">
            {/* Watch Demo Video Button */}
            <button
              className="btn btn-primary btn-sm"
              style={{
                background: 'linear-gradient(135deg, #0284c7, #2563eb)',
                borderColor: '#38bdf8',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontWeight: 600
              }}
              onClick={() => setShowVideoModal(true)}
              title="Watch full 1080p demonstration video (160s)"
            >
              <Play size={13} fill="currentColor" />
              <span>Watch Demo (160s)</span>
            </button>

            {/* Persona Switcher */}
            <div className="role-selector-wrap">
              <UserCheck size={14} color="#60a5fa" />
              <span className="role-label">Role:</span>
              <select
                className="role-select"
                value={currentRole}
                onChange={e => setCurrentRole(e.target.value)}
                title="Switch role to test server-side authorization"
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {getPersonaName(currentRole)}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
              <span>Gateway active</span>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {activeTab === 'overview' && <OverviewView onNavigate={setActiveTab} />}
          {activeTab === 'workspace' && <WorkspaceView currentRole={currentRole} onNavigate={setActiveTab} />}
          {activeTab === 'data_protection' && <DataProtectionView />}
          {activeTab === 'threat_detection' && <ThreatDetectionView />}
          {activeTab === 'policy' && <PolicyView />}
          {activeTab === 'traces' && <AgentTraceView />}
          {activeTab === 'audit' && <AuditView />}
          {activeTab === 'evaluation' && <EvaluationLabView />}
          {activeTab === 'settings' && <SettingsView currentRole={currentRole} />}
        </main>
      </div>

      {/* Video Modal Player */}
      {showVideoModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(8px)',
            zIndex: 99999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem'
          }}
          onClick={() => setShowVideoModal(false)}
        >
          <div
            style={{
              background: '#0b1118',
              border: '1px solid #1e293b',
              borderRadius: '12px',
              maxWidth: '1100px',
              width: '100%',
              overflow: 'hidden',
              boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '0.85rem 1.25rem',
                borderBottom: '1px solid #1e293b',
                background: '#090e15'
              }}
            >
              <div>
                <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>
                  SecureAgent AI — Product Demonstration
                </strong>
                <span style={{ color: '#94a3b8', fontSize: '0.75rem', marginLeft: '0.65rem' }}>
                  IBM Z Datathon 2026 • 160s • 1080p Full HD
                </span>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowVideoModal(false)}
                style={{ padding: '0.3rem 0.5rem' }}
              >
                <X size={15} /> Close
              </button>
            </div>

            <div style={{ position: 'relative', width: '100%', paddingTop: '56.25%', background: '#000' }}>
              <video
                controls
                autoPlay
                playsInline
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%'
                }}
              >
                <source src="/secureagent_ai_demo.mp4" type="video/mp4" />
                <source src="./secureagent_ai_demo.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

