import pytest
from app.audit.audit_service import audit_service
from app.database.db import get_connection

def test_audit_event_hash_chaining():
    # Log two distinct events
    ev1 = audit_service.log_event(
        request_id="REQ-TEST-001",
        actor="unit_tester",
        action="TEST_ACTION_ONE",
        risk_level="LOW",
        policy_outcome="ALLOWED",
        redaction_summary={"COUNT": 1},
        approval_status="NOT_REQUIRED",
        details={"info": "first event"}
    )
    assert len(ev1.entry_hash) == 64

    ev2 = audit_service.log_event(
        request_id="REQ-TEST-002",
        actor="unit_tester",
        action="TEST_ACTION_TWO",
        risk_level="MEDIUM",
        policy_outcome="ALLOWED",
        redaction_summary={"COUNT": 2},
        approval_status="NOT_REQUIRED",
        details={"info": "second event"}
    )
    assert ev2.previous_hash == ev1.entry_hash

def test_audit_integrity_verification():
    report = audit_service.verify_integrity()
    assert report.is_valid is True
    assert report.total_records > 0
    assert report.corrupted_record_id is None

def test_secret_scrubbing_in_audit_details():
    ev = audit_service.log_event(
        request_id="REQ-TEST-SECRET",
        actor="unit_tester",
        action="LOGIN_TEST",
        risk_level="LOW",
        policy_outcome="ALLOWED",
        redaction_summary={},
        details={"user": "alice", "password": "SuperSecretPassword123!", "api_token": "sk-123456789"}
    )
    assert ev.details["password"] == "[REDACTED_SECRET]"
    assert ev.details["api_token"] == "[REDACTED_SECRET]"
