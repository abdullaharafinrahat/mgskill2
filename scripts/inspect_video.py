#!/usr/bin/env python3
"""inspect_video.py — probe input video for motion-broll-pro"""
import subprocess, json, argparse, pathlib
from pathlib import Path

def get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except: return "ffmpeg"

def inspect(in_path):
    ff = get_ffmpeg()
    cmd = [ff, "-i", in_path, "-f", "null", "-"]
    # Use ffprobe via ffmpeg stderr
    import os
    # Simple: use imageio-ffmpeg probe via python cv logic fallback
    # We'll use ffprobe if exists else parse via ffmpeg output
    # For now just try to get via ffmpeg -i stderr
    import subprocess
    r = subprocess.run([ff, "-i", in_path], capture_output=True, text=True)
    out = r.stderr
    # parse WxH, fps, duration crudely
    import re
    m = re.search(r"(\d+)x(\d+).*?(\d+(?:\.\d+)?) fps", out)
    m2 = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    W=H=0; fps=25; dur=0
    if m: W=int(m.group(1)); H=int(m.group(2)); fps=float(m.group(3))
    if m2: dur=int(m2.group(1))*3600+int(m2.group(2))*60+float(m2.group(3))
    return {"W":W,"H":H,"fps":fps,"duration":dur,"raw":out[:800]}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", default="output/inspect.json")
    args=p.parse_args()
    info=inspect(args.inp)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2))
