export interface DetectedEntity {
  entity_type: string;
  start: number;
  end: number;
  score: number;
  text_snippet: string;
}

export interface RedactionResult {
  original_text: string;
  redacted_text: string;
  detected_entities: DetectedEntity[];
  entity_counts: Record<string, number>;
  classification: 'PUBLIC' | 'INTERNAL' | 'CONFIDENTIAL' | 'RESTRICTED';
  redacted: boolean;
  engine_used: string;
  limitations_note: string;
}

export interface ThreatSignal {
  category: string;
  pattern_name: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  matched_text: string;
  weight: number;
}

export interface ThreatDetectionResult {
  input_text: string;
  threat_score: number;
  threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  is_safe: boolean;
  signals: ThreatSignal[];
  recommendation: string;
  defense_summary: string;
}

export interface AgentTraceStep {
  step_number: number;
  agent_name: string;
  action_description: string;
  status: 'SUCCESS' | 'BLOCKED' | 'PENDING' | 'SKIPPED';
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  duration_ms: number;
}

export interface ChatResponse {
  request_id: string;
  actor: string;
  role: string;
  original_input: string;
  redacted_input: string;
  classification: string;
  threat_level: string;
  threat_score: number;
  policy_outcome: 'ALLOWED' | 'DENIED' | 'PENDING_APPROVAL';
  final_output: string;
  approval_id?: string;
  tool_executed?: string;
  tool_output?: Record<string, any>;
  trace_steps: AgentTraceStep[];
  audit_hash: string;
  execution_latency_ms: number;
}

export interface AuditRecord {
  id: number;
  request_id: string;
  timestamp: string;
  actor: string;
  action: string;
  risk_level: string;
  policy_outcome: string;
  redaction_summary: Record<string, any>;
  approval_status: string;
  details: Record<string, any>;
  previous_hash: string;
  entry_hash: string;
}

export interface AuditVerificationReport {
  is_valid: boolean;
  total_records: number;
  latest_hash?: string;
  corrupted_record_id?: number;
  verification_message: string;
}

export interface PolicyItem {
  policy_id: string;
  name: string;
  description: string;
  rule_type: string;
  config: Record<string, any>;
  is_enabled: boolean;
  updated_at: string;
}

export interface ApprovalTicket {
  approval_id: string;
  request_id: string;
  action: string;
  actor: string;
  target_resource: string;
  risk_score: number;
  payload_preview: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  decided_at?: string;
  decided_by?: string;
  rejection_reason?: string;
}

export interface TestResult {
  id: string;
  category: string;
  name: string;
  passed: boolean;
  actual_outcome: string;
  actual_threat_score: number;
  actual_classification: string;
  redaction_occurred: boolean;
  latency_ms: number;
  notes: string;
}

export interface BenchmarkReport {
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  pass_rate_pct: number;
  mean_latency_ms: number;
  confusion_matrix: {
    true_positive: number;
    false_positive: number;
    true_negative: number;
    false_negative: number;
  };
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
  };
  category_summary: Record<string, { total: number; passed: number; avg_latency_ms: number }>;
  results: TestResult[];
}

export interface IBMZPosture {
  is_s390x: boolean;
  architecture: string;
  operating_system: string;
  execution_mode: 'PRODUCTION_IBM_Z' | 'LOCAL_EMULATION';
  cpacf_hardware_crypto: Record<string, any>;
  secure_execution_enclave: Record<string, any>;
  enterprise_identity_mapper: Record<string, any>;
  audit_telemetry_adapter: Record<string, any>;
  notes: string;
}

export interface OverviewMetrics {
  total_audit_events: number;
  blocked_security_events: number;
  pending_human_approvals: number;
  active_policies_count: number;
  ibm_z_posture: IBMZPosture;
  recent_activity: Array<{
    id: number;
    request_id: string;
    timestamp: string;
    actor: string;
    action: string;
    risk_level: string;
    policy_outcome: string;
    entry_hash: string;
  }>;
}
