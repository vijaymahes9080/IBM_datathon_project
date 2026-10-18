import pytest
from app.adapters.ibm_z import ibm_z_adapter

def test_ibm_z_posture_reporting():
    posture = ibm_z_adapter.get_platform_posture()
    assert posture.architecture is not None
    assert posture.execution_mode in ["PRODUCTION_IBM_Z", "LOCAL_EMULATION"]
    # If on x86/Windows, verify that it honestly reports local emulation
    if not posture.is_s390x:
        assert posture.execution_mode == "LOCAL_EMULATION"
        assert posture.cpacf_hardware_crypto["hardware_verified"] is False
        assert "Local" in posture.notes

def test_racf_identity_mapping():
    assert ibm_z_adapter.map_racf_identity("RACF-SEC01") == "admin"
    assert ibm_z_adapter.map_racf_identity("RACF-ADM99") == "admin"
    assert ibm_z_adapter.map_racf_identity("RACF-ANA04") == "analyst"
    assert ibm_z_adapter.map_racf_identity("RACF-VIEW01") == "viewer"

def test_accelerated_hash():
    digest = ibm_z_adapter.execute_accelerated_hash("IBM Z Confidential AI Test Payload")
    assert len(digest) == 64
