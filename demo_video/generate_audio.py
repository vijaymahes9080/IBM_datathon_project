import asyncio
import os
import edge_tts
import imageio_ffmpeg
import subprocess

VOICE = "en-US-ChristopherNeural"

SCENES = {
    "scene1": {
        "text": (
            "In modern enterprises, generative AI agents are increasingly connected to databases and automated workflows. "
            "But large language models cannot reliably police themselves. "
            "When sensitive customer data enters prompt context, or an adversarial prompt overrides model instructions, internal guardrails fail. "
            "Enterprises cannot innovate with generative AI if it means risking confidential data exposure or unverified system actions."
        ),
        "target_duration": 28.0
    },
    "scene2": {
        "text": (
            "SecureAgent AI solves this by establishing a deterministic outer security perimeter around the language model. "
            "The model is treated as an untrusted reasoning component. "
            "Before any prompt reaches an adapter, Microsoft Presidio and enterprise recognizers scrub sensitive identifiers. "
            "An adversarial scanner intercepts injection attacks, while a deterministic policy engine enforces role-based clearance levels outside model context. "
            "High-risk actions require administrator sign-off, and every decision is permanently recorded in an unbroken, tamper-evident SHA-256 hash-chained ledger."
        ),
        "target_duration": 44.0
    },
    "scene3": {
        "text": (
            "Here is SecureAgent AI running live. First, we submit an inquiry with synthetic Social Security and payment card numbers. "
            "The gateway classifies the request as confidential and scrubs each identifier. "
            "The model only ever receives masked tokens. "
            "Next, an adversarial injection attempt. "
            "The threat engine catches the instruction override, assigning a threat score of 1.0, and the policy engine blocks it immediately. "
            "When a viewer attempts an unauthorized record lookup, server-side RBAC denies access. "
            "For high-risk operations, like exporting restricted data, execution pauses until an administrator approves the ticket. "
            "Finally, our evaluation lab runs sixteen live adversarial benchmarks, while our cryptographic audit trail verifies that the hash chain is mathematically intact."
        ),
        "target_duration": 58.0
    },
    "scene4": {
        "text": (
            "SecureAgent AI is architected for Linux on IBM Z and LinuxONE. "
            "In production, our adapter bridges directly to on-chip CPACF instructions for line-speed cryptography. "
            "Workloads execute inside IBM Secure Execution enclaves, shielding in-memory model context from host inspection, with full RACF identity federation. "
            "Tested locally in emulation mode, SecureAgent AI proves that enterprises can deploy generative AI with complete confidence: "
            "enabling genuine innovation, without ever exposing confidential data."
        ),
        "target_duration": 38.0
    }
}

async def generate():
    os.makedirs("audio", exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    durations = {}
    for key, data in SCENES.items():
        mp3_path = f"audio/{key}.mp3"
        wav_path = f"audio/{key}.wav"
        print(f"Generating voice for {key}...")
        comm = edge_tts.Communicate(data["text"], VOICE, rate="-2%")
        await comm.save(mp3_path)

        # Convert to WAV for exact timing analysis
        subprocess.run([ffmpeg_exe, "-y", "-i", mp3_path, wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Get duration using ffprobe via ffmpeg output
        probe_cmd = [ffmpeg_exe, "-i", wav_path]
        res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        # Parse Duration: 00:00:23.45
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
            durations[key] = round(dur, 2)
            print(f"  -> {key}: {durations[key]}s (Target: {data['target_duration']}s)")

    total_dur = sum(durations.values())
    print(f"\nTotal Spoken Duration: {total_dur}s (Target: ~168s, max 180s)")

if __name__ == "__main__":
    asyncio.run(generate())
