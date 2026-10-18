import ast
import math
import operator
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from ..database.db import get_connection

class ToolExecutionResult(BaseModel):
    tool_name: str
    status: str  # SUCCESS, BLOCKED, ERROR
    output: Any
    error_message: Optional[str] = None
    audit_notes: str

# Safe AST Math Evaluator (No eval())
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_ast_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants allowed in secure arithmetic.")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported mathematical operator: {op_type.__name__}")
        left = _eval_ast_node(node.left)
        right = _eval_ast_node(node.right)
        if op_type == ast.Pow and (right > 100 or left > 1000):
            raise ValueError("Exponentiation arguments exceeded safe bounds.")
        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("Division by zero in secure metric.")
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return SAFE_OPERATORS[op_type](_eval_ast_node(node.operand))
    else:
        raise ValueError(f"Disallowed AST expression construct: {type(node).__name__}")

class SafeToolService:
    @staticmethod
    def calculate_secure_metric(expression: str) -> ToolExecutionResult:
        """Evaluate safe mathematical expression using AST tree parsing without eval()."""
        try:
            cleaned = expression.strip()
            if len(cleaned) > 200:
                raise ValueError("Expression length exceeds maximum allowed limit (200 chars).")
            tree = ast.parse(cleaned, mode='eval')
            val = _eval_ast_node(tree.body)
            return ToolExecutionResult(
                tool_name="calculate_secure_metric",
                status="SUCCESS",
                output={"expression": expression, "result": val},
                audit_notes="Safe AST numeric calculation executed successfully."
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_name="calculate_secure_metric",
                status="ERROR",
                output=None,
                error_message=f"Arithmetic parsing error: {str(e)}",
                audit_notes=f"Calculation rejected: {str(e)}"
            )

    @staticmethod
    def analyze_text_statistics(text: str) -> ToolExecutionResult:
        """Compute statistical breakdown of text length, tokens, and lexical diversity."""
        try:
            words = text.split()
            word_count = len(words)
            char_count = len(text)
            unique_words = len(set(w.lower() for w in words))
            token_estimate = max(1, int(char_count / 4))
            diversity_ratio = round(unique_words / max(1, word_count), 2)

            return ToolExecutionResult(
                tool_name="analyze_text_statistics",
                status="SUCCESS",
                output={
                    "character_count": char_count,
                    "word_count": word_count,
                    "estimated_tokens": token_estimate,
                    "unique_word_count": unique_words,
                    "lexical_diversity": diversity_ratio
                },
                audit_notes="Text metrics calculated without external model or data leakage."
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_name="analyze_text_statistics",
                status="ERROR",
                output=None,
                error_message=str(e),
                audit_notes=f"Text analysis failed: {str(e)}"
            )

    @staticmethod
    def lookup_synthetic_record(record_id: str, actor_role: str) -> ToolExecutionResult:
        """Query synthetic database with server-side RBAC and data classification barrier."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM synthetic_records WHERE id = ? OR account_number = ?", (record_id, record_id))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return ToolExecutionResult(
                    tool_name="lookup_synthetic_record",
                    status="ERROR",
                    output=None,
                    error_message=f"Record '{record_id}' not found in synthetic database.",
                    audit_notes="Lookup query returned 0 matches."
                )

            data = dict(row)
            classification = data["classification"]

            # Role clearance validation
            if classification == "RESTRICTED" and actor_role != "admin":
                return ToolExecutionResult(
                    tool_name="lookup_synthetic_record",
                    status="BLOCKED",
                    output=None,
                    error_message=f"Access Denied: Record '{record_id}' is RESTRICTED and requires administrator role.",
                    audit_notes=f"RBAC barrier blocked {actor_role} from accessing RESTRICTED record."
                )

            # Masking for lower clearance roles
            if actor_role == "viewer":
                data["notes"] = "[CONFIDENTIAL NOTES HIDDEN FROM VIEWER]"
                data["balance"] = 0.0

            return ToolExecutionResult(
                tool_name="lookup_synthetic_record",
                status="SUCCESS",
                output=data,
                audit_notes=f"Synthetic record {record_id} ({classification}) retrieved with appropriate role masking."
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_name="lookup_synthetic_record",
                status="ERROR",
                output=None,
                error_message=str(e),
                audit_notes=f"Database query error: {str(e)}"
            )

    @staticmethod
    def export_restricted_records(record_id: str, approval_id: str, actor_role: str) -> ToolExecutionResult:
        """High-risk action requiring verified, approved Human-In-The-Loop token."""
        try:
            if actor_role != "admin":
                return ToolExecutionResult(
                    tool_name="export_restricted_records",
                    status="BLOCKED",
                    output=None,
                    error_message="Unauthorized: Only administrators can execute export_restricted_records.",
                    audit_notes="Non-admin caller attempted restricted export."
                )

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT status, target_resource FROM approvals WHERE approval_id = ?", (approval_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return ToolExecutionResult(
                    tool_name="export_restricted_records",
                    status="BLOCKED",
                    output=None,
                    error_message=f"Approval token '{approval_id}' does not exist or has expired.",
                    audit_notes="Invalid approval token presented."
                )

            approval_status, target_res = row["status"], row["target_resource"]
            if approval_status != "APPROVED":
                conn.close()
                return ToolExecutionResult(
                    tool_name="export_restricted_records",
                    status="BLOCKED",
                    output=None,
                    error_message=f"Action Blocked: Approval request is currently '{approval_status}'. Must be APPROVED before execution.",
                    audit_notes=f"Export blocked due to unapproved token status ({approval_status})."
                )

            # Fetch the restricted record
            cursor.execute("SELECT * FROM synthetic_records WHERE id = ?", (record_id,))
            record_row = cursor.fetchone()
            conn.close()

            if not record_row:
                return ToolExecutionResult(
                    tool_name="export_restricted_records",
                    status="ERROR",
                    output=None,
                    error_message=f"Record {record_id} not found.",
                    audit_notes="Approved export failed: record missing."
                )

            return ToolExecutionResult(
                tool_name="export_restricted_records",
                status="SUCCESS",
                output={
                    "export_token": approval_id,
                    "record": dict(record_row),
                    "certified_by": "Human Security Administrator",
                    "export_timestamp": "Executed under audited authorization"
                },
                audit_notes=f"RESTRICTED record {record_id} successfully exported under verified approval token {approval_id}."
            )

        except Exception as e:
            return ToolExecutionResult(
                tool_name="export_restricted_records",
                status="ERROR",
                output=None,
                error_message=str(e),
                audit_notes=f"Restricted export failed: {str(e)}"
            )

# Global Instance
safe_tools = SafeToolService()
