import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080

def get_font(size, bold=False):
    # Try Windows system fonts
    font_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf" if not bold else "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if not bold else "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\consola.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_title_card():
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#080b11")
    draw = ImageDraw.Draw(img)

    # Subtle top accent bar
    draw.rectangle([0, 0, WIDTH, 6], fill="#2563eb")

    # Corner brackets / framing
    draw.rectangle([80, 80, WIDTH - 80, HEIGHT - 80], outline="#1e293b", width=1)
    
    font_meta = get_font(22, bold=True)
    font_title = get_font(72, bold=True)
    font_sub = get_font(34, bold=False)
    font_badge = get_font(20, bold=True)
    font_foot = get_font(20, bold=False)

    # Header category badge
    badge_text = "IBM Z DATATHON 2026 SUBMISSION"
    draw.rectangle([140, 140, 560, 185], fill="#111827", outline="#2563eb", width=1)
    draw.text((160, 150), badge_text, fill="#60a5fa", font=font_badge)

    # Main Project Title
    draw.text((140, 260), "SecureAgent AI", fill="#f1f5f9", font=font_title)
    
    # Subtitle / Challenge Theme
    draw.text((140, 360), "AI Secured: Innovation Without Exposure", fill="#38bdf8", font=font_sub)

    # Core value proposition bullets
    bullets = [
        ("Outer Security Perimeter", "Deterministic Python barrier isolating untrusted LLM reasoning"),
        ("Presidio Data Protection", "Zero PII leakage with custom enterprise regex recognizers"),
        ("Adversarial Threat Defense", "Scans prompt injections, jailbreaks, and command overrides"),
        ("IBM Z / LinuxONE Alignment", "Confidential computing, CPACF crypto, and RACF identity")
    ]

    y_start = 480
    for title, desc in bullets:
        # Indicator pip
        draw.rectangle([140, y_start + 8, 152, y_start + 20], fill="#2563eb")
        draw.text((170, y_start), title + " — ", fill="#f8fafc", font=get_font(24, bold=True))
        w = draw.textlength(title + " — ", font=get_font(24, bold=True))
        draw.text((170 + int(w), y_start), desc, fill="#94a3b8", font=get_font(24, bold=False))
        y_start += 70

    # Footer note
    draw.text((140, 930), "Platform: Linux on IBM Z / LinuxONE  |  Verified Local Emulation Architecture", fill="#64748b", font=font_foot)
    draw.text((WIDTH - 420, 930), "Live Demonstration Video", fill="#60a5fa", font=font_foot)

    img.save("graphics/01_title_card.png")
    print("Saved 01_title_card.png")

def create_problem_diagram():
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#080b11")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 6], fill="#ef4444")
    draw.rectangle([80, 80, WIDTH - 80, HEIGHT - 80], outline="#1e293b", width=1)

    font_hdr = get_font(42, bold=True)
    font_sub = get_font(24, bold=False)
    font_card_title = get_font(26, bold=True)
    font_card_desc = get_font(20, bold=False)

    draw.text((140, 130), "The Enterprise AI Vulnerability Gap", fill="#f87171", font=font_hdr)
    draw.text((140, 190), "Why Large Language Models Cannot Reliably Self-Police Internal Enterprise Access", fill="#94a3b8", font=font_sub)

    # 3 Flawed Assumptions vs Reality Cards
    cards = [
        ("Vulnerability 1: Unprotected Prompt Ingress", 
         "Incoming Prompts with PII / Secrets", 
         "Without an outer scanner, sensitive identifiers enter model context directly, leaking into logging pipelines, third-party model APIs, or fine-tuning datasets.",
         "#ef4444"),
        ("Vulnerability 2: Adversarial Injection Overrides", 
         "Jailbreaks & DAN Mode Payloads", 
         "System prompt guardrails are easily bypassed by instruction overrides. An untrusted model cannot evaluate its own execution boundaries.",
         "#f59e0b"),
        ("Vulnerability 3: Direct Database & Tool Invocation", 
         "Unbounded Tool Actions", 
         "If the language model directly decides which SQL query or API to execute, low-privilege users can trigger unauthorized data exfiltration.",
         "#a855f7")
    ]

    x = 140
    for title, sub, desc, color in cards:
        draw.rectangle([x, 270, x + 490, 840], fill="#0f1522", outline="#1e293b", width=1)
        draw.rectangle([x, 270, x + 490, 276], fill=color)
        
        draw.text((x + 25, 310), title, fill="#f1f5f9", font=font_card_title)
        draw.text((x + 25, 355), sub, fill=color, font=get_font(20, bold=True))
        
        # Word wrapped description
        import textwrap
        lines = textwrap.wrap(desc, width=34)
        y_text = 420
        for l in lines:
            draw.text((x + 25, y_text), l, fill="#94a3b8", font=font_card_desc)
            y_text += 34
        
        x += 540

    draw.text((140, 920), "Core Requirement: An outer deterministic security boundary outside model context", fill="#38bdf8", font=get_font(22, bold=True))
    img.save("graphics/02_problem_diagram.png")
    print("Saved 02_problem_diagram.png")

def create_architecture_diagram():
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#080b11")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 6], fill="#2563eb")
    draw.rectangle([80, 80, WIDTH - 80, HEIGHT - 80], outline="#1e293b", width=1)

    draw.text((140, 120), "SecureAgent AI — Outer Perimeter Architecture", fill="#f1f5f9", font=get_font(42, bold=True))
    draw.text((140, 180), "Deterministic Multi-Stage Bounded Security Enforcement (Outside Model Reasoning)", fill="#60a5fa", font=get_font(24, bold=False))

    stages = [
        ("01", "Presidio Ingress Redactor", "Detects SSN, credit cards, emails, RACF IDs; replaces with safe tokens.", "#10b981"),
        ("02", "Threat Heuristics Engine", "Scores instruction overrides, fake system delimiters, and command injection.", "#ef4444"),
        ("03", "Deterministic Policy Engine", "Enforces strict RBAC matrix (Viewer/Analyst/Admin) and fail-closed checks.", "#3b82f6"),
        ("04", "Safe Execution & HITL Gating", "AST safe math execution; restricted actions require admin approval sign-off.", "#f59e0b"),
        ("05", "Untrusted Model Adapter", "Receives strictly redacted payload; processes via local engine or enclave.", "#a855f7"),
        ("06", "Tamper-Evident SHA-256 Chain", "Hash-linked ledger: Hash_n = SHA256(Hash_n-1 || Entry). Verifiable.", "#38bdf8")
    ]

    y = 260
    for num, name, desc, color in stages:
        draw.rectangle([140, y, WIDTH - 140, y + 85], fill="#0f1522", outline="#1e293b", width=1)
        draw.rectangle([140, y, 146, y + 85], fill=color)
        
        draw.rectangle([165, y + 15, 235, y + 70], fill="#182234", outline="#2563eb", width=1)
        draw.text((180, y + 25), num, fill="#60a5fa", font=get_font(26, bold=True))
        
        draw.text((260, y + 16), name, fill="#f1f5f9", font=get_font(24, bold=True))
        draw.text((260, y + 48), desc, fill="#94a3b8", font=get_font(19, bold=False))
        
        y += 102

    draw.text((140, 920), "Key Guarantee: Raw confidential data never reaches the language model", fill="#10b981", font=get_font(22, bold=True))
    img.save("graphics/03_architecture_diagram.png")
    print("Saved 03_architecture_diagram.png")

def create_ibm_z_graphic():
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#080b11")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 6], fill="#a855f7")
    draw.rectangle([80, 80, WIDTH - 80, HEIGHT - 80], outline="#1e293b", width=1)

    draw.text((140, 120), "Linux on IBM Z & LinuxONE Hardware Security Integration", fill="#f1f5f9", font=get_font(40, bold=True))
    draw.text((140, 180), "Production Architecture Alignment for s390x Mainframe Infrastructure", fill="#c4b5fd", font=get_font(24, bold=False))

    pillars = [
        ("CPACF Crypto Acceleration",
         "On-chip hardware instructions (KM, KMC, KLMD, KMAC) execute AES-256-GCM and SHA-512 at wire speed without OS context-switch overhead.",
         "#a855f7"),
        ("IBM Secure Execution for Linux",
         "Ultravisor hardware memory encryption isolates guest VM memory. Host root administrators cannot inspect in-memory model weights or context.",
         "#3b82f6"),
        ("IBM RACF Enterprise Identity",
         "Federated identity mapper binds RACF user credentials directly to server-side RBAC clearance levels (Security Admin, Operations Analyst, Auditor).",
         "#10b981"),
        ("z/OS SMF & QRadar Audit Stream",
         "Local SHA-256 hash chains stream to z/OS SMF Type 83/119 records or IBM QRadar SIEM via RFC 5424 TLS for FIPS 140-3 compliance.",
         "#f59e0b")
    ]

    coords = [
        (140, 260, 920, 530),
        (980, 260, WIDTH - 140, 530),
        (140, 560, 920, 830),
        (980, 560, WIDTH - 140, 830)
    ]

    for (title, text, color), (x1, y1, x2, y2) in zip(pillars, coords):
        draw.rectangle([x1, y1, x2, y2], fill="#0f1522", outline="#1e293b", width=1)
        draw.rectangle([x1, y1, x2, y1 + 5], fill=color)
        draw.text((x1 + 30, y1 + 30), title, fill="#f1f5f9", font=get_font(26, bold=True))
        
        import textwrap
        lines = textwrap.wrap(text, width=46)
        yt = y1 + 80
        for l in lines:
            draw.text((x1 + 30, yt), l, fill="#94a3b8", font=get_font(20, bold=False))
            yt += 32

    draw.text((140, 920), "Status: Verified local emulation mode active. Automatic s390x hardware detection implemented.", fill="#38bdf8", font=get_font(22, bold=True))
    img.save("graphics/04_ibm_z_graphic.png")
    print("Saved 04_ibm_z_graphic.png")

def create_outro_card():
    img = Image.new("RGB", (WIDTH, HEIGHT), color="#080b11")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 6], fill="#2563eb")
    draw.rectangle([80, 80, WIDTH - 80, HEIGHT - 80], outline="#1e293b", width=1)

    draw.text((WIDTH//2 - 340, 320), "SecureAgent AI", fill="#f1f5f9", font=get_font(76, bold=True))
    draw.text((WIDTH//2 - 400, 430), "AI Secured: Innovation Without Exposure", fill="#38bdf8", font=get_font(38, bold=True))

    draw.rectangle([WIDTH//2 - 250, 550, WIDTH//2 + 250, 610], fill="#111827", outline="#2563eb", width=1)
    draw.text((WIDTH//2 - 210, 565), "IBM Z DATATHON 2026 SUBMISSION", fill="#60a5fa", font=get_font(22, bold=True))

    draw.text((WIDTH//2 - 310, 720), "Repository: github.com/vijaymahes9080/IBM_datathon_project", fill="#94a3b8", font=get_font(22, bold=False))
    draw.text((WIDTH//2 - 220, 770), "Live Console: http://127.0.0.1:8000/", fill="#64748b", font=get_font(20, bold=False))

    draw.text((WIDTH//2 - 230, 920), "Empirical Security & Outer Perimeter Defense", fill="#10b981", font=get_font(22, bold=True))

    img.save("graphics/05_outro_card.png")
    img.save("../demo_video/thumbnail.png")
    print("Saved 05_outro_card.png and thumbnail.png")

if __name__ == "__main__":
    os.makedirs("graphics", exist_ok=True)
    create_title_card()
    create_problem_diagram()
    create_architecture_diagram()
    create_ibm_z_graphic()
    create_outro_card()
