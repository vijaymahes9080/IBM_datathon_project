import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings
from .database.db import init_db, get_connection
from .security.gateway import security_gateway, EnterprisePrincipal, PERSONA_STORE
from .security.redactor import redactor_service, RedactionResult
from .security.threat_detector import threat_detector, ThreatDetectionResult
from .security.policy_engine import policy_engine
from .agent.orchestrator import orchestrator, OrchestratorExecutionResult
from .audit.audit_service import audit_service, AuditRecord, AuditVerificationReport
from .evaluation.benchmarks import evaluation_lab, BenchmarkReport
from .adapters.ibm_z import ibm_z_adapter, IBMZAdapterStatus

# Initialize SQLite tables and seeds on launch
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Security-First Agentic AI with Outer Boundary Policy Enforcement, Presidio PII Masking, and IBM Z Architecture Adapter",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Strict CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    prompt: str = Field(..., max_length=10000, description="User instruction or data processing prompt")
    role: str = Field(default="analyst", description="Caller persona: viewer | analyst | admin")
    racf_id: Optional[str] = Field(default=None, description="Optional IBM RACF Identity")
    model_mode: str = Field(default="deterministic", description="deterministic | ollama | ibm_z_enclave")
    manual_approval_id: Optional[str] = Field(default=None, description="Pre-approved HITL token if applicable")

class ScanRequest(BaseModel):
    text: str = Field(..., max_length=50000, description="Raw text payload to analyze")

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVED or REJECTED")
    decided_by: str = Field(default="admin_secops", description="Administrator making decision")
    rejection_reason: Optional[str] = Field(default=None, description="Reason if rejected")

class PolicyToggleRequest(BaseModel):
    policy_id: str
    is_enabled: bool

# -----------------------------------------------------------------------------
# Health & Overview
# -----------------------------------------------------------------------------
@app.get("/api/health")
def get_health():
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "platform_mode": "IBM_Z_PRODUCTION" if ibm_z_adapter.is_s390x else "LOCAL_EMULATION"
    }

@app.get("/api/overview")
def get_overview_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM audit_log")
    total_audits = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE policy_outcome = 'DENIED'")
    blocked_threats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM approvals WHERE status = 'PENDING'")
    pending_approvals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM policies WHERE is_enabled = 1")
    active_policies = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 5")
    recent_audits = cursor.fetchall()
    conn.close()

    parsed_recent = []
    for r in recent_audits:
        parsed_recent.append({
            "id": r["id"],
            "request_id": r["request_id"],
            "timestamp": r["timestamp"],
            "actor": r["actor"],
            "action": r["action"],
            "risk_level": r["risk_level"],
            "policy_outcome": r["policy_outcome"],
            "entry_hash": r["entry_hash"][:16] + "..."
        })

    return {
        "total_audit_events": total_audits,
        "blocked_security_events": blocked_threats,
        "pending_human_approvals": pending_approvals,
        "active_policies_count": active_policies,
        "ibm_z_posture": ibm_z_adapter.get_platform_posture().model_dump(),
        "recent_activity": parsed_recent
    }

# -----------------------------------------------------------------------------
# Secure AI Workspace Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/agent/chat", response_model=OrchestratorExecutionResult)
async def chat_with_agent(req: ChatRequest):
    principal = security_gateway.authenticate_actor(req.role, req.racf_id)
    result = await orchestrator.execute_workflow(
        prompt=req.prompt,
        actor=principal.username,
        role=principal.role,
        model_mode=req.model_mode,
        manual_approval_id=req.manual_approval_id
    )
    return result

# -----------------------------------------------------------------------------
# Data Protection & Redaction Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/redact/scan", response_model=RedactionResult)
def scan_and_redact(req: ScanRequest):
    return redactor_service.redact(req.text)

# -----------------------------------------------------------------------------
# Threat Detection Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/threats/scan", response_model=ThreatDetectionResult)
def scan_threats(req: ScanRequest):
    return threat_detector.scan_input(req.text)

# -----------------------------------------------------------------------------
# Policy Management Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/policies")
def list_policies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies ORDER BY policy_id ASC")
    rows = cursor.fetchall()
    conn.close()

    policies = []
    for r in rows:
        policies.append({
            "policy_id": r["policy_id"],
            "name": r["name"],
            "description": r["description"],
            "rule_type": r["rule_type"],
            "config": json.loads(r["config_json"]),
            "is_enabled": bool(r["is_enabled"]),
            "updated_at": r["updated_at"]
        })
    return policies

@app.post("/api/policies/toggle")
def toggle_policy(req: PolicyToggleRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE policies SET is_enabled = ?, updated_at = ? WHERE policy_id = ?",
        (1 if req.is_enabled else 0, datetime.now(timezone.utc).isoformat(), req.policy_id)
    )
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "policy_id": req.policy_id, "is_enabled": req.is_enabled}

# -----------------------------------------------------------------------------
# Human-In-The-Loop Approval Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/approvals")
def get_approvals(status_filter: Optional[str] = Query(None)):
    conn = get_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM approvals WHERE status = ? ORDER BY created_at DESC", (status_filter.upper(),))
    else:
        cursor.execute("SELECT * FROM approvals ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/approvals/{approval_id}/decide")
def decide_approval(approval_id: str, req: ApprovalDecisionRequest):
    dec = req.decision.upper().strip()
    if dec not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE approval_id = ?", (approval_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Approval ticket not found")

    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE approvals
        SET status = ?, decided_at = ?, decided_by = ?, rejection_reason = ?
        WHERE approval_id = ?
    """, (dec, now_iso, req.decided_by, req.rejection_reason, approval_id))
    conn.commit()
    conn.close()

    # Log approval audit event
    audit_service.log_event(
        request_id=row["request_id"],
        actor=req.decided_by,
        action=f"APPROVAL_{dec}",
        risk_level="MEDIUM",
        policy_outcome="ALLOWED" if dec == "APPROVED" else "DENIED",
        redaction_summary={},
        approval_status=dec,
        details={
            "approval_id": approval_id,
            "target_resource": row["target_resource"],
            "decision": dec,
            "rejection_reason": req.rejection_reason
        }
    )

    return {"status": "SUCCESS", "approval_id": approval_id, "decision": dec}

# -----------------------------------------------------------------------------
# Tamper-Evident Audit Trail Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/audit")
def get_audit_trail(limit: int = Query(50, le=200), actor: Optional[str] = None):
    return audit_service.get_recent_logs(limit=limit, actor=actor)

@app.get("/api/audit/verify", response_model=AuditVerificationReport)
def verify_audit_trail():
    return audit_service.verify_integrity()

# -----------------------------------------------------------------------------
# Evaluation Lab Benchmark Endpoints
# -----------------------------------------------------------------------------
@app.post("/api/evaluation/run", response_model=BenchmarkReport)
async def run_evaluation_benchmarks():
    return await evaluation_lab.run_benchmark_suite()

# -----------------------------------------------------------------------------
# IBM Z / LinuxONE Hardware Posture
# -----------------------------------------------------------------------------
@app.get("/api/platform/ibm-z", response_model=IBMZAdapterStatus)
def get_ibm_z_posture():
    return ibm_z_adapter.get_platform_posture()

# -----------------------------------------------------------------------------
# Synthetic Records Database Explorer (Role Gated)
# -----------------------------------------------------------------------------
@app.get("/api/records")
def list_synthetic_records(role: str = Query("analyst")):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM synthetic_records")
    rows = cursor.fetchall()
    conn.close()

    records = []
    for r in rows:
        data = dict(r)
        # Apply role-based data view filtering
        if role == "viewer":
            data["notes"] = "[CONFIDENTIAL NOTES HIDDEN FROM VIEWER]"
            data["balance"] = 0.0
            data["ssn_masked"] = "***-**-****"
        elif role == "analyst" and data["classification"] == "RESTRICTED":
            data["notes"] = "[RESTRICTED VAULT RECORD - REQUIRES ADMIN CLEARANCE]"
            data["balance"] = 0.0
        records.append(data)
    return records
