import uuid
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..security.redactor import redactor_service, RedactionResult
from ..security.threat_detector import threat_detector, ThreatDetectionResult
from ..security.policy_engine import policy_engine, PolicyDecision
from ..tools.safe_tools import safe_tools, ToolExecutionResult
from .model_adapter import model_adapter, ModelResponse
from ..audit.audit_service import audit_service
from ..database.db import get_connection

class AgentTraceStep(BaseModel):
    step_number: int
    agent_name: str
    action_description: str
    status: str  # SUCCESS, BLOCKED, PENDING, SKIPPED
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float

class OrchestratorExecutionResult(BaseModel):
    request_id: str
    actor: str
    role: str
    original_input: str
    redacted_input: str
    classification: str
    threat_level: str
    threat_score: float
    policy_outcome: str  # ALLOWED, DENIED, PENDING_APPROVAL
    final_output: str
    approval_id: Optional[str] = None
    tool_executed: Optional[str] = None
    tool_output: Optional[Dict[str, Any]] = None
    trace_steps: List[AgentTraceStep]
    audit_hash: str
    execution_latency_ms: float

class AgentOrchestrator:
    def __init__(self):
        pass

    async def execute_workflow(
        self,
        prompt: str,
        actor: str = "analyst_user",
        role: str = "analyst",
        model_mode: str = "deterministic",
        manual_approval_id: Optional[str] = None
    ) -> OrchestratorExecutionResult:
        """
        Execute deterministic, security-first multi-agent pipeline:
        1. Threat Detection & Security Scan
        2. Protected Data Redaction & Classification
        3. Task Planner Agent
        4. Security & Policy Evaluator Agent (Outside LLM)
        5. Authorized Tool Executor
        6. Model Reasoning Adapter (Redacted Only)
        7. Audit Record Creation
        """
        start_time = time.time()
        request_id = f"REQ-{uuid.uuid4().hex[:10].upper()}"
        trace_steps: List[AgentTraceStep] = []

        # =========================================================================
        # STEP 1: Threat Defense & Adversarial Prompt Injection Detection
        # =========================================================================
        t0 = time.time()
        threat_res = threat_detector.scan_input(prompt)
        step1_duration = round((time.time() - t0) * 1000, 2)
        trace_steps.append(
            AgentTraceStep(
                step_number=1,
                agent_name="Threat Defense Agent",
                action_description="Scan input for prompt injections, jailbreaks, and command overrides",
                status="SUCCESS" if threat_res.is_safe else "BLOCKED",
                input_data={"raw_prompt_length": len(prompt)},
                output_data={
                    "threat_score": threat_res.threat_score,
                    "threat_level": threat_res.threat_level,
                    "signals_detected": [s.pattern_name for s in threat_res.signals],
                    "recommendation": threat_res.recommendation
                },
                duration_ms=step1_duration
            )
        )

        # =========================================================================
        # STEP 2: Protected Data Processor (Presidio + Custom Identifiers)
        # =========================================================================
        t0 = time.time()
        redaction_res = redactor_service.redact(prompt)
        step2_duration = round((time.time() - t0) * 1000, 2)
        trace_steps.append(
            AgentTraceStep(
                step_number=2,
                agent_name="Protected Data Processor Agent",
                action_description="Identify sensitive entities, classify sensitivity, and mask confidential data",
                status="SUCCESS",
                input_data={"text_length": len(prompt)},
                output_data={
                    "classification": redaction_res.classification,
                    "entity_counts": redaction_res.entity_counts,
                    "redacted_text_preview": redaction_res.redacted_text[:120],
                    "engine_used": redaction_res.engine_used
                },
                duration_ms=step2_duration
            )
        )

        # =========================================================================
        # STEP 3: Planner Agent (Intent Extraction & Tool Selection)
        # =========================================================================
        t0 = time.time()
        planned_action, tool_name, tool_args = self._plan_task(redaction_res.redacted_text, manual_approval_id)
        step3_duration = round((time.time() - t0) * 1000, 2)
        trace_steps.append(
            AgentTraceStep(
                step_number=3,
                agent_name="Task Planner Agent",
                action_description="Determine intent and identify required safe allowlisted tool",
                status="SUCCESS",
                input_data={"sanitized_prompt": redaction_res.redacted_text},
                output_data={
                    "planned_action": planned_action,
                    "tool_name": tool_name or "NONE",
                    "tool_args": tool_args
                },
                duration_ms=step3_duration
            )
        )

        # =========================================================================
        # STEP 4: Security & Policy Evaluator (Independent Outer Perimeter)
        # =========================================================================
        t0 = time.time()
        policy_decision = policy_engine.evaluate_action(
            actor_role=role,
            action=planned_action,
            target_sensitivity=redaction_res.classification,
            threat_score=threat_res.threat_score,
            is_threat_safe=threat_res.is_safe,
            tool_args=tool_args
        )
        step4_duration = round((time.time() - t0) * 1000, 2)
        trace_steps.append(
            AgentTraceStep(
                step_number=4,
                agent_name="Security & Policy Evaluator Agent",
                action_description="Enforce RBAC, sensitivity barriers, and risk threshold outside language model",
                status="SUCCESS" if policy_decision.outcome == "ALLOWED" else ("PENDING" if policy_decision.outcome == "PENDING_APPROVAL" else "BLOCKED"),
                input_data={
                    "actor_role": role,
                    "action": planned_action,
                    "target_sensitivity": redaction_res.classification,
                    "threat_score": threat_res.threat_score
                },
                output_data={
                    "outcome": policy_decision.outcome,
                    "reason": policy_decision.reason,
                    "matched_policy_id": policy_decision.matched_policy_id,
                    "risk_score": policy_decision.risk_score
                },
                duration_ms=step4_duration
            )
        )

        # =========================================================================
        # Handle Policy Rejection (Denied)
        # =========================================================================
        if policy_decision.outcome == "DENIED":
            final_output = f"SECURITY POLICY BLOCK: {policy_decision.reason}"
            total_duration = round((time.time() - start_time) * 1000, 2)
            audit_record = audit_service.log_event(
                request_id=request_id,
                actor=actor,
                action=planned_action,
                risk_level=threat_res.threat_level,
                policy_outcome="DENIED",
                redaction_summary=redaction_res.entity_counts,
                approval_status="NOT_REQUIRED",
                details={
                    "reason": policy_decision.reason,
                    "threat_score": threat_res.threat_score,
                    "policy_id": policy_decision.matched_policy_id
                }
            )
            return OrchestratorExecutionResult(
                request_id=request_id,
                actor=actor,
                role=role,
                original_input=prompt,
                redacted_input=redaction_res.redacted_text,
                classification=redaction_res.classification,
                threat_level=threat_res.threat_level,
                threat_score=threat_res.threat_score,
                policy_outcome="DENIED",
                final_output=final_output,
                approval_id=None,
                tool_executed=None,
                tool_output=None,
                trace_steps=trace_steps,
                audit_hash=audit_record.entry_hash,
                execution_latency_ms=total_duration
            )

        # =========================================================================
        # Handle High-Risk Gating (Human Approval Required)
        # =========================================================================
        if policy_decision.outcome == "PENDING_APPROVAL":
            approval_id = f"APPR-{uuid.uuid4().hex[:8].upper()}"
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO approvals (
                    approval_id, request_id, action, actor, target_resource,
                    risk_score, payload_preview, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                approval_id, request_id, planned_action, actor,
                tool_args.get("record_id", "RESTRICTED_DATASET"),
                policy_decision.risk_score,
                redaction_res.redacted_text[:200],
                "PENDING",
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            conn.close()

            final_output = (
                f"ACTION SUSPENDED PENDING HUMAN APPROVAL: Operation '{planned_action}' targets RESTRICTED resources. "
                f"Approval ticket {approval_id} registered. An enterprise security administrator must sign off before execution."
            )
            total_duration = round((time.time() - start_time) * 1000, 2)
            audit_record = audit_service.log_event(
                request_id=request_id,
                actor=actor,
                action=planned_action,
                risk_level="HIGH",
                policy_outcome="PENDING_APPROVAL",
                redaction_summary=redaction_res.entity_counts,
                approval_status="PENDING",
                details={
                    "approval_id": approval_id,
                    "target_resource": tool_args.get("record_id", "RESTRICTED_DATASET"),
                    "risk_score": policy_decision.risk_score
                }
            )
            return OrchestratorExecutionResult(
                request_id=request_id,
                actor=actor,
                role=role,
                original_input=prompt,
                redacted_input=redaction_res.redacted_text,
                classification=redaction_res.classification,
                threat_level=threat_res.threat_level,
                threat_score=threat_res.threat_score,
                policy_outcome="PENDING_APPROVAL",
                final_output=final_output,
                approval_id=approval_id,
                tool_executed=None,
                tool_output=None,
                trace_steps=trace_steps,
                audit_hash=audit_record.entry_hash,
                execution_latency_ms=total_duration
            )

        # =========================================================================
        # STEP 5: Authorized Tool Execution (Strict Allowlist)
        # =========================================================================
        tool_result = None
        if tool_name:
            t0 = time.time()
            if tool_name == "calculate_secure_metric":
                tool_result = safe_tools.calculate_secure_metric(tool_args.get("expression", "0"))
            elif tool_name == "analyze_text_statistics":
                tool_result = safe_tools.analyze_text_statistics(redaction_res.redacted_text)
            elif tool_name == "lookup_synthetic_record":
                tool_result = safe_tools.lookup_synthetic_record(tool_args.get("record_id", "REC-1001"), actor_role=role)
            elif tool_name == "export_restricted_records":
                tool_result = safe_tools.export_restricted_records(
                    record_id=tool_args.get("record_id", "REC-1003"),
                    approval_id=manual_approval_id or "",
                    actor_role=role
                )
            step5_duration = round((time.time() - t0) * 1000, 2)
            trace_steps.append(
                AgentTraceStep(
                    step_number=5,
                    agent_name="Authorized Execution Agent",
                    action_description=f"Execute server-side allowlisted tool '{tool_name}'",
                    status="SUCCESS" if tool_result and tool_result.status == "SUCCESS" else "BLOCKED",
                    input_data=tool_args,
                    output_data=tool_result.model_dump() if tool_result else {},
                    duration_ms=step5_duration
                )
            )

        # =========================================================================
        # STEP 6: Model Reasoning Adapter (Redacted Context Only)
        # =========================================================================
        t0 = time.time()
        model_res = await model_adapter.generate_response(
            redacted_prompt=redaction_res.redacted_text,
            mode=model_mode,
            tool_results=tool_result.model_dump() if tool_result else None
        )
        step6_duration = round((time.time() - t0) * 1000, 2)
        trace_steps.append(
            AgentTraceStep(
                step_number=6,
                agent_name="Model Adapter",
                action_description=f"Reason and generate sanitized response via {model_res.adapter_name}",
                status="SUCCESS",
                input_data={"redacted_input_sent": model_res.input_payload_sent},
                output_data={"generated_preview": model_res.generated_text[:120], "latency_ms": model_res.latency_ms},
                duration_ms=step6_duration
            )
        )

        total_duration = round((time.time() - start_time) * 1000, 2)

        # =========================================================================
        # STEP 7: Append Tamper-Evident Audit Record
        # =========================================================================
        audit_record = audit_service.log_event(
            request_id=request_id,
            actor=actor,
            action=planned_action,
            risk_level=threat_res.threat_level,
            policy_outcome="ALLOWED",
            redaction_summary=redaction_res.entity_counts,
            approval_status="APPROVED" if manual_approval_id else "NOT_REQUIRED",
            details={
                "tool_executed": tool_name,
                "tool_status": tool_result.status if tool_result else "NONE",
                "classification": redaction_res.classification,
                "model_adapter": model_res.adapter_name
            }
        )

        return OrchestratorExecutionResult(
            request_id=request_id,
            actor=actor,
            role=role,
            original_input=prompt,
            redacted_input=redaction_res.redacted_text,
            classification=redaction_res.classification,
            threat_level=threat_res.threat_level,
            threat_score=threat_res.threat_score,
            policy_outcome="ALLOWED",
            final_output=model_res.generated_text,
            approval_id=manual_approval_id,
            tool_executed=tool_name,
            tool_output=tool_result.model_dump() if tool_result else None,
            trace_steps=trace_steps,
            audit_hash=audit_record.entry_hash,
            execution_latency_ms=total_duration
        )

    def _plan_task(self, text: str, manual_approval_id: Optional[str] = None) -> tuple[str, Optional[str], Dict[str, Any]]:
        """Identify safe allowlisted tool based on prompt keywords."""
        p_lower = text.lower()

        # Export Restricted Request
        if "export" in p_lower and ("restricted" in p_lower or "rec-1003" in p_lower or "vault" in p_lower):
            m = re.search(r"rec-\d{4}", p_lower)
            rec_id = m.group(0).upper() if m else "REC-1003"
            return "export_restricted_records", "export_restricted_records", {"record_id": rec_id, "approval_id": manual_approval_id}

        # Synthetic Record Lookup
        if any(term in p_lower for term in ["lookup", "find customer", "account", "record", "rec-"]):
            m = re.search(r"rec-\d{4}", p_lower)
            rec_id = m.group(0).upper() if m else "REC-1001"
            return "lookup_synthetic_record", "lookup_synthetic_record", {"record_id": rec_id}

        # Safe Math Calculation
        if any(term in p_lower for term in ["calculate", "math", "evaluate", "metric"]) or re.search(r"\d+\s*[\+\-\*\/]\s*\d+", text):
            expr_match = re.search(r"([\d\.\s\+\-\*\/\(\)]+)", text)
            expr = expr_match.group(1).strip() if expr_match else "42 * 10"
            return "calculate_secure_metric", "calculate_secure_metric", {"expression": expr}

        # Text Analysis
        if any(term in p_lower for term in ["analyze", "statistics", "word count", "tokens", "density"]):
            return "analyze_text_statistics", "analyze_text_statistics", {"target_text": text}

        # General Query
        return "view_overview", None, {}

# Global Instance
orchestrator = AgentOrchestrator()
