import pytest
from app.security.redactor import redactor_service

def test_ssn_redaction():
    text = "The applicant's social security number is 123-45-6789 for tax records."
    res = redactor_service.redact(text)
    assert res.redacted is True
    assert "123-45-6789" not in res.redacted_text
    assert res.classification in ["CONFIDENTIAL", "RESTRICTED"]
    assert "US_SSN" in res.entity_counts or len(res.detected_entities) > 0

def test_credit_card_redaction():
    text = "Payment details: Card 4532123456789012 expiring next month."
    res = redactor_service.redact(text)
    assert res.redacted is True
    assert "4532123456789012" not in res.redacted_text
    assert res.classification == "CONFIDENTIAL"

def test_api_key_redaction_restricted_classification():
    text = "Deploy with token sk-abcdef12345678901234567890 for cluster access."
    res = redactor_service.redact(text)
    assert res.redacted is True
    assert "sk-abcdef12345678901234567890" not in res.redacted_text
    assert res.classification == "RESTRICTED"

def test_ibm_racf_id_redaction():
    text = "Please link operator RACF-SEC8901 to the new authorization profile."
    res = redactor_service.redact(text)
    assert res.redacted is True
    assert "RACF-SEC8901" not in res.redacted_text
    assert res.classification == "CONFIDENTIAL"

def test_benign_text_classification():
    text = "Quarterly financial summary for public distribution."
    res = redactor_service.redact(text)
    assert res.redacted is False
    assert res.classification == "PUBLIC"
    assert res.original_text == res.redacted_text

def test_limitations_note_present():
    text = "Test sample"
    res = redactor_service.redact(text)
    assert len(res.limitations_note) > 0
