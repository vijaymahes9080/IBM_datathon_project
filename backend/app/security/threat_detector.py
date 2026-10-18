import re
from typing import List, Dict, Any
from pydantic import BaseModel

class ThreatSignal(BaseModel):
    category: str
    pattern_name: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    matched_text: str
    weight: float

class ThreatDetectionResult(BaseModel):
    input_text: str
    threat_score: float  # 0.0 to 1.0
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    is_safe: bool
    signals: List[ThreatSignal]
    recommendation: str
    defense_summary: str

# Threat heuristics catalog
INJECTION_RULES = [
    {
        "category": "INSTRUCTION_OVERRIDE",
        "pattern_name": "Ignore Previous Instructions",
        "regex": r"(?i)\b(ignore|disregard|forget|bypass|override)\b.*?\b(previous|all|system|security|prior)\b.*?\b(instructions|prompts|rules|policies|guidelines)\b",
        "severity": "CRITICAL",
        "weight": 0.90
    },
    {
        "category": "INSTRUCTION_OVERRIDE",
        "pattern_name": "System Prompt Override Delimiters",
        "regex": r"(?i)(<\/?system>|\[system\s*instruction\]|===+\s*new\s*system|---+\s*override\s*---+|<admin_override>)",
        "severity": "CRITICAL",
        "weight": 0.85
    },
    {
        "category": "JAILBREAK_PERSONA",
        "pattern_name": "Jailbreak Persona / DAN Mode",
        "regex": r"(?i)\b(DAN mode|developer mode|unrestricted mode|jailbreak|evil assistant|bypass filters|no restrictions|do anything now)\b",
        "severity": "CRITICAL",
        "weight": 0.88
    },
    {
        "category": "PRIVILEGE_ESCALATION",
        "pattern_name": "Privilege Escalation Request",
        "regex": r"(?i)\b(grant\s+(me\s+)?(admin|root|superuser)|elevate\s+privileges|disable\s+(security|redaction|audit|policy|logging))\b",
        "severity": "HIGH",
        "weight": 0.75
    },
    {
        "category": "DATA_EXFILTRATION",
        "pattern_name": "Bulk Sensitive Data Exfiltration Attempt",
        "regex": r"(?i)\b(dump\s+all|export\s+all|reveal\s+(unmasked|raw)\s+(ssn|passwords|keys|records|credentials)|exfiltrate)\b",
        "severity": "HIGH",
        "weight": 0.70
    },
    {
        "category": "UNAUTHORIZED_TOOL",
        "pattern_name": "Arbitrary Command / Shell Execution Attempt",
        "regex": r"(?i)\b(execute_shell|exec\(|os\.system|subprocess|drop\s+table|delete\s+from|cat\s+\/etc\/passwd|powershell\s+-enc)\b",
        "severity": "CRITICAL",
        "weight": 0.95
    },
    {
        "category": "ROLE_CONFUSION",
        "pattern_name": "Assistant Impersonation & Role Hijacking",
        "regex": r"(?i)\b(you are no longer|act as an unrestricted|pretend you have no safety|disregard your programming)\b",
        "severity": "MEDIUM",
        "weight": 0.55
    }
]

class ThreatDetectorService:
    def __init__(self):
        self.compiled_rules = [
            {**rule, "compiled": re.compile(rule["regex"])}
            for rule in INJECTION_RULES
        ]

    def scan_input(self, text: str) -> ThreatDetectionResult:
        if not text or not text.strip():
            return ThreatDetectionResult(
                input_text=text,
                threat_score=0.0,
                threat_level="LOW",
                is_safe=True,
                signals=[],
                recommendation="ALLOW",
                defense_summary="Empty or clean input with zero threat indicators."
            )

        detected_signals: List[ThreatSignal] = []
        max_weight = 0.0
        cumulative_weight = 0.0

        for rule in self.compiled_rules:
            matches = list(rule["compiled"].finditer(text))
            for m in matches:
                matched_str = m.group(0)
                signal = ThreatSignal(
                    category=rule["category"],
                    pattern_name=rule["pattern_name"],
                    severity=rule["severity"],
                    matched_text=matched_str[:40],
                    weight=rule["weight"]
                )
                detected_signals.append(signal)
                max_weight = max(max_weight, rule["weight"])
                cumulative_weight += rule["weight"] * 0.25

        raw_score = min(1.0, max_weight + cumulative_weight)
        score = round(raw_score, 3)

        if score >= 0.80:
            threat_level = "CRITICAL"
            is_safe = False
            rec = "BLOCK_IMMEDIATE"
            summary = "Prompt contains critical adversarial injection patterns designed to hijack control flow or execute unauthorized commands."
        elif score >= 0.60:
            threat_level = "HIGH"
            is_safe = False
            rec = "BLOCK_OR_REQUIRE_APPROVAL"
            summary = "High-risk instruction tampering or exfiltration pattern detected; policy requires blocking or strict administrative review."
        elif score >= 0.30:
            threat_level = "MEDIUM"
            is_safe = True
            rec = "ALLOW_WITH_RESTRICTION"
            summary = "Subtle or borderline phrasing detected; passing through redaction gateway with elevated audit logging."
        else:
            threat_level = "LOW"
            is_safe = True
            rec = "ALLOW"
            summary = "No prompt injection or adversarial signatures discovered."

        return ThreatDetectionResult(
            input_text=text,
            threat_score=score,
            threat_level=threat_level,
            is_safe=is_safe,
            signals=detected_signals,
            recommendation=rec,
            defense_summary=summary
        )

# Global Singleton Instance
threat_detector = ThreatDetectorService()
