import re
import time
import logging
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try importing Presidio components
try:
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    PRESIODIO_AVAILABLE = True
except ImportError:
    PRESIODIO_AVAILABLE = False
    logger.warning("Microsoft Presidio not found; using deterministic high-assurance regex engine.")

class DetectedEntity(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    text_snippet: str

class RedactionResult(BaseModel):
    original_text: str
    redacted_text: str
    detected_entities: List[DetectedEntity]
    entity_counts: Dict[str, int]
    classification: str  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    redacted: bool
    engine_used: str  # "Microsoft Presidio (NLP + Custom Recognizers)" or "Deterministic Rule-Based Redactor"
    limitations_note: str

# Deterministic High-Assurance Regex Patterns for Fallback & Custom Recognizers
SENSITIVE_PATTERNS = {
    "US_SSN": {
        "regex": r"\b(?!000|666|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b",
        "score": 0.95,
        "classification": "CONFIDENTIAL"
    },
    "CREDIT_CARD": {
        "regex": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
        "score": 0.95,
        "classification": "CONFIDENTIAL"
    },
    "EMAIL_ADDRESS": {
        "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "score": 0.85,
        "classification": "INTERNAL"
    },
    "PHONE_NUMBER": {
        "regex": r"\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b",
        "score": 0.85,
        "classification": "INTERNAL"
    },
    "API_KEY": {
        "regex": r"\b(?:sk-[a-zA-Z0-9]{20,48}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})\b",
        "score": 0.98,
        "classification": "RESTRICTED"
    },
    "IBM_RACF_ID": {
        "regex": r"\b(?:RACF-[A-Z0-9]{4,8}|IBMZ-[A-Z0-9]{6,8})\b",
        "score": 0.92,
        "classification": "CONFIDENTIAL"
    },
    "MEDICAL_RECORD_NUMBER": {
        "regex": r"\b(?:MRN-\d{6,10}|PATIENT-\d{5,8})\b",
        "score": 0.90,
        "classification": "CONFIDENTIAL"
    },
    "ACCOUNT_NUMBER": {
        "regex": r"\bACCT-[0-9]{6,10}\b",
        "score": 0.88,
        "classification": "CONFIDENTIAL"
    }
}

class SensitiveDataProtectionService:
    def __init__(self):
        self.presidio_analyzer = None
        self.presidio_anonymizer = None
        self.init_presidio()

    def init_presidio(self):
        if not PRESIODIO_AVAILABLE:
            return
        try:
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            
            # Explicitly configure lightweight local en_core_web_sm to avoid 400MB lg download
            nlp_config = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
            }
            provider = NlpEngineProvider(nlp_configuration=nlp_config)
            nlp_engine = provider.create_engine()

            # Initialize Presidio Analyzer & Anonymizer
            self.presidio_analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            self.presidio_anonymizer = AnonymizerEngine()

            # Add custom enterprise pattern recognizers for all sensitive patterns
            for name, meta in SENSITIVE_PATTERNS.items():
                pattern = Pattern(name=f"{name}_pattern", regex=meta["regex"], score=meta["score"])
                recognizer = PatternRecognizer(supported_entity=name, patterns=[pattern])
                self.presidio_analyzer.registry.add_recognizer(recognizer)
            logger.info("Presidio Analyzer initialized with en_core_web_sm and enterprise recognizers.")
        except Exception as e:
            logger.warning(f"Presidio model initialization warning (falling back to deterministic regex): {e}")
            self.presidio_analyzer = None
            self.presidio_anonymizer = None

    def classify_text(self, detected_entities: List[DetectedEntity]) -> str:
        """Assign data sensitivity classification according to discovered entities."""
        if not detected_entities:
            return "PUBLIC"
        
        has_restricted = any(
            e.entity_type in ["API_KEY", "PRIVATE_KEY", "RESTRICTED"] for e in detected_entities
        )
        if has_restricted:
            return "RESTRICTED"

        has_confidential = any(
            e.entity_type in ["US_SSN", "CREDIT_CARD", "IBM_RACF_ID", "MEDICAL_RECORD_NUMBER", "ACCOUNT_NUMBER", "IBAN_CODE"]
            for e in detected_entities
        )
        if has_confidential:
            return "CONFIDENTIAL"

        has_internal = any(
            e.entity_type in ["EMAIL_ADDRESS", "PHONE_NUMBER", "IP_ADDRESS"]
            for e in detected_entities
        )
        if has_internal:
            return "INTERNAL"

        return "INTERNAL"

    def redact(self, text: str) -> RedactionResult:
        """Scrub sensitive identifiers and provide deterministic audit summary."""
        if not text or not text.strip():
            return RedactionResult(
                original_text=text,
                redacted_text=text,
                detected_entities=[],
                entity_counts={},
                classification="PUBLIC",
                redacted=False,
                engine_used="Deterministic Engine",
                limitations_note="No text provided."
            )

        detected_entities: List[DetectedEntity] = []
        entity_counts: Dict[str, int] = {}
        engine_used = "Deterministic Rule-Based Redactor"

        # Attempt Presidio if ready
        if self.presidio_analyzer and self.presidio_anonymizer:
            try:
                results = self.presidio_analyzer.analyze(
                    text=text,
                    language="en",
                    entities=list(SENSITIVE_PATTERNS.keys()) + ["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "IP_ADDRESS"]
                )
                if results:
                    for res in results:
                        entity_type = res.entity_type
                        snippet = text[res.start:res.end]
                        detected_entities.append(
                            DetectedEntity(
                                entity_type=entity_type,
                                start=res.start,
                                end=res.end,
                                score=res.score,
                                text_snippet=snippet[:4] + "***" if len(snippet) > 4 else "***"
                            )
                        )
                        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

                    anonymized = self.presidio_anonymizer.anonymize(
                        text=text,
                        analyzer_results=results
                    )
                    classification = self.classify_text(detected_entities)
                    return RedactionResult(
                        original_text=text,
                        redacted_text=anonymized.text,
                        detected_entities=detected_entities,
                        entity_counts=entity_counts,
                        classification=classification,
                        redacted=len(detected_entities) > 0,
                        engine_used="Microsoft Presidio (NLP + Custom Enterprise Recognizers)",
                        limitations_note="Statistical and regex recognizers may miss novel syntaxes, leetspeak encodings, or contextual PII without structural markers."
                    )
            except Exception as e:
                logger.warning(f"Presidio analyze error, falling back to deterministic engine: {e}")

        # Deterministic Regex Redactor (High-speed, zero-dependency, guaranteed reproducibility)
        redacted_text = text
        for entity_type, config in SENSITIVE_PATTERNS.items():
            pattern = re.compile(config["regex"], re.IGNORECASE)
            matches = list(pattern.finditer(redacted_text))
            if matches:
                # Process in reverse to maintain string index integrity
                for match in reversed(matches):
                    snippet = match.group(0)
                    start, end = match.start(), match.end()
                    detected_entities.append(
                        DetectedEntity(
                            entity_type=entity_type,
                            start=start,
                            end=end,
                            score=config["score"],
                            text_snippet=snippet[:3] + "***" if len(snippet) > 3 else "***"
                        )
                    )
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                    placeholder = f"<{entity_type}>"
                    redacted_text = redacted_text[:start] + placeholder + redacted_text[end:]

        classification = self.classify_text(detected_entities)
        return RedactionResult(
            original_text=text,
            redacted_text=redacted_text,
            detected_entities=detected_entities,
            entity_counts=entity_counts,
            classification=classification,
            redacted=len(detected_entities) > 0,
            engine_used="Deterministic Rule-Based Redactor (RegEx + Enterprise Identifiers)",
            limitations_note="Rule-based matching covers known high-risk syntactic patterns (SSN, Cards, RACF IDs, Keys, MRN, Phones, Emails). Context-dependent semantic entities require active NLP models."
        )

# Global Singleton Instance
redactor_service = SensitiveDataProtectionService()
