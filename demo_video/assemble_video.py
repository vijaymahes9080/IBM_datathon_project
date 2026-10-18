import os
import sys
import subprocess
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def run_cmd(cmd, desc=""):
    if desc:
        print(f"--> {desc}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:\n{res.stderr[-1000:]}")
        sys.exit(1)
    return res

def build_scene(scene_id, shots, audio_file, pre_delay, total_dur):
    """
    shots: list of (image_path, duration)
    total_dur: total duration for this scene
    """
    print(f"\nBuilding {scene_id} (Total: {total_dur}s)...")
    
    # 1. Create video track by concatenating image stills
    shot_files = []
    concat_list = f"clips/{scene_id}_shots.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for idx, (img_path, dur) in enumerate(shots):
            shot_mp4 = f"clips/{scene_id}_shot_{idx}.mp4"
            # Encode still image to 30fps 1080p video segment
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", img_path,
                "-t", str(dur),
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                shot_mp4
            ]
            run_cmd(cmd, f"Encoding {scene_id} shot {idx} ({dur}s)")
            shot_files.append(shot_mp4)
            # Write absolute path for concat demuxer
            abs_p = os.path.abspath(shot_mp4).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    # Concat video shots
    video_only = f"clips/{scene_id}_video.mp4"
    run_cmd([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        video_only
    ], f"Concatenating video shots for {scene_id}")

    # 2. Build timed audio track: silence pre_delay + audio_file + pad to total_dur
    scene_audio = f"clips/{scene_id}_audio.wav"
    # Filter complex to delay audio and pad with silence to total_dur
    delay_ms = int(pre_delay * 1000)
    afilt = f"adelay={delay_ms}|{delay_ms},apad=pad_dur={total_dur}"
    run_cmd([
        FFMPEG, "-y",
        "-i", audio_file,
        "-af", afilt,
        "-t", str(total_dur),
        scene_audio
    ], f"Timing audio for {scene_id}")

    # 3. Merge video and audio for this scene
    scene_out = f"clips/{scene_id}_final.mp4"
    run_cmd([
        FFMPEG, "-y",
        "-i", video_only,
        "-i", scene_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        scene_out
    ], f"Muxing {scene_id} segment")

    return scene_out

def assemble_all():
    os.makedirs("clips", exist_ok=True)

    # Scene 1: The Problem (31.0s)
    # Audio duration: 29.35s
    s1 = build_scene(
        "scene1",
        [
            ("graphics/01_title_card.png", 8.0),
            ("graphics/02_problem_diagram.png", 23.0)
        ],
        "audio/scene1.wav",
        pre_delay=1.2,
        total_dur=31.0
    )

    # Scene 2: How It Works - Architecture (41.0s)
    # Audio duration: 39.31s
    s2 = build_scene(
        "scene2",
        [
            ("graphics/03_architecture_diagram.png", 23.0),
            ("clips/screen_overview.png", 18.0)
        ],
        "audio/scene2.wav",
        pre_delay=0.8,
        total_dur=41.0
    )

    # Scene 3: Live Security Demonstration (58.0s)
    # Audio duration: 55.39s
    s3 = build_scene(
        "scene3",
        [
            ("clips/screen_pii_masking.png", 9.5),
            ("clips/screen_prompt_injection.png", 10.0),
            ("clips/screen_hitl_ticket.png", 9.5),
            ("clips/screen_policy_approved.png", 9.5),
            ("clips/screen_evaluation.png", 10.0),
            ("clips/screen_audit_verify.png", 9.5)
        ],
        "audio/scene3.wav",
        pre_delay=0.8,
        total_dur=58.0
    )

    # Scene 4: IBM Z & Impact (42.0s)
    # Audio duration: 36.12s
    s4 = build_scene(
        "scene4",
        [
            ("clips/screen_platform.png", 14.0),
            ("graphics/04_ibm_z_graphic.png", 18.0),
            ("graphics/05_outro_card.png", 10.0)
        ],
        "audio/scene4.wav",
        pre_delay=0.8,
        total_dur=42.0
    )

    # Concat all 4 scenes
    scenes = [s1, s2, s3, s4]
    concat_list = "clips/master_scenes.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for sc in scenes:
            abs_p = os.path.abspath(sc).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    unsubbed_mp4 = "clips/master_unsubbed.mp4"
    run_cmd([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        unsubbed_mp4
    ], "Merging all scenes into Master Video")

    # Burn subtitles and embed SRT track into final submission MP4
    srt_file = os.path.abspath("subtitles.srt").replace("\\", "/")
    # Escape path for ffmpeg subtitles filter (escape colon and backslash)
    srt_escaped = srt_file.replace(":", "\\:").replace("'", "\\'")

    # Subtitle style: clean Arial, size 16, crisp outline and shadow, positioned cleanly above lower-third callout
    sub_style = "Fontname=Arial,Fontsize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=3,Outline=1.5,Shadow=1,MarginV=145"
    sub_filter = f"subtitles='{srt_escaped}':force_style='{sub_style}'"

    final_mp4 = "SecureAgent_AI_Demo.mp4"
    print("\nRendering final submission video with burned subtitles...")
    run_cmd([
        FFMPEG, "-y",
        "-i", unsubbed_mp4,
        "-vf", sub_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        final_mp4
    ], "Rendering final MP4 with subtitles")

    # Probe final output
    probe_cmd = [FFMPEG, "-i", final_mp4]
    res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    import re
    m_dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    m_res = re.search(r"Stream.*Video:.*,\s*(\d+x\d+)", res.stderr)

    print("\n==================================================================")
    print("FINAL DELIVERABLE VERIFICATION:")
    if m_dur:
        dur_s = int(m_dur.group(1))*3600 + int(m_dur.group(2))*60 + float(m_dur.group(3))
        print(f"  Duration  : {dur_s} seconds (Target: <= 180s)")
        assert dur_s <= 180.0, f"Error: Video duration {dur_s} exceeds 180 seconds!"
    if m_res:
        print(f"  Resolution: {m_res.group(1)} (Full HD 1080p)")
    print(f"  File Path : {os.path.abspath(final_mp4)}")
    print(f"  File Size : {os.path.getsize(final_mp4) / (1024*1024):.2f} MB")
    print("==================================================================\n")

if __name__ == "__main__":
    assemble_all()
