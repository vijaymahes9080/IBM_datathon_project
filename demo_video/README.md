# SecureAgent AI — Video Demonstration Deliverables

**Submission**: IBM Z Datathon 2026 — *“AI Secured: Innovation Without Exposure”*  
**Deliverable File**: [`SecureAgent_AI_Demo.mp4`](SecureAgent_AI_Demo.mp4)  
**Format**: MP4 (H.264 / AAC)  
**Resolution**: 1920x1080 (Full HD, 1080p @ 30 fps)  
**Duration**: 172.04 Seconds (2m 52s) — Strictly compliant with $\le 180$ seconds constraint  
**Audio**: High-clarity English neural narration (`en-US-ChristopherNeural`) with burned & synchronized subtitles  

---

## 1. Directory Structure

```
demo_video/
├── SecureAgent_AI_Demo.mp4      # Master 1080p 30fps video (< 180s, submission-ready)
├── narration_script.md          # Full transcript with timestamp markers and word counts
├── subtitles.srt                # Accurate synchronized subtitle file
├── storyboard.md                # Comprehensive scene-by-scene storyboard
├── thumbnail.png                # 1920x1080 video thumbnail
├── generate_audio.py            # Audio narration synthesis script
├── generate_graphics.py         # 1080p graphic slide generator
├── annotate_screens.py          # Screen capture annotation script
├── assemble_video.py            # Master FFmpeg assembly and subtitling script
├── audio/                       # Individual scene WAV and MP3 clips
├── graphics/                    # 1080p title and architecture diagram slides
├── raw_captures/                # Original live application 1080p screenshots
└── clips/                       # Segment video and audio renders
```

---

## 2. Storyboard & Scene Summary

| Scene | Duration | Timing | Focus & Content |
| :--- | :--- | :--- | :--- |
| **Scene 1: The Problem** | 31.0s | 0:00 – 0:31 | Title card & enterprise vulnerability gap: why LLMs cannot safely self-police internal access. |
| **Scene 2: Architecture** | 41.0s | 0:31 – 1:12 | 6-stage outer security boundary: Ingress $\to$ Presidio Redactor $\to$ Threat Scanner $\to$ RBAC $\to$ Safe Tools/HITL $\to$ SHA-256 Ledger. Cuts to live Overview console. |
| **Scene 3: Live Security Demonstration** | 58.0s | 1:12 – 2:10 | Genuine screen captures from running application: <br>• Preset A: PII scrubbing & payload isolation (`<US_SSN>`, `<CREDIT_CARD>`)<br>• Preset C: Prompt injection blocked (threat score 1.00)<br>• Preset D: Viewer role denied customer lookup<br>• Preset F: Restricted export halted for administrator sign-off<br>• Approvals Console: Administrator approves ticket<br>• Evaluation Suite: 16 live benchmarks executed<br>• Audit View: Unbroken SHA-256 hash chain verified mathematically |
| **Scene 4: IBM Z & Impact** | 42.0s | 2:10 – 2:52 | Linux on IBM Z / LinuxONE deployment path: CPACF hardware crypto (`KM`/`KMC`), IBM Secure Execution Ultravisor memory isolation, and RACF identity mapping. Closes on submission outro. |

---

## 3. Technical Verification & FFprobe Metrics

You can verify the video resolution, duration, and codecs using the bundled FFprobe/FFmpeg:

```bash
# Verify video duration and streams
..\venv\Scripts\python -c "import imageio_ffmpeg, subprocess; print(subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-i', 'SecureAgent_AI_Demo.mp4'], stderr=subprocess.PIPE, text=True).stderr)"
```

### Verified Stream Attributes:
- **Duration**: `00:02:52.04` (172.04 seconds)
- **Video Stream**: H.264 (High Profile, `yuv420p`), $1920 \times 1080$, 30 fps, Progressive
- **Audio Stream**: AAC-LC, 24,000 Hz, Mono, 95 kbps
- **Container**: MP4 (`isom` / `mp41` / `avc1`) with `faststart` enabled for instant streaming

---

## 4. Manual Upload & Presentation Instructions

1. **Submission Portal**: Upload [`SecureAgent_AI_Demo.mp4`](SecureAgent_AI_Demo.mp4) directly to the Datathon review portal or attach via GitHub release.
2. **YouTube / Vimeo (if required)**:
   - Title: `SecureAgent AI — AI Secured: Innovation Without Exposure (IBM Z Datathon 2026)`
   - Description: Include link to repository [https://github.com/vijaymahes9080/IBM_datathon_project](https://github.com/vijaymahes9080/IBM_datathon_project)
   - Closed Captions: Upload [`subtitles.srt`](subtitles.srt) for optional native player captions.
   - Thumbnail: Use [`thumbnail.png`](thumbnail.png).
