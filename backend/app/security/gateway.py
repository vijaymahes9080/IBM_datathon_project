from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException, status
from ..adapters.ibm_z import ibm_z_adapter

class EnterprisePrincipal(BaseModel):
    user_id: str
    username: str
    role: str  # viewer, analyst, admin
    racf_id: Optional[str] = None
    department: str
    session_id: str

PERSONA_STORE: Dict[str, EnterprisePrincipal] = {
    "viewer": EnterprisePrincipal(
        user_id="USR-101",
        username="viewer_guest",
        role="viewer",
        racf_id="RACF-VIEW01",
        department="Public Relations",
        session_id="SESS-VIEW-984"
    ),
    "analyst": EnterprisePrincipal(
        user_id="USR-202",
        username="analyst_alice",
        role="analyst",
        racf_id="RACF-ANA04",
        department="Risk & Compliance",
        session_id="SESS-ANA-412"
    ),
    "admin": EnterprisePrincipal(
        user_id="USR-909",
        username="admin_secops",
        role="admin",
        racf_id="RACF-SEC01",
        department="Information Security",
        session_id="SESS-ADM-001"
    )
}

class SecurityGatewayService:
    def authenticate_actor(self, requested_role: str = "analyst", racf_id: Optional[str] = None) -> EnterprisePrincipal:
        """Authenticate persona or resolve from IBM RACF ID mapping."""
        if racf_id:
            mapped_role = ibm_z_adapter.map_racf_identity(racf_id)
            return EnterprisePrincipal(
                user_id=f"USR-{racf_id}",
                username=f"racf_user_{racf_id.lower()}",
                role=mapped_role,
                racf_id=racf_id,
                department="IBM Z RACF Federated Realm",
                session_id=f"SESS-{racf_id}"
            )
        clean_role = requested_role.lower().strip()
        if clean_role in PERSONA_STORE:
            return PERSONA_STORE[clean_role]
        return PERSONA_STORE["viewer"]

# Global Instance
security_gateway = SecurityGatewayService()
