import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secureagent.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Audit Log Table with Hash Chaining
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        policy_outcome TEXT NOT NULL,
        redaction_summary TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        details TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        entry_hash TEXT NOT NULL
    );
    """)

    # 2. Synthetic Enterprise Records (Access Controlled)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS synthetic_records (
        id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        account_number TEXT NOT NULL,
        classification TEXT NOT NULL,
        ssn_masked TEXT NOT NULL,
        balance REAL NOT NULL,
        notes TEXT NOT NULL,
        department TEXT NOT NULL
    );
    """)

    # 3. Human Approval Requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        approval_id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        target_resource TEXT NOT NULL,
        risk_score REAL NOT NULL,
        payload_preview TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        decided_at TEXT,
        decided_by TEXT,
        rejection_reason TEXT
    );
    """)

    # 4. Configurable Policies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        policy_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        config_json TEXT NOT NULL,
        is_enabled INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL
    );
    """)

    conn.commit()

    # Seed Synthetic Records if empty
    cursor.execute("SELECT COUNT(*) FROM synthetic_records")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            ("REC-1001", "Jane Doe", "ACCT-984210", "INTERNAL", "***-**-4589", 14500.50, "Standard account holder - KYC verified", "Retail"),
            ("REC-1002", "Alex Mercer", "ACCT-331045", "CONFIDENTIAL", "***-**-9012", 280000.00, "High net worth individual - strict audit", "Wealth"),
            ("REC-1003", "Morgan Vance", "ACCT-774129", "RESTRICTED", "***-**-1122", 1540000.00, "Corporate treasury vault account - human approval required for export", "Executive"),
            ("REC-1004", "Taylor Kim", "ACCT-556102", "PUBLIC", "***-**-7890", 3200.10, "Non-sensitive demo reference record", "General"),
            ("REC-1005", "Jordan Smith", "ACCT-889104", "CONFIDENTIAL", "***-**-6543", 94250.75, "Commercial loan portfolio record", "Commercial")
        ]
        cursor.executemany("""
            INSERT INTO synthetic_records (id, customer_name, account_number, classification, ssn_masked, balance, notes, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_data)
        conn.commit()

    # Seed Default Policies if empty
    cursor.execute("SELECT COUNT(*) FROM policies")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        default_policies = [
            ("POL-RBAC-01", "Role-Based Tool Access Control", "Restricts sensitive tool execution based on caller role", "RBAC",
             json.dumps({
                 "viewer": ["calculate_secure_metric", "analyze_text_statistics"],
                 "analyst": ["calculate_secure_metric", "analyze_text_statistics", "lookup_synthetic_record"],
                 "admin": ["calculate_secure_metric", "analyze_text_statistics", "lookup_synthetic_record", "export_restricted_records"]
             }), 1, now),
            ("POL-SENS-02", "Data Sensitivity Export Barrier", "Requires administrative privilege and explicit human sign-off for RESTRICTED data", "SENSITIVITY",
             json.dumps({
                 "PUBLIC": {"min_role": "viewer", "requires_approval": False},
                 "INTERNAL": {"min_role": "analyst", "requires_approval": False},
                 "CONFIDENTIAL": {"min_role": "analyst", "requires_approval": False},
                 "RESTRICTED": {"min_role": "admin", "requires_approval": True}
             }), 1, now),
            ("POL-RISK-03", "Adaptive Risk Threshold Gating", "Automatically suspends execution and requests human review if aggregate risk score exceeds 0.70", "RISK_THRESHOLD",
             json.dumps({"risk_threshold": 0.70, "fail_closed": True}), 1, now),
            ("POL-REDACT-04", "Pre-Model Redaction Mandate", "Guarantees all detected PII entities are scrubbed prior to dispatching context to language models", "REDACTION",
             json.dumps({"enforce_strict_redaction": True, "allowed_identifiers": []}), 1, now)
        ]
        cursor.executemany("""
            INSERT INTO policies (policy_id, name, description, rule_type, config_json, is_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_policies)
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
