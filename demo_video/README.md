# SecureAgent AI — Video Demonstration Deliverables

**Submission**: IBM Z Datathon 2026 — *“AI Secured: Innovation Without Exposure”*  
**Deliverable File**: [`secureagent_ai_realistic_demo.mp4`](secureagent_ai_realistic_demo.mp4) (also copied to [`secureagent_ai_demo.mp4`](../secureagent_ai_demo.mp4))  
**Format**: MP4 (H.264 / AAC)  
**Resolution**: 1920x1080 (Full HD, 1080p @ 30 fps)  
**Duration**: 160.21 Seconds (2m 40s) — Strictly compliant with $\le 180$ seconds constraint  
**Audio**: High-clarity English neural narration (`en-US-ChristopherNeural`) with synchronized, beautifully styled burned subtitles  
**Production Technique**: Authentic live browser screen recordings via Playwright with realistic cursor trajectory, live input execution, and zero AI watermarks/labels.

---

## 1. Directory Structure

```
demo_video/
├── secureagent_ai_realistic_demo.mp4 # Master 1080p 30fps realistic video (< 180s, live screen capture)
├── narration_script.md               # Full transcript with timestamp markers and word counts
├── subtitles.srt                     # Accurate synchronized subtitle file
├── storyboard.md                     # Comprehensive scene-by-scene storyboard
├── thumbnail.png                     # 1920x1080 video thumbnail
├── record_all_scenes.py              # Automated live browser screen recorder (Playwright + Edge)
├── assemble_realistic_video.py       # Master FFmpeg assembly and subtitle burning script
├── live_recordings/                  # Captured high-fps webm browser sessions
│   ├── rec_overview/                 # Scene 2 Overview console walkthrough
│   ├── rec_demo/                     # Scene 3 AI Workspace, Policy, Eval Lab & Audit Log
│   └── rec_platform/                 # Scene 4 IBM Z Platform & CPACF view
├── audio/                            # Neural narration WAV clips (scenes 1-4)
├── graphics/                         # 1080p title and architecture diagram slides
└── output/                           # Final production MP4 renders
```

---

## 2. Storyboard & Scene Summary

| Scene | Duration | Timing | Visual & Demonstrative Content |
| :--- | :--- | :--- | :--- |
| **Scene 1: The Problem** | 29.35s | 0:00 – 0:29 | Opening title card & enterprise vulnerability diagram: why large language models cannot reliably police themselves when confidential customer data enters prompt context. |
| **Scene 2: Architecture & Overview** | 39.31s | 0:29 – 1:08 | 6-stage outer security boundary diagram (Presidio Redactor $\to$ Threat Scanner $\to$ RBAC $\to$ Safe Tools/HITL $\to$ SHA-256 Ledger), transitioning to a **live screen recording** of the Overview Dashboard highlighting live security metrics and active rules. |
| **Scene 3: Live Security Demonstration** | 55.39s | 1:08 – 2:04 | **Authentic continuous live screen recording** of the active web application:<br>• Preset 1: PII scrubbing & payload comparison (`<US_SSN>`, `<CREDIT_CARD>`)<br>• Preset 2: Adversarial prompt injection blocked immediately (threat score 1.00)<br>• Preset 3: Role switched to Viewer $\to$ server-side RBAC denies record lookup<br>• Preset 4: Role switched to Admin $\to$ Restricted export halted for Human-in-the-Loop review<br>• Policy View: Administrator approves the pending ticket live<br>• Evaluation Suite: Live execution of 16 security benchmarks with 100% pass score<br>• Audit Log: Live verification of cryptographic SHA-256 hash chain integrity |
| **Scene 4: IBM Z & Enterprise Impact** | 36.12s | 2:04 – 2:40 | **Live screen recording** of Platform & IBM Z settings view showing CPACF crypto status and Secure Execution enclave isolation, followed by IBM Z architecture blueprint and submission outro card. |

---

## 3. Technical Verification & FFprobe Metrics

You can verify the video resolution, duration, and codecs using the bundled FFprobe/FFmpeg:

```bash
..\venv\Scripts\python -c "import imageio_ffmpeg, subprocess; print(subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-i', 'secureagent_ai_realistic_demo.mp4'], stderr=subprocess.PIPE, text=True).stderr)"
```

### Verified Stream Attributes:
- **Duration**: `00:02:40.21` (160.21 seconds)
- **Video Stream**: H.264 (High Profile, `yuv420p`), $1920 \times 1080$, 30 fps, Progressive
- **Audio Stream**: AAC-LC, 44,100 Hz, Stereo, 192 kbps
- **Subtitles**: Burned in with Segoe UI font, readable dark stroke, optimal bottom margin
- **Container**: MP4 (`isom` / `mp41` / `avc1`)
