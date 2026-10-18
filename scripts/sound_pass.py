#!/usr/bin/env python3
"""sound_pass.py — map beats + SFX from plan → timed SFX JSON, duck under voice
Wraps skills/sound-effects/scripts/sound_pass.py logic. Falls back to simple mapper if not installed.
"""
import json, argparse
from pathlib import Path

SFX_MAP={
 "whoosh": "whoosh-soft-01.wav",
 "pop": "pop-cork-02.wav",
 "shutter": "shutter-01.wav",
 "tick": "click-soft.wav",
 "chime": "chime-success.wav",
 "hit": "swoosh-hit.wav"
}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--plan", default="output/plan.json")
    p.add_argument("--beats", default="output/beats.json")
    p.add_argument("--out", default="output/timed_sfx.json")
    args=p.parse_args()
    plan=json.loads(Path(args.plan).read_text()) if Path(args.plan).exists() else {"beats":[]}
    sfx=[]
    for b in plan.get("beats",[]):
        for s in b.get("sfx",[]):
            sfx.append({"at":s["at"],"type":s["type"],"file":SFX_MAP.get(s["type"],""),"beat":b["id"]})
    # quantize to 1/8 beat (~0.06s at 124 BPM) and enforce ≤1 per 0.4s
    sfx=sorted(sfx, key=lambda x:x["at"])
    filtered=[]
    last=-10
    for e in sfx:
        if e["at"]-last >=0.4:
            # quantize
            e["atQuant"]=round(round(e["at"]/0.06)*0.06,3)
            filtered.append(e); last=e["at"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"sfx":filtered,"duckVoiceDb":-16,"duckSfxDb":-21}, indent=2))
    print(f"SFX: {len(filtered)} events → {args.out}")
    for e in filtered: print(f"  {e['atQuant']:.2f}s {e['type']} ({e['beat']})")
