import os
import time
from playwright.sync_api import sync_playwright

def smooth_move(page, target_selector, steps=25, delay=0.015):
    """Smoothly move mouse to the center of target element."""
    elem = page.locator(target_selector).first
    box = elem.bounding_box()
    if box:
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        page.mouse.move(target_x, target_y, steps=steps)
        time.sleep(delay)
        return box
    return None

def record():
    os.makedirs("demo_video/live_recordings", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="demo_video/live_recordings",
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Inject visible cursor highlighter for realistic presentation feel
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
                cursor.style.backgroundColor = 'rgba(56, 189, 248, 0.35)';
                cursor.style.boxShadow = '0 0 12px rgba(56, 189, 248, 0.6)';
                cursor.style.pointerEvents = 'none';
                cursor.style.zIndex = '999999';
                cursor.style.transform = 'translate(-50%, -50%)';
                cursor.style.transition = 'transform 0.08s ease, width 0.1s ease, height 0.1s ease, background-color 0.1s ease';
                document.body.appendChild(cursor);

                window.addEventListener('mousemove', (e) => {
                    cursor.style.left = e.clientX + 'px';
                    cursor.style.top = e.clientY + 'px';
                });

                window.addEventListener('mousedown', () => {
                    cursor.style.width = '18px';
                    cursor.style.height = '18px';
                    cursor.style.backgroundColor = 'rgba(16, 185, 129, 0.8)';
                    cursor.style.borderColor = '#34d399';
                });

                window.addEventListener('mouseup', () => {
                    cursor.style.width = '24px';
                    cursor.style.height = '24px';
                    cursor.style.backgroundColor = 'rgba(56, 189, 248, 0.35)';
                    cursor.style.borderColor = '#38bdf8';
                });
            });
        """)

        print("Navigating to http://127.0.0.1:8000/ ...")
        page.goto("http://127.0.0.1:8000/")
        page.wait_for_load_state("networkidle")
        time.sleep(2.0)

        # ---------------------------------------------------------------------
        # Part 1: Navigate to AI Workspace & PII Redaction Demo (12 seconds)
        # ---------------------------------------------------------------------
        print("Navigating to AI Workspace...")
        smooth_move(page, "button:has-text('AI Workspace')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('AI Workspace')")
        time.sleep(1.5)

        print("Clicking PII Masking Preset...")
        smooth_move(page, "button:has-text('PII Masking')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('PII Masking')")
        time.sleep(1.0)

        print("Sending PII Request...")
        smooth_move(page, "button:has-text('Send Request')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Send Request')")
        time.sleep(2.5)

        # Toggle raw vs redacted comparison
        print("Toggling Raw vs Redacted...")
        if page.locator("button:has-text('Compare Raw vs Redacted')").count() > 0:
            smooth_move(page, "button:has-text('Compare Raw vs Redacted')", steps=20)
            time.sleep(0.3)
            page.click("button:has-text('Compare Raw vs Redacted')")
            time.sleep(3.5)

        # ---------------------------------------------------------------------
        # Part 2: Prompt Injection Demo (11 seconds)
        # ---------------------------------------------------------------------
        print("Clicking Prompt Injection Preset...")
        smooth_move(page, "button:has-text('Prompt Injection')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Prompt Injection')")
        time.sleep(1.0)

        print("Sending Injection Request...")
        smooth_move(page, "button:has-text('Send Request')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Send Request')")
        time.sleep(3.5)

        # ---------------------------------------------------------------------
        # Part 3: RBAC Viewer Block & Admin HITL Approval Ticket (13 seconds)
        # ---------------------------------------------------------------------
        print("Switching Role to Viewer...")
        smooth_move(page, "select.role-select", steps=20)
        time.sleep(0.3)
        page.select_option("select.role-select", "viewer")
        time.sleep(1.0)

        print("Attempting Unauthorized Tool lookup as Viewer...")
        smooth_move(page, "button:has-text('Unauthorized Tool')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Unauthorized Tool')")
        time.sleep(0.5)

        smooth_move(page, "button:has-text('Send Request')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Send Request')")
        time.sleep(2.5)

        print("Switching Role to Administrator...")
        smooth_move(page, "select.role-select", steps=20)
        time.sleep(0.3)
        page.select_option("select.role-select", "admin")
        time.sleep(1.0)

        print("Triggering Restricted Export (HITL)...")
        smooth_move(page, "button:has-text('Restricted Export (HITL)')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Restricted Export (HITL)')")
        time.sleep(0.5)

        smooth_move(page, "button:has-text('Send Request')", steps=20)
        time.sleep(0.3)
        page.click("button:has-text('Send Request')")
        time.sleep(2.5)

        # ---------------------------------------------------------------------
        # Part 4: Policy & Approvals Dashboard (11 seconds)
        # ---------------------------------------------------------------------
        print("Navigating to Policy Management...")
        smooth_move(page, "button:has-text('Policy Management')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Policy Management')")
        time.sleep(1.5)

        # Locate approve button
        if page.locator("button:has-text('Approve Execution')").count() > 0:
            print("Approving Pending Action...")
            smooth_move(page, "button:has-text('Approve Execution')", steps=25)
            time.sleep(0.5)
            page.click("button:has-text('Approve Execution')")
            time.sleep(3.0)

        # ---------------------------------------------------------------------
        # Part 5: Evaluation Lab & Cryptographic Audit Verification (11 seconds)
        # ---------------------------------------------------------------------
        print("Navigating to Evaluation Suite...")
        smooth_move(page, "button:has-text('Evaluation Suite')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Evaluation Suite')")
        time.sleep(1.5)

        print("Running Full Benchmark Suite Live...")
        smooth_move(page, "button:has-text('Run Benchmark Suite')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Run Benchmark Suite')")
        time.sleep(3.5)

        print("Navigating to Audit Log...")
        smooth_move(page, "button:has-text('Audit Log')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Audit Log')")
        time.sleep(1.5)

        print("Verifying Cryptographic Integrity...")
        smooth_move(page, "button:has-text('Verify Cryptographic Integrity')", steps=25)
        time.sleep(0.3)
        page.click("button:has-text('Verify Cryptographic Integrity')")
        time.sleep(3.0)

        # End recording
        time.sleep(1.0)
        video_path = page.video.path()
        context.close()
        browser.close()
        print(f"\nLive Screen Recording Complete! Saved to: {video_path}")

if __name__ == "__main__":
    record()
