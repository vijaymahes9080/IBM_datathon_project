import os
import time
import math
from playwright.sync_api import sync_playwright

def get_center(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

def human_mouse_move(page, start_x, start_y, end_x, end_y, steps=25):
    """Move mouse along a smooth natural curved path with gentle easing."""
    for i in range(1, steps + 1):
        t = i / steps
        ease = 0.5 - 0.5 * math.cos(t * math.pi)
        curve = math.sin(t * math.pi) * 12
        cx = start_x + (end_x - start_x) * ease + curve * 0.15
        cy = start_y + (end_y - start_y) * ease - curve * 0.35
        page.mouse.move(cx, cy)
        time.sleep(0.012)
    return end_x, end_y

def inject_cursor(page):
    page.add_init_script("""
        window.addEventListener('DOMContentLoaded', () => {
            const cursor = document.createElement('div');
            cursor.id = 'demo-cursor';
            cursor.style.position = 'fixed';
            cursor.style.top = '0';
            cursor.style.left = '0';
            cursor.style.width = '24px';
            cursor.style.height = '24px';
            cursor.style.borderRadius = '50%';
            cursor.style.border = '2.5px solid #38bdf8';
            cursor.style.backgroundColor = 'rgba(56, 189, 248, 0.32)';
            cursor.style.boxShadow = '0 0 16px rgba(56, 189, 248, 0.6)';
            cursor.style.pointerEvents = 'none';
            cursor.style.zIndex = '999999';
            cursor.style.transform = 'translate(-50%, -50%)';
            cursor.style.transition = 'transform 0.05s ease, width 0.1s ease, height 0.1s ease, background-color 0.12s ease';
            document.body.appendChild(cursor);

            window.addEventListener('mousemove', (e) => {
                cursor.style.left = e.clientX + 'px';
                cursor.style.top = e.clientY + 'px';
            });

            window.addEventListener('mousedown', () => {
                cursor.style.width = '18px';
                cursor.style.height = '18px';
                cursor.style.backgroundColor = 'rgba(16, 185, 129, 0.85)';
                cursor.style.borderColor = '#34d399';
            });

            window.addEventListener('mouseup', () => {
                cursor.style.width = '24px';
                cursor.style.height = '24px';
                cursor.style.backgroundColor = 'rgba(56, 189, 248, 0.32)';
                cursor.style.borderColor = '#38bdf8';
            });
        });
    """)

def record_overview_scene(playwright, output_dir):
    """Record Scene 2 Overview Dashboard (~18.5 seconds)"""
    print("\n==============================================")
    print("Recording Scene 2: Live Overview Dashboard...")
    print("==============================================")
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    rec_dir = os.path.join(output_dir, "rec_overview")
    os.makedirs(rec_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=rec_dir,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    inject_cursor(page)
    
    page.goto("http://127.0.0.1:8000/")
    page.wait_for_load_state("networkidle")
    time.sleep(1.5)
    
    cur_x, cur_y = 960, 450
    page.mouse.move(cur_x, cur_y)
    time.sleep(0.5)
    
    # 1. Hover across System Metric Cards
    cards = page.locator(".metric-card").all()
    for card in cards[:4]:
        box = card.bounding_box()
        if box:
            tx, ty = get_center(box)
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, tx, ty, steps=25)
            time.sleep(1.0)
            
    # 2. Hover over IBM Z Adapter Posture card
    elem = page.locator(".card:has-text('IBM Z Adapter Posture')").first
    if elem.count() > 0:
        box = elem.bounding_box()
        if box:
            tx, ty = get_center(box)
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, tx, ty, steps=25)
            time.sleep(2.0)
            
    # 3. Hover over Active Security Guardrails card
    elem2 = page.locator(".card:has-text('Active Security Guardrails')").first
    if elem2.count() > 0:
        box = elem2.bounding_box()
        if box:
            tx, ty = get_center(box)
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, tx, ty, steps=25)
            time.sleep(2.2)
            
    # 4. Hover over Recent Gateway Activity
    elem3 = page.locator(".card:has-text('Recent Gateway Activity')").first
    if elem3.count() > 0:
        box = elem3.bounding_box()
        if box:
            tx, ty = get_center(box)
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, tx, ty, steps=25)
            time.sleep(2.5)
            
    time.sleep(2.0)
    video_path = page.video.path()
    context.close()
    browser.close()
    print(f"Overview scene recorded to: {video_path}")
    return video_path

def record_workspace_demo_scene(playwright, output_dir):
    """Record Scene 3 Live Security Demonstration (~56 seconds)"""
    print("\n==============================================")
    print("Recording Scene 3: Live Security Demonstration...")
    print("==============================================")
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    rec_dir = os.path.join(output_dir, "rec_demo")
    os.makedirs(rec_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=rec_dir,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    inject_cursor(page)
    
    page.goto("http://127.0.0.1:8000/")
    page.wait_for_load_state("networkidle")
    time.sleep(1.0)
    
    cur_x, cur_y = 120, 220
    page.mouse.move(cur_x, cur_y)
    
    # 1. Navigate to AI Workspace
    print("Step 1: Navigating to AI Workspace...")
    btn = page.locator("button:has-text('AI Workspace')").first
    box = btn.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(1.2)
    
    # PII Masking Preset
    print("Step 2: Triggering PII Masking Preset...")
    btn_pii = page.locator("button:has-text('PII Masking')").first
    box = btn_pii.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(0.8)
    
    # Click Send Request
    btn_send = page.locator("button:has-text('Send Request')").first
    box = btn_send.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(2.5)
    
    # Compare Raw vs Redacted
    print("Step 3: Toggle Compare Raw vs Redacted...")
    btn_cmp = page.locator("button:has-text('Compare Raw vs Redacted')").first
    if btn_cmp.count() > 0:
        box = btn_cmp.bounding_box()
        cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
        page.mouse.click(cur_x, cur_y)
        time.sleep(3.5)
        
    # 2. Prompt Injection Demo
    print("Step 4: Triggering Prompt Injection Attack...")
    btn_inj = page.locator("button:has-text('Prompt Injection')").first
    box = btn_inj.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(0.8)
    
    btn_send = page.locator("button:has-text('Send Request')").first
    box = btn_send.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(3.5)
    
    # 3. RBAC Viewer Block & Admin HITL Approval
    print("Step 5: Role switch to Viewer...")
    sel = page.locator("select.role-select").first
    box = sel.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.select_option("select.role-select", "viewer")
    time.sleep(1.0)
    
    btn_unauth = page.locator("button:has-text('Unauthorized Tool')").first
    box = btn_unauth.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(0.5)
    
    btn_send = page.locator("button:has-text('Send Request')").first
    box = btn_send.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(2.5)
    
    print("Step 6: Role switch to Admin & Restricted Export...")
    sel = page.locator("select.role-select").first
    box = sel.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.select_option("select.role-select", "admin")
    time.sleep(1.0)
    
    btn_hitl = page.locator("button:has-text('Restricted Export (HITL)')").first
    box = btn_hitl.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(0.5)
    
    btn_send = page.locator("button:has-text('Send Request')").first
    box = btn_send.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(2.5)
    
    # 4. Policy Management: Approve HITL
    print("Step 7: Policy Management Approval...")
    btn_pol = page.locator("button:has-text('Policy Management')").first
    box = btn_pol.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(1.5)
    
    btn_appr = page.locator("button:has-text('Approve')").first
    if btn_appr.count() > 0:
        box = btn_appr.bounding_box()
        cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
        page.mouse.click(cur_x, cur_y)
        time.sleep(3.0)
        
    # 5. Evaluation Lab
    print("Step 8: Evaluation Suite...")
    btn_eval = page.locator("button:has-text('Evaluation Suite')").first
    box = btn_eval.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(1.2)
    
    btn_run = page.locator("button:has-text('Run Benchmark Suite')").first
    box = btn_run.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=20)
    page.mouse.click(cur_x, cur_y)
    time.sleep(3.5)
    
    # 6. Audit Log: Verify Hash Chain
    print("Step 9: Audit Log & Cryptographic Verification...")
    btn_aud = page.locator("button:has-text('Audit Log')").first
    box = btn_aud.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(1.2)
    
    btn_v = page.locator("button:has-text('Verify Hash Chain')").first
    box = btn_v.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(3.0)
    
    video_path = page.video.path()
    context.close()
    browser.close()
    print(f"Workspace demo scene recorded to: {video_path}")
    return video_path

def record_platform_scene(playwright, output_dir):
    """Record Scene 4 Platform & IBM Z View (~16.0 seconds)"""
    print("\n==============================================")
    print("Recording Scene 4: Platform & IBM Z View...")
    print("==============================================")
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    rec_dir = os.path.join(output_dir, "rec_platform")
    os.makedirs(rec_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=rec_dir,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    inject_cursor(page)
    
    page.goto("http://127.0.0.1:8000/")
    page.wait_for_load_state("networkidle")
    time.sleep(1.0)
    
    cur_x, cur_y = 120, 480
    page.mouse.move(cur_x, cur_y)
    
    btn = page.locator("button:has-text('Platform & IBM Z')").first
    box = btn.bounding_box()
    cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
    page.mouse.click(cur_x, cur_y)
    time.sleep(2.0)
    
    # Hover over CPACF Crypto card
    cpacf = page.locator("div:has-text('CPACF Crypto')").last
    if cpacf.count() > 0:
        box = cpacf.bounding_box()
        if box:
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
            time.sleep(3.0)
            
    # Hover over Secure Execution Enclave card
    enclave = page.locator("div:has-text('Secure Execution Enclave')").last
    if enclave.count() > 0:
        box = enclave.bounding_box()
        if box:
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
            time.sleep(3.0)
            
    # Hover over Enterprise Partition Data Store
    store = page.locator(".card-title:has-text('Enterprise Partition Data Store')").first
    if store.count() > 0:
        box = store.bounding_box()
        if box:
            cur_x, cur_y = human_mouse_move(page, cur_x, cur_y, box["x"]+box["width"]/2, box["y"]+box["height"]/2, steps=25)
            time.sleep(2.5)
            
    time.sleep(2.0)
    video_path = page.video.path()
    context.close()
    browser.close()
    print(f"Platform scene recorded to: {video_path}")
    return video_path

if __name__ == "__main__":
    out_dir = "d:/current project/IBM/demo_video/live_recordings"
    os.makedirs(out_dir, exist_ok=True)
    with sync_playwright() as p:
        v_overview = record_overview_scene(p, out_dir)
        v_demo = record_workspace_demo_scene(p, out_dir)
        v_platform = record_platform_scene(p, out_dir)
        print("\n==============================================")
        print("All 3 live browser scenes recorded successfully!")
        print("==============================================")
