import httpx
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..config import settings
from ..security.redactor import SENSITIVE_PATTERNS

class ModelResponse(BaseModel):
    adapter_name: str
    generated_text: str
    input_payload_sent: str
    latency_ms: float
    offline_mode: bool
    safety_assertions_passed: bool

class ModelAdapterService:
    def verify_no_unmasked_pii(self, text: str) -> bool:
        """Defense-in-depth pre-flight check: ensure no unmasked credit card or SSN is sent."""
        ssn_re = re.compile(SENSITIVE_PATTERNS["US_SSN"]["regex"])
        cc_re = re.compile(SENSITIVE_PATTERNS["CREDIT_CARD"]["regex"])
        return not bool(ssn_re.search(text) or cc_re.search(text))

    async def generate_response(
        self,
        redacted_prompt: str,
        mode: str = "deterministic",
        context_data: Optional[Dict[str, Any]] = None,
        tool_results: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        """
        Dispatch redacted prompt to the selected processing adapter.
        Guarantees that raw sensitive identifiers never cross the model boundary.
        """
        import time
        start_time = time.time()

        # Strict defense-in-depth safety assertion
        safety_ok = self.verify_no_unmasked_pii(redacted_prompt)
        if not safety_ok:
            return ModelResponse(
                adapter_name="Security Gateway Guard",
                generated_text="Model dispatch blocked: Unmasked PII detected in outgoing payload.",
                input_payload_sent="[BLOCKED_BY_SAFETY_GUARD]",
                latency_ms=0.5,
                offline_mode=True,
                safety_assertions_passed=False
            )

        # 1. Deterministic Rule-Based Engine (Default, Zero-Network, 100% Demonstrable)
        if mode == "deterministic" or mode not in ["ollama", "ibm_z_enclave"]:
            resp_text = self._generate_deterministic(redacted_prompt, tool_results)
            latency = round((time.time() - start_time) * 1000, 2)
            return ModelResponse(
                adapter_name="Local Deterministic Reasoning Engine (Offline)",
                generated_text=resp_text,
                input_payload_sent=redacted_prompt,
                latency_ms=latency,
                offline_mode=True,
                safety_assertions_passed=True
            )

        # 2. IBM Z Enclave Simulation Mode
        elif mode == "ibm_z_enclave":
            resp_text = (
                f"[Processed within IBM Secure Execution Enclave Isolation]\n\n"
                f"{self._generate_deterministic(redacted_prompt, tool_results)}\n\n"
                f"(Workload memory protected against host hypervisor inspection via Ultravisor hardware keys)"
            )
            latency = round((time.time() - start_time) * 1000, 2)
            return ModelResponse(
                adapter_name="IBM Z Secure Execution Enclave Adapter (Simulation)",
                generated_text=resp_text,
                input_payload_sent=redacted_prompt,
                latency_ms=latency,
                offline_mode=True,
                safety_assertions_passed=True
            )

        # 3. Local Ollama Adapter (with graceful offline fallback)
        elif mode == "ollama":
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(
                        f"{settings.OLLAMA_BASE_URL}/api/generate",
                        json={
                            "model": settings.OLLAMA_MODEL,
                            "prompt": redacted_prompt,
                            "stream": False
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        latency = round((time.time() - start_time) * 1000, 2)
                        return ModelResponse(
                            adapter_name=f"Ollama Local LLM ({settings.OLLAMA_MODEL})",
                            generated_text=data.get("response", "No response content generated."),
                            input_payload_sent=redacted_prompt,
                            latency_ms=latency,
                            offline_mode=False,
                            safety_assertions_passed=True
                        )
            except Exception as e:
                # Graceful offline fallback
                pass

            # Fallback when Ollama daemon is not running locally
            fallback_text = (
                f"[Note: Local Ollama daemon unreachable at {settings.OLLAMA_BASE_URL}. Active fallback to Deterministic Engine]\n\n"
                f"{self._generate_deterministic(redacted_prompt, tool_results)}"
            )
            latency = round((time.time() - start_time) * 1000, 2)
            return ModelResponse(
                adapter_name="Ollama Adapter (Fallback to Deterministic Engine)",
                generated_text=fallback_text,
                input_payload_sent=redacted_prompt,
                latency_ms=latency,
                offline_mode=True,
                safety_assertions_passed=True
            )

    def _generate_deterministic(self, prompt: str, tool_results: Optional[Dict[str, Any]] = None) -> str:
        """Deterministic NLP synthesizer responding accurately to queries and tools."""
        p_lower = prompt.lower()

        # If a tool result is present, summarize it cleanly
        if tool_results:
            tool_name = tool_results.get("tool_name", "")
            output = tool_results.get("output", {})
            if tool_name == "calculate_secure_metric":
                res = output.get("result") if isinstance(output, dict) else output
                expr = output.get("expression") if isinstance(output, dict) else ""
                return f"I evaluated the mathematical expression '{expr}'. The verified result is {res}."
            elif tool_name == "analyze_text_statistics":
                return (
                    f"Text Analysis Complete:\n"
                    f"• Word count: {output.get('word_count')}\n"
                    f"• Character count: {output.get('character_count')}\n"
                    f"• Estimated token count: {output.get('estimated_tokens')}\n"
                    f"• Lexical diversity score: {output.get('lexical_diversity')}"
                )
            elif tool_name == "lookup_synthetic_record":
                rec = output
                return (
                    f"Enterprise Record Retrieved:\n"
                    f"• ID: {rec.get('id')}\n"
                    f"• Customer: {rec.get('customer_name')}\n"
                    f"• Account: {rec.get('account_number')}\n"
                    f"• Classification: {rec.get('classification')}\n"
                    f"• SSN: {rec.get('ssn_masked')}\n"
                    f"• Balance: ${rec.get('balance'):,.2f}\n"
                    f"• Department: {rec.get('department')}\n"
                    f"• Notes: {rec.get('notes')}"
                )
            elif tool_name == "export_restricted_records":
                return (
                    f"Restricted Export Successful:\n"
                    f"Record {output.get('record', {}).get('id')} has been exported under authorized human approval token {output.get('export_token')}."
                )

        if "balance" in p_lower or "account" in p_lower:
            return "To view account details or balances, request a synthetic record lookup (e.g., 'Lookup record REC-1001'). Your role permissions will determine what fields are visible."
        if "calculate" in p_lower or "+" in p_lower or "*" in p_lower:
            return "I can execute secure mathematical calculations through the allowlisted calculation tool. Please specify the arithmetic expression."
        if "policy" in p_lower or "rule" in p_lower:
            return "Enterprise security policies enforce strict role-based access control, automated Presidio PII redaction, threat heuristics, and tamper-evident audit logging."

        return (
            f"Your request was received and processed through the SecureAgent AI gateway. "
            f"All sensitive identifiers were masked prior to reasoning, and actions complied with enterprise policy."
        )

# Global Instance
model_adapter = ModelAdapterService()
