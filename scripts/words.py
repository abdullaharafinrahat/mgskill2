#!/usr/bin/env python3
"""words.py — transcript + video duration → word timings beats.json"""
import json, argparse
from pathlib import Path

def build_beats(transcript_path, duration, fps=25):
    text=Path(transcript_path).read_text(encoding="utf-8")
    words=text.split()
    per = duration / max(1,len(words))
    beats=[]
    t=0
    for i,w in enumerate(words):
        beats.append({"i":i,"w":w,"t":round(t,3)})
        t+=per
    # also add sentence hits
    return {"duration":duration,"fps":fps,"words":beats,"perWord":per}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--transcript", required=True)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--out", default="output/beats.json")
    args=p.parse_args()
    data=build_beats(args.transcript, args.duration)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"beats: {len(data['words'])} words, {data['perWord']:.3f}s/word → {args.out}")
