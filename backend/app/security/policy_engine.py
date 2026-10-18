import json
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel
from ..database.db import get_connection

class PolicyDecision(BaseModel):
    outcome: str  # ALLOWED, DENIED, PENDING_APPROVAL
    reason: str
    matched_policy_id: Optional[str] = None
    requires_human_approval: bool = False
    risk_score: float = 0.0
    action: str
    actor_role: str
    target_sensitivity: str

# Sensitivity ranking for least privilege checks
SENSITIVITY_RANK = {
    "PUBLIC": 0,
    "INTERNAL": 1,
    "CONFIDENTIAL": 2,
    "RESTRICTED": 3
}

ROLE_CLEARANCE = {
    "viewer": 0,       # Can view PUBLIC
    "analyst": 2,      # Can view PUBLIC, INTERNAL, CONFIDENTIAL
    "admin": 3         # Can access RESTRICTED (with approval when exporting)
}

class PolicyEngineService:
    def __init__(self):
        pass

    def evaluate_action(
        self,
        actor_role: str,
        action: str,
        target_sensitivity: str = "INTERNAL",
        threat_score: float = 0.0,
        is_threat_safe: bool = True,
        tool_args: Optional[Dict[str, Any]] = None
    ) -> PolicyDecision:
        """
        Deterministic, outside-the-model policy evaluation.
        Fails closed on any unexpected state or error.
        """
        try:
            actor_role = actor_role.lower().strip()
            target_sensitivity = target_sensitivity.upper().strip()

            # 1. Fail closed on severe threat detection
            if threat_score >= 0.70 or not is_threat_safe:
                return PolicyDecision(
                    outcome="DENIED",
                    reason=f"Policy Block: Threat score ({threat_score}) exceeds security limit or input contains adversarial injection patterns.",
                    matched_policy_id="POL-RISK-03",
                    requires_human_approval=False,
                    risk_score=threat_score,
                    action=action,
                    actor_role=actor_role,
                    target_sensitivity=target_sensitivity
                )

            # 2. RBAC check on Tool / Action
            role_tools = {
                "viewer": ["calculate_secure_metric", "analyze_text_statistics", "view_overview"],
                "analyst": ["calculate_secure_metric", "analyze_text_statistics", "lookup_synthetic_record", "view_overview"],
                "admin": ["calculate_secure_metric", "analyze_text_statistics", "lookup_synthetic_record", "export_restricted_records", "view_overview", "manage_policy"]
            }

            allowed_tools = role_tools.get(actor_role, [])
            if action not in allowed_tools:
                return PolicyDecision(
                    outcome="DENIED",
                    reason=f"RBAC Violation: Role '{actor_role}' lacks permission to execute '{action}'.",
                    matched_policy_id="POL-RBAC-01",
                    requires_human_approval=False,
                    risk_score=0.85,
                    action=action,
                    actor_role=actor_role,
                    target_sensitivity=target_sensitivity
                )

            # 3. Data Sensitivity vs Role Clearance
            user_clearance = ROLE_CLEARANCE.get(actor_role, 0)
            required_clearance = SENSITIVITY_RANK.get(target_sensitivity, 1)

            if user_clearance < required_clearance:
                return PolicyDecision(
                    outcome="DENIED",
                    reason=f"Sensitivity Barrier: Data classified as '{target_sensitivity}' requires higher role clearance than '{actor_role}'.",
                    matched_policy_id="POL-SENS-02",
                    requires_human_approval=False,
                    risk_score=0.75,
                    action=action,
                    actor_role=actor_role,
                    target_sensitivity=target_sensitivity
                )

            # 4. High-Risk Action / Sensitive Export Gating (Human-In-The-Loop Approval)
            if action == "export_restricted_records" or target_sensitivity == "RESTRICTED":
                return PolicyDecision(
                    outcome="PENDING_APPROVAL",
                    reason="Mandatory Human Approval: Exporting or processing RESTRICTED enterprise records requires security administrator sign-off.",
                    matched_policy_id="POL-SENS-02",
                    requires_human_approval=True,
                    risk_score=0.80,
                    action=action,
                    actor_role=actor_role,
                    target_sensitivity=target_sensitivity
                )

            # 5. Composite Risk Calculation for Allowed Action
            base_risk = 0.05
            if target_sensitivity == "CONFIDENTIAL":
                base_risk = 0.25
            elif target_sensitivity == "INTERNAL":
                base_risk = 0.10
            
            blended_risk = round(min(0.65, base_risk + (threat_score * 0.4)), 3)

            return PolicyDecision(
                outcome="ALLOWED",
                reason="Policy Approved: Caller permissions, data sensitivity boundaries, and threat heuristics satisfied.",
                matched_policy_id="POL-RBAC-01",
                requires_human_approval=False,
                risk_score=blended_risk,
                action=action,
                actor_role=actor_role,
                target_sensitivity=target_sensitivity
            )

        except Exception as e:
            # Deterministic Fail Closed
            return PolicyDecision(
                outcome="DENIED",
                reason=f"Fail-Closed Triggered: Policy engine exception ({str(e)}).",
                matched_policy_id="POL-FAIL-CLOSED",
                requires_human_approval=False,
                risk_score=1.0,
                action=action,
                actor_role=actor_role,
                target_sensitivity=target_sensitivity
            )

# Global Singleton Instance
policy_engine = PolicyEngineService()
