import os
import glob
import subprocess

FFMPEG_EXE = r"d:\current project\IBM\venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
DEMO_DIR = r"d:\current project\IBM\demo_video"
AUDIO_DIR = os.path.join(DEMO_DIR, "audio")
GRAPHICS_DIR = os.path.join(DEMO_DIR, "graphics")
LIVE_DIR = os.path.join(DEMO_DIR, "live_recordings")
OUTPUT_DIR = os.path.join(DEMO_DIR, "output")
SUBTITLES_SRT = os.path.join(DEMO_DIR, "subtitles.srt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_media_duration(file_path):
    cmd = [
        FFMPEG_EXE, "-i", file_path,
        "-hide_banner"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 0.0

def find_latest_recording(folder):
    files = glob.glob(os.path.join(folder, "*.webm"))
    if not files:
        raise FileNotFoundError(f"No .webm file found in {folder}")
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def make_scene1():
    """Scene 1: Title Card (7s) + Problem Diagram (22.35s) + audio/scene1.wav (29.35s)"""
    audio_file = os.path.join(AUDIO_DIR, "scene1.wav")
    a_dur = get_media_duration(audio_file)
    print(f"Scene 1 audio duration: {a_dur:.2f}s")
    
    t_card = 7.0
    t_prob = a_dur - t_card
    
    out_mp4 = os.path.join(OUTPUT_DIR, "scene1_cut.mp4")
    card_img = os.path.join(GRAPHICS_DIR, "01_title_card.png").replace("\\", "/")
    prob_img = os.path.join(GRAPHICS_DIR, "02_problem_diagram.png").replace("\\", "/")
    
    filt = (
        f"[0:v]loop=loop=-1:size=1:start=0,scale=1920:1080,fps=30,trim=duration={t_card},setpts=PTS-STARTPTS[v0]; "
        f"[1:v]loop=loop=-1:size=1:start=0,scale=1920:1080,fps=30,trim=duration={t_prob},setpts=PTS-STARTPTS[v1]; "
        f"[v0][v1]concat=n=2:v=1:a=0[vout]"
    )
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", card_img,
        "-i", prob_img,
        "-i", audio_file,
        "-filter_complex", filt,
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", str(a_dur),
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Scene 1 generated: {out_mp4}")
    return out_mp4

def make_scene2():
    """Scene 2: Architecture Diagram (21s) + Live Overview Recording (18.31s) + audio/scene2.wav (39.31s)"""
    audio_file = os.path.join(AUDIO_DIR, "scene2.wav")
    a_dur = get_media_duration(audio_file)
    print(f"Scene 2 audio duration: {a_dur:.2f}s")
    
    arch_img = os.path.join(GRAPHICS_DIR, "03_architecture_diagram.png").replace("\\", "/")
    rec_webm = find_latest_recording(os.path.join(LIVE_DIR, "rec_overview")).replace("\\", "/")
    
    t_arch = 21.0
    t_live = a_dur - t_arch
    
    out_mp4 = os.path.join(OUTPUT_DIR, "scene2_cut.mp4")
    
    filt = (
        f"[0:v]loop=loop=-1:size=1:start=0,scale=1920:1080,fps=30,trim=duration={t_arch},setpts=PTS-STARTPTS[v0]; "
        f"[1:v]scale=1920:1080,fps=30,trim=duration={t_live},setpts=PTS-STARTPTS[v1]; "
        f"[v0][v1]concat=n=2:v=1:a=0[vout]"
    )
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", arch_img,
        "-i", rec_webm,
        "-i", audio_file,
        "-filter_complex", filt,
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", str(a_dur),
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Scene 2 generated: {out_mp4}")
    return out_mp4

def make_scene3():
    """Scene 3: Full Live Recorded Security Demo + audio/scene3.wav (55.39s)"""
    audio_file = os.path.join(AUDIO_DIR, "scene3.wav")
    a_dur = get_media_duration(audio_file)
    print(f"Scene 3 audio duration: {a_dur:.2f}s")
    
    rec_webm = find_latest_recording(os.path.join(LIVE_DIR, "rec_demo")).replace("\\", "/")
    webm_dur = get_media_duration(rec_webm)
    print(f"Live demo raw recording duration: {webm_dur:.2f}s")
    
    out_mp4 = os.path.join(OUTPUT_DIR, "scene3_cut.mp4")
    
    # Scale video duration smoothly to match audio duration exactly
    pts_factor = a_dur / webm_dur if webm_dur > 0 else 1.0
    filt = f"[0:v]setpts={pts_factor}*PTS,scale=1920:1080,fps=30[vout]"
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", rec_webm,
        "-i", audio_file,
        "-filter_complex", filt,
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", str(a_dur),
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Scene 3 generated: {out_mp4}")
    return out_mp4

def make_scene4():
    """Scene 4: Live Platform recording (16s) + IBM Z graphic (14s) + Outro (6.12s) + audio/scene4.wav (36.12s)"""
    audio_file = os.path.join(AUDIO_DIR, "scene4.wav")
    a_dur = get_media_duration(audio_file)
    print(f"Scene 4 audio duration: {a_dur:.2f}s")
    
    rec_webm = find_latest_recording(os.path.join(LIVE_DIR, "rec_platform")).replace("\\", "/")
    ibm_img = os.path.join(GRAPHICS_DIR, "04_ibm_z_graphic.png").replace("\\", "/")
    outro_img = os.path.join(GRAPHICS_DIR, "05_outro_card.png").replace("\\", "/")
    
    t_live = 16.0
    t_ibm = 14.0
    t_outro = a_dur - (t_live + t_ibm)
    
    out_mp4 = os.path.join(OUTPUT_DIR, "scene4_cut.mp4")
    
    filt = (
        f"[0:v]scale=1920:1080,fps=30,trim=duration={t_live},setpts=PTS-STARTPTS[v0]; "
        f"[1:v]loop=loop=-1:size=1:start=0,scale=1920:1080,fps=30,trim=duration={t_ibm},setpts=PTS-STARTPTS[v1]; "
        f"[2:v]loop=loop=-1:size=1:start=0,scale=1920:1080,fps=30,trim=duration={t_outro},setpts=PTS-STARTPTS[v2]; "
        f"[v0][v1][v2]concat=n=3:v=1:a=0[vout]"
    )
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", rec_webm,
        "-i", ibm_img,
        "-i", outro_img,
        "-i", audio_file,
        "-filter_complex", filt,
        "-map", "[vout]",
        "-map", "3:a",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", str(a_dur),
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Scene 4 generated: {out_mp4}")
    return out_mp4

def assemble_master(s1, s2, s3, s4):
    final_mp4 = os.path.join(OUTPUT_DIR, "secureagent_ai_realistic_demo.mp4")
    srt_escaped = SUBTITLES_SRT.replace("\\", "/").replace(":", "\\:")
    sub_style = "FontSize=17,FontName=Segoe UI,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BackColour=&H60000000,BorderStyle=4,Outline=1,Shadow=0,MarginV=140,Alignment=2"

    filt = (
        "[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a]concat=n=4:v=1:a=1[vcat][acat]; "
        f"[vcat]subtitles='{srt_escaped}':force_style='{sub_style}'[vout]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", s1,
        "-i", s2,
        "-i", s3,
        "-i", s4,
        "-filter_complex", filt,
        "-map", "[vout]",
        "-map", "[acat]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        final_mp4
    ]
    subprocess.run(cmd, check=True)
    
    dur = get_media_duration(final_mp4)
    size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"\n==========================================")
    print(f"MASTER REALISTIC VIDEO PRODUCED SUCCESSFULLY!")
    print(f"Output: {final_mp4}")
    print(f"Duration: {dur:.2f} seconds ({dur/60:.2f} minutes)")
    print(f"File Size: {size_mb:.2f} MB")
    print(f"==========================================\n")
    return final_mp4

if __name__ == "__main__":
    s1 = make_scene1()
    s2 = make_scene2()
    s3 = make_scene3()
    s4 = make_scene4()
    master = assemble_master(s1, s2, s3, s4)
