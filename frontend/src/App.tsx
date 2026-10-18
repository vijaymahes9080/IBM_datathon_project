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
  UserCheck
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

  const navItems = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={18} /> },
    { id: 'workspace', label: 'Secure AI Workspace', icon: <Shield size={18} /> },
    { id: 'data_protection', label: 'Data Protection & PII', icon: <ShieldCheck size={18} /> },
    { id: 'threat_detection', label: 'Threat Defense Engine', icon: <ShieldAlert size={18} /> },
    { id: 'policy', label: 'Policy & Approvals', icon: <Sliders size={18} /> },
    { id: 'traces', label: 'Agent Activity & Traces', icon: <Activity size={18} /> },
    { id: 'audit', label: 'Tamper-Evident Audit', icon: <FileText size={18} /> },
    { id: 'evaluation', label: 'Evaluation Lab', icon: <FlaskConical size={18} /> },
    { id: 'settings', label: 'IBM Z Deployment', icon: <Settings size={18} /> },
  ];

  const getPersonaName = (role: string) => {
    switch (role) {
      case 'viewer': return 'viewer_guest (Public Read-Only)';
      case 'admin': return 'admin_secops (Full Security Officer)';
      case 'analyst':
      default: return 'analyst_alice (Standard Risk Operations)';
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
            <Cpu size={22} />
          </div>
          <div>
            <div className="brand-title">SecureAgent AI</div>
            <div className="brand-sub">IBM Z Datathon 2026</div>
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
            <Cpu size={14} />
            <span>IBM Z / LinuxONE Adapter</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Zero Trust AI Perimeter v1.0.0
          </div>
        </div>
      </aside>

      {/* Main Execution Wrapper */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title-area">
            <h1 className="view-heading">{getHeading()}</h1>
          </div>

          <div className="header-actions">
            {/* Live Role Switcher */}
            <div className="role-selector-wrap">
              <UserCheck size={16} color="#60a5fa" />
              <span className="role-label">Persona:</span>
              <select
                className="role-select"
                value={currentRole}
                onChange={e => setCurrentRole(e.target.value)}
                title="Switch active persona to test server-side RBAC and authorization barriers"
              >
                <option value="viewer">Viewer (Least Privilege)</option>
                <option value="analyst">Analyst (Internal Operations)</option>
                <option value="admin">Administrator (Security Officer)</option>
              </select>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: '0.25rem' }}>
                ({getPersonaName(currentRole)})
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
              <span>Gateway Online</span>
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
    </div>
  );
}

export default App;
