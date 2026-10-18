import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080

def get_font(size, bold=False):
    paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf" if not bold else "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if not bold else "C:\\Windows\\Fonts\\arialbd.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

CAPTURES = [
    {
        "input": "raw_captures/overview_dashboard_1792292885925.png",
        "output": "clips/screen_overview.png",
        "badge": "PRODUCTION CONSOLE",
        "title": "Live Security Telemetry & Platform Posture",
        "desc": "Active outer perimeter guardrails, real-time audit ledger, and IBM Z adapter posture.",
        "badge_color": "#2563eb"
    },
    {
        "input": "raw_captures/pii_masking_comparison_1792292918149.png",
        "output": "clips/screen_pii_masking.png",
        "badge": "INGRESS DATA PROTECTION",
        "title": "Microsoft Presidio & Custom Recognizers Scrub Identifiers",
        "desc": "Raw SSN, card, and email are intercepted at gateway. Only redacted payload reaches model adapter.",
        "badge_color": "#10b981"
    },
    {
        "input": "raw_captures/prompt_injection_block_1792292928944.png",
        "output": "clips/screen_prompt_injection.png",
        "badge": "THREAT DEFENSE SCANNER",
        "title": "Adversarial Prompt Injection Blocked (Threat Score: 1.00)",
        "desc": "Instruction override detected; policy engine triggers fail-closed security block outside the model.",
        "badge_color": "#ef4444"
    },
    {
        "input": "raw_captures/hitl_suspended_admin_1792292991536.png",
        "output": "clips/screen_hitl_ticket.png",
        "badge": "ACCESS CONTROL & HITL",
        "title": "Server-Side RBAC Enforcement & Approval Ticket Created",
        "desc": "Viewer query denied. Restricted asset export halted and queued for administrator sign-off.",
        "badge_color": "#f59e0b"
    },
    {
        "input": "raw_captures/policy_management_approved_1792293013099.png",
        "output": "clips/screen_policy_approved.png",
        "badge": "HUMAN-IN-THE-LOOP",
        "title": "Administrator Reviews & Grants Verified Approval",
        "desc": "Suspended action approved in policy console; cryptographic execution token recorded to audit trail.",
        "badge_color": "#10b981"
    },
    {
        "input": "raw_captures/evaluation_suite_benchmarks_1792293042327.png",
        "output": "clips/screen_evaluation.png",
        "badge": "EMPIRICAL EVALUATION",
        "title": "16 Live Benchmark Test Cases Executed",
        "desc": "Empirical accuracy, precision, recall, and confusion matrix derived from live adversarial execution.",
        "badge_color": "#3b82f6"
    },
    {
        "input": "raw_captures/audit_log_verification_1792293078294.png",
        "output": "clips/screen_audit_verify.png",
        "badge": "CRYPTOGRAPHIC AUDIT",
        "title": "Tamper-Evident SHA-256 Hash Chain Integrity Verified",
        "desc": "Recursive hash traversal validates every ledger entry is uncompromised: Hash_n = SHA256(Hash_n-1 || Entry).",
        "badge_color": "#a855f7"
    },
    {
        "input": "raw_captures/platform_ibm_z_1792293100132.png",
        "output": "clips/screen_platform.png",
        "badge": "IBM Z PLATFORM ADAPTER",
        "title": "Hardware Security Posture: CPACF & Secure Execution",
        "desc": "Hardware instruction readiness (KM/KMC), Ultravisor enclave isolation, and RACF identity mapping.",
        "badge_color": "#a855f7"
    }
]

def annotate_image(c):
    if not os.path.exists(c["input"]):
        print(f"Warning: {c['input']} not found.")
        return

    img = Image.open(c["input"]).convert("RGB")
    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Clean lower-third callout banner
    banner_y = HEIGHT - 130
    draw.rectangle([60, banner_y, WIDTH - 60, HEIGHT - 30], fill="#0a0f18")
    draw.rectangle([60, banner_y, WIDTH - 60, HEIGHT - 30], outline="#1e293b", width=1)
    draw.rectangle([60, banner_y, 66, HEIGHT - 30], fill=c["badge_color"])

    # Badge pill
    badge_font = get_font(18, bold=True)
    badge_w = draw.textlength(c["badge"], font=badge_font)
    draw.rectangle([85, banner_y + 16, 95 + int(badge_w) + 10, banner_y + 46], fill="#111827", outline=c["badge_color"], width=1)
    draw.text((95, banner_y + 20), c["badge"], fill=c["badge_color"], font=badge_font)

    # Title
    title_font = get_font(24, bold=True)
    draw.text((115 + int(badge_w) + 15, banner_y + 18), c["title"], fill="#f8fafc", font=title_font)

    # Description
    desc_font = get_font(19, bold=False)
    draw.text((85, banner_y + 60), c["desc"], fill="#94a3b8", font=desc_font)

    img.save(c["output"])
    print(f"Created {c['output']}")

if __name__ == "__main__":
    os.makedirs("clips", exist_ok=True)
    for cap in CAPTURES:
        annotate_image(cap)
