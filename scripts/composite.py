#!/usr/bin/env python3
"""composite.py — ffmpeg mux clips + voice + music + SFX → final.mp4
Real compositing is done via ffmpeg; this validates inputs and prints command.
"""
import json, argparse, subprocess
from pathlib import Path

def get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except: return "ffmpeg"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--clipsDir", default="output/clips")
    p.add_argument("--voice", default="output/voice.mp3")
    p.add_argument("--out", default="output/final.mp4")
    args=p.parse_args()
    clips=sorted(Path(args.clipsDir).glob("*.mp4")) if Path(args.clipsDir).exists() else []
    print(f"Clips found: {len(clips)}")
    for c in clips: print(f"  {c.name}")
    if Path(args.voice).exists(): print(f"Voice: {args.voice}")
    else: print(f"Voice missing (will render silent, check TTS)")
    # Build example ffmpeg concat
    ff=get_ffmpeg()
    print(f"\nExample concat (agent will run):")
    print(f"  {ff} -f concat -safe 0 -i <clips_list.txt> -i {args.voice} -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k {args.out}")
    # Write placeholder
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path("output/TIMING.md").write_text("# TIMING\n\nAuto-generated. See beats.json for word-level timings.\n")
    print("Wrote output/TIMING.md")
