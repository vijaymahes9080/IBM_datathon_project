# SecureAgent AI — Video Narration Script

**Challenge**: IBM Z Datathon 2026 — *“AI Secured: Innovation Without Exposure”*  
**Duration**: 175 Seconds  
**Voice**: `en-US-ChristopherNeural` (Clear, authoritative, professional technical register)  
**Total Word Count**: 342 words (~117 words/min with natural pauses)

---

### Scene 1: The Problem (0:00 – 0:30 | 62 words)
**Visual**: Opening title card transitions to enterprise risk diagram showing unprotected AI agent connected to corporate database.  
**Caption**: *“The Challenge: Generative AI without an Outer Security Perimeter”*

> "In modern enterprises, generative AI agents are increasingly connected to databases and automated workflows. But large language models cannot reliably police themselves. When sensitive customer data enters prompt context, or an adversarial prompt overrides model instructions, internal guardrails fail. Enterprises cannot innovate with generative AI if it means risking confidential data exposure or unverified system actions."

---

### Scene 2: How It Works — Architecture (0:30 – 1:15 | 88 words)
**Visual**: Clean, animated architectural flow: Ingress $\to$ Presidio Redactor $\to$ Threat Scanner $\to$ Deterministic Policy Engine (RBAC) $\to$ Safe Tools & HITL $\to$ SHA-256 Ledger. Cuts to Overview dashboard.  
**Caption**: *“Deterministic Outer Security Perimeter Outside the LLM”*

> "SecureAgent AI solves this by establishing a deterministic outer security perimeter around the language model. The model is treated as an untrusted reasoning component. Before any prompt reaches an adapter, Microsoft Presidio and enterprise recognizers scrub sensitive identifiers. An adversarial scanner intercepts injection attacks, while a deterministic policy engine enforces role-based clearance levels outside model context. High-risk actions require administrator sign-off, and every decision is permanently recorded in an unbroken, tamper-evident SHA-256 hash-chained ledger."

---

### Scene 3: Live Security Demonstration (1:15 – 2:15 | 118 words)
**Visual**: Live 1080p recorded walkthrough of real application on `http://127.0.0.1:8000/`.  
- **1:15–1:30**: PII Redaction & Payload Comparison (`<US_SSN>`, `<CREDIT_CARD>`).  
- **1:30–1:42**: Adversarial prompt injection flagged (threat score 1.00) & blocked.  
- **1:42–1:55**: Viewer role denied customer records lookup; restricted export queued for approval.  
- **1:55–2:05**: Administrator approves ticket; safe execution resumes.  
- **2:05–2:15**: Evaluation Lab runs 16 live benchmarks; SHA-256 audit chain verified intact.  
**Captions**: *“Sensitive data redacted”* | *“Injection attempt blocked”* | *“RBAC enforced”* | *“Human approval verified”* | *“Cryptographic integrity validated”*

> "Here is SecureAgent AI running live. First, we submit an inquiry with synthetic Social Security and payment card numbers. The gateway classifies the request as confidential and scrubs each identifier. The model only ever receives masked tokens. Next, an adversarial injection attempt. The threat engine catches the instruction override, assigning a threat score of 1.0, and the policy engine blocks it immediately. When a viewer attempts an unauthorized record lookup, server-side RBAC denies access. For high-risk operations, like exporting restricted data, execution pauses until an administrator approves the ticket. Finally, our evaluation lab runs sixteen live adversarial benchmarks, while our cryptographic audit trail verifies that the hash chain is mathematically intact."

---

### Scene 4: IBM Z / LinuxONE & Enterprise Impact (2:15 – 2:55 | 74 words)
**Visual**: IBM Z Architecture posture view, CPACF coprocessor instructions (`KM`/`KMC`), IBM Secure Execution enclave memory protection, and closing title card.  
**Caption**: *“Linux on IBM Z & LinuxONE: Hardware-Anchored AI Security”*

> "SecureAgent AI is architected for Linux on IBM Z and LinuxONE. In production, our adapter bridges directly to on-chip CPACF instructions for line-speed cryptography. Workloads execute inside IBM Secure Execution enclaves, shielding in-memory model context from host inspection, with full RACF identity federation. Tested locally in emulation mode, SecureAgent AI proves that enterprises can deploy generative AI with complete confidence: enabling genuine innovation, without ever exposing confidential data."

---

### End Card (2:55 – 3:00)
**Visual**: Final title card:  
*“SecureAgent AI | AI Secured: Innovation Without Exposure”*  
*IBM Z Datathon 2026*
