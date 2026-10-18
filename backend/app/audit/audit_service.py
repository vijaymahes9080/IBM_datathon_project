import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from ..database.db import get_connection

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class AuditRecord(BaseModel):
    id: Optional[int] = None
    request_id: str
    timestamp: str
    actor: str
    action: str
    risk_level: str
    policy_outcome: str
    redaction_summary: Dict[str, Any]
    approval_status: str
    details: Dict[str, Any]
    previous_hash: str
    entry_hash: str

class AuditVerificationReport(BaseModel):
    is_valid: bool
    total_records: int
    latest_hash: Optional[str] = None
    corrupted_record_id: Optional[int] = None
    verification_message: str

class AuditTrailService:
    def sanitize_payload(self, data: Any) -> Any:
        """Strip raw credentials, tokens, or plaintext secrets before auditing."""
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                lower_k = str(k).lower()
                if any(secret_term in lower_k for secret_term in ["password", "secret", "token", "raw_key", "authorization"]):
                    sanitized[k] = "[REDACTED_SECRET]"
                else:
                    sanitized[k] = self.sanitize_payload(v)
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_payload(item) for item in data]
        return data

    def compute_hash(
        self,
        prev_hash: str,
        request_id: str,
        timestamp: str,
        actor: str,
        action: str,
        risk_level: str,
        policy_outcome: str,
        approval_status: str,
        details_str: str
    ) -> str:
        """Compute deterministic SHA-256 digest of record contents chained to previous hash."""
        raw_payload = f"{prev_hash}|{request_id}|{timestamp}|{actor}|{action}|{risk_level}|{policy_outcome}|{approval_status}|{details_str}"
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    def get_latest_hash(self) -> str:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row["entry_hash"] if row else GENESIS_HASH

    def log_event(
        self,
        request_id: str,
        actor: str,
        action: str,
        risk_level: str,
        policy_outcome: str,
        redaction_summary: Dict[str, Any],
        approval_status: str = "NOT_REQUIRED",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditRecord:
        """Append cryptographically chained entry to audit log."""
        timestamp = datetime.now(timezone.utc).isoformat()
        sanitized_details = self.sanitize_payload(details or {})
        details_json = json.dumps(sanitized_details, sort_keys=True)
        redaction_json = json.dumps(redaction_summary, sort_keys=True)

        prev_hash = self.get_latest_hash()
        entry_hash = self.compute_hash(
            prev_hash=prev_hash,
            request_id=request_id,
            timestamp=timestamp,
            actor=actor,
            action=action,
            risk_level=risk_level,
            policy_outcome=policy_outcome,
            approval_status=approval_status,
            details_str=details_json
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (
                request_id, timestamp, actor, action, risk_level, policy_outcome,
                redaction_summary, approval_status, details, previous_hash, entry_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id, timestamp, actor, action, risk_level, policy_outcome,
            redaction_json, approval_status, details_json, prev_hash, entry_hash
        ))
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return AuditRecord(
            id=row_id,
            request_id=request_id,
            timestamp=timestamp,
            actor=actor,
            action=action,
            risk_level=risk_level,
            policy_outcome=policy_outcome,
            redaction_summary=redaction_summary,
            approval_status=approval_status,
            details=sanitized_details,
            previous_hash=prev_hash,
            entry_hash=entry_hash
        )

    def get_recent_logs(self, limit: int = 50, actor: Optional[str] = None) -> List[AuditRecord]:
        conn = get_connection()
        cursor = conn.cursor()
        if actor:
            cursor.execute("SELECT * FROM audit_log WHERE actor = ? ORDER BY id DESC LIMIT ?", (actor, limit))
        else:
            cursor.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        records = []
        for r in rows:
            records.append(
                AuditRecord(
                    id=r["id"],
                    request_id=r["request_id"],
                    timestamp=r["timestamp"],
                    actor=r["actor"],
                    action=r["action"],
                    risk_level=r["risk_level"],
                    policy_outcome=r["policy_outcome"],
                    redaction_summary=json.loads(r["redaction_summary"]),
                    approval_status=r["approval_status"],
                    details=json.loads(r["details"]),
                    previous_hash=r["previous_hash"],
                    entry_hash=r["entry_hash"]
                )
            )
        return records

    def verify_integrity(self) -> AuditVerificationReport:
        """Traverse the entire audit trail and mathematically verify hash linkage."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return AuditVerificationReport(
                is_valid=True,
                total_records=0,
                latest_hash=GENESIS_HASH,
                corrupted_record_id=None,
                verification_message="Audit log is currently empty. Hash root at genesis state."
            )

        expected_prev_hash = GENESIS_HASH
        for row in rows:
            row_id = row["id"]
            if row["previous_hash"] != expected_prev_hash:
                return AuditVerificationReport(
                    is_valid=False,
                    total_records=len(rows),
                    latest_hash=None,
                    corrupted_record_id=row_id,
                    verification_message=f"Hash chain broken at record #{row_id}: previous_hash mismatch."
                )

            recomputed_hash = self.compute_hash(
                prev_hash=row["previous_hash"],
                request_id=row["request_id"],
                timestamp=row["timestamp"],
                actor=row["actor"],
                action=row["action"],
                risk_level=row["risk_level"],
                policy_outcome=row["policy_outcome"],
                approval_status=row["approval_status"],
                details_str=row["details"]
            )

            if recomputed_hash != row["entry_hash"]:
                return AuditVerificationReport(
                    is_valid=False,
                    total_records=len(rows),
                    latest_hash=None,
                    corrupted_record_id=row_id,
                    verification_message=f"Tampering detected at record #{row_id}: entry_hash does not match recomputed SHA-256 digest."
                )

            expected_prev_hash = row["entry_hash"]

        return AuditVerificationReport(
            is_valid=True,
            total_records=len(rows),
            latest_hash=expected_prev_hash,
            corrupted_record_id=None,
            verification_message=f"Integrity verified: all {len(rows)} audit records form an unbroken, cryptographically valid SHA-256 chain."
        )

# Global Instance
audit_service = AuditTrailService()
