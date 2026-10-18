import pytest
from app.security.policy_engine import policy_engine

def test_viewer_allowed_safe_math():
    dec = policy_engine.evaluate_action(
        actor_role="viewer",
        action="calculate_secure_metric",
        target_sensitivity="PUBLIC"
    )
    assert dec.outcome == "ALLOWED"
    assert dec.requires_human_approval is False

def test_viewer_denied_synthetic_records():
    dec = policy_engine.evaluate_action(
        actor_role="viewer",
        action="lookup_synthetic_record",
        target_sensitivity="CONFIDENTIAL"
    )
    assert dec.outcome == "DENIED"
    assert "RBAC" in dec.reason or "Sensitivity" in dec.reason

def test_analyst_allowed_synthetic_records():
    dec = policy_engine.evaluate_action(
        actor_role="analyst",
        action="lookup_synthetic_record",
        target_sensitivity="CONFIDENTIAL"
    )
    assert dec.outcome == "ALLOWED"

def test_restricted_export_requires_approval():
    dec = policy_engine.evaluate_action(
        actor_role="admin",
        action="export_restricted_records",
        target_sensitivity="RESTRICTED"
    )
    assert dec.outcome == "PENDING_APPROVAL"
    assert dec.requires_human_approval is True

def test_fail_closed_on_high_threat():
    dec = policy_engine.evaluate_action(
        actor_role="admin",
        action="calculate_secure_metric",
        threat_score=0.92,
        is_threat_safe=False
    )
    assert dec.outcome == "DENIED"
    assert "Threat score" in dec.reason or "Adversarial" in dec.reason
