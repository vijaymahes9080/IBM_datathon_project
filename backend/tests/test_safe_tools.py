import pytest
from app.tools.safe_tools import safe_tools

def test_secure_metric_basic_math():
    res = safe_tools.calculate_secure_metric("100 * (4 + 6) / 2")
    assert res.status == "SUCCESS"
    assert res.output["result"] == 500.0

def test_secure_metric_blocks_arbitrary_code():
    res = safe_tools.calculate_secure_metric("__import__('os').system('dir')")
    assert res.status == "ERROR"
    assert "Disallowed" in res.error_message or "parsing error" in res.error_message

def test_secure_metric_division_by_zero():
    res = safe_tools.calculate_secure_metric("42 / 0")
    assert res.status == "ERROR"
    assert "Division by zero" in res.error_message

def test_text_statistics():
    sample = "SecureAgent AI enforces outer boundary data protection and security controls."
    res = safe_tools.analyze_text_statistics(sample)
    assert res.status == "SUCCESS"
    assert res.output["word_count"] == 10
    assert res.output["character_count"] > 20

def test_synthetic_record_rbac():
    # REC-1003 is RESTRICTED
    res_viewer = safe_tools.lookup_synthetic_record("REC-1003", actor_role="viewer")
    assert res_viewer.status == "BLOCKED"

    res_admin = safe_tools.lookup_synthetic_record("REC-1003", actor_role="admin")
    assert res_admin.status == "SUCCESS"
    assert res_admin.output["id"] == "REC-1003"
