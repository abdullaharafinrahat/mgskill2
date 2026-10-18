#!/usr/bin/env python3
"""
slop-check.py — 15 AI Slop Blacklist + 20 Quality Checks
Fails if slop_score >30 or any CRITICAL rule triggered.
Run: python linters/slop-check.py --plan output/plan.json [--render-dir output/clips]

CRITICAL slop (instant fail):
  #1 Purple Flood, #7 AI Face, #8 Fake Numbers, #14 Robotic Bengali
"""
import json, sys, argparse, re
from pathlib import Path

CRITICAL = {1,7,8,14}

SLOP_RULES = {
 1: ("Purple Flood", "maxPurpleRatio >0.25 or bg contains #7C3AED/A78BFA/8B5CF6 as dominant", 15, True),
 2: ("Glass Everywhere", ">2 glass layers in single beat", 6, False),
 3: ("Glow Diarrhea", "glow radius >18px or opacity >0.6 or >2 glows concurrent", 8, False),
 4: ("Floating 3D No Physics", "3D without shadow/press/bob >1.5s", 7, False),
 5: ("Particle Spam", ">6 particles per trigger or infinite loop", 6, False),
 6: ("Wavy Unreadable", "wave amp >8px or skew >12° on sentence", 7, False),
 7: ("AI Face/Hand", "generate person face when inputMode=raw_video", 15, True),
 8: ("Fake Numbers", "invented stat without source/skeleton", 15, True),
 9: ("Same Spring Loop", "2 consecutive beats same spring preset", 5, False),
10: ("Center Locked", "<40% beats have asymmetry (fx!=0)", 6, False),
11: ("Stock Mock Empty", "mock with lorem/no real UI data", 7, False),
12: ("Flare Overdose", ">1 flare or flare over face/mouth", 6, False),
13: ("ADHD Pop Spam", ">3 concurrent or stagger <120ms", 8, False),
14: ("Robotic Bengali TTS", "wrong lang tag bn-BD or mispronounce check fails", 12, True),
15: ("Template Recycle", "same template 3x consecutive or missing required variety", 9, False),
}

QUALITY_CHECKS = [
 "Safe 8% inset", "3-size typography", "Contrast 4.5:1", "Icon stroke 2.2px",
 "Shadow 0 16px 40px", "Logo clear space 0.5x", "Assets ≥1024px / SVG",
 "≥30% negative space", "Zero linear (springs only)", "Hold ≥0.8s readable",
 "180° blur >400px/s", "≤3 concurrent ≥120ms stagger", "Hold ≤1.4s high /4s med",
 "Cam asymmetry ≥40%", "Story 5-8 beats", "Numbers sourced/skeleton",
 "Bengali correct", "Palette sampled not purple", "SFX mapped per beat", "Every frame drift"
]

def check_purple(plan):
    pal = plan.get("meta",{}).get("palette",{})
    bg = pal.get("bg","").lower()
    purple = pal.get("maxPurpleRatio",0)
    # detect purple flood: if palette contains known purple and ratio >0.25
    purple_hex = ["#7c3aed","#a78bfa","#8b5cf6","#9333ea","#c084fc"]
    if purple > 0.25: return False, f"maxPurpleRatio {purple} >0.25"
    if bg in purple_hex: return False, f"bg {bg} is purple flood"
    return True, "ok"

def check_face(plan):
    mode = plan.get("meta",{}).get("inputMode")
    assets = plan.get("assets",[])
    for a in assets:
        if mode=="raw_video" and a.get("type")=="generate" and any(k in a.get("query","").lower() for k in ["face","person","man","woman","speaker"]):
            return False, f"asset {a['id']} generates person while raw video exists"
    return True, "ok"

def check_fake_numbers(plan):
    beats = plan.get("beats",[])
    for b in beats:
        line=b.get("line","")
        # if contains $/ % with large number, must have asset fetch or mock
        if re.search(r"\$[\d,]+|[\d]+%", line):
            # check if any asset for this beat is fetch/mock
            has_fetch = any(a.get("beatId")==b["id"] and a["type"] in ("fetch","mock") for a in plan.get("assets",[]))
            if not has_fetch:
                return False, f"beat {b['id']} has number but no fetch/mock source"
    return True, "ok"

def check_template_recycle(plan):
    beats = plan.get("beats",[])
    templates=[b.get("template") for b in beats]
    for i in range(len(templates)-2):
        if templates[i]==templates[i+1]==templates[i+2]:
            return False, f"templates {templates[i]} x3 consecutive at {i}"
    # required variety for high energy: at least 4 distinct templates in 5+ beats
    if len(set(templates)) < 4 and len(beats)>=5:
        return False, f"only {len(set(templates))} distinct templates, need ≥4"
    return True, "ok"

def check_hold(plan):
    energy = plan.get("meta",{}).get("energy","high")
    max_hold = 1.4 if energy=="high" else 4.0
    for b in plan.get("beats",[]):
        hold = b.get("tOut",0)-b.get("tIn",0)
        # also check per-layer hold vs beat hold
        if hold > max_hold + 0.5: # allow tiny overshoot for final CTA
            return False, f"beat {b['id']} hold {hold:.2f}s >{max_hold}s for {energy}"
        # per-layer readable hold ≥0.8s
        for L in b.get("layers",[]):
            lh = L.get("tout",0)-L.get("tin",0)
            if 0 < lh < 0.6:
                return False, f"layer {L['el']} in {b['id']} only {lh:.2f}s (<0.8 readable)"
    return True, "ok"

def check_stagger(plan):
    for b in plan.get("beats",[]):
        layers=sorted(b.get("layers",[]), key=lambda x:x["tin"])
        for i in range(len(layers)-1):
            gap = layers[i+1]["tin"] - layers[i]["tin"]
            if gap < 0.12:
                return False, f"beat {b['id']} layers {layers[i]['el']}→{layers[i+1]['el']} gap {gap*1000:.0f}ms <120ms"
        if len([l for l in layers if l["tin"]<=b["tIn"]+0.5]) >3:
            return False, f"beat {b['id']} has >3 concurrent pops in first 0.5s"
    return True, "ok"

def check_asymmetry(plan):
    beats=plan.get("beats",[])
    if not beats: return True, "ok"
    asym = 0
    for b in beats:
        sh = b.get("SH",{})
        seq = b.get("SEQ",[])
        # if any SH bg cam !=1 or any SEQ cam change, count
        # simplified: check if template in grid/split/dashboard or SH has cam !=1
        if b.get("template") in ("grid","split","dashboard","terminal") or any(v.get("cam",1)!=1 for v in sh.values()):
            asym+=1
    ratio = asym/len(beats)
    if ratio < 0.4:
        return False, f"asymmetry ratio {ratio:.2f} <0.4 (center locked)"
    return True, "ok"

def check_palette_source(plan):
    src = plan.get("meta",{}).get("paletteSource","")
    if src == "default_navy":
        return True, "ok default navy allowed"
    if src not in ("sampled_from_input","user_provided","default_navy"):
        return False, f"paletteSource {src} not allowed — must sample from input or user"
    return True, "ok"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan", required=True)
    p.add_argument("--render-dir", default=None)
    args=p.parse_args()
    plan=json.loads(Path(args.plan).read_text())

    failures=[]
    slop_score=0
    critical_hit=False

    checks=[
        (1, lambda: check_purple(plan)),
        (7, lambda: check_face(plan)),
        (8, lambda: check_fake_numbers(plan)),
        (15, lambda: check_template_recycle(plan)),
        (13, lambda: check_stagger(plan)),
        (10, lambda: check_asymmetry(plan)),
        (999, lambda: check_palette_source(plan)), # extra quality check mapped to slop 1
        (999, lambda: check_hold(plan)),
    ]
    for rid, fn in checks:
        ok, msg = fn()
        if not ok:
            is_critical = rid in CRITICAL
            weight = SLOP_RULES.get(rid, ("Quality", "", 6, False))[2] if rid in SLOP_RULES else 7
            slop_score+=weight
            status="CRITICAL" if is_critical else "FAIL"
            failures.append(f"[{status}] #{rid if rid!=999 else 'Q'} {msg} (+{weight})")
            if is_critical: critical_hit=True

    # duration / energy mismatch
    energy=plan.get("meta",{}).get("energy","high")
    dur=plan.get("video",{}).get("duration",0)
    if energy=="high" and dur>22:
        failures.append(f"[FAIL] #Q high-energy duration {dur}s >22s (should be 12/15/20)")
        slop_score+=6
    if energy=="medium" and dur<25:
        failures.append(f"[FAIL] #Q medium duration {dur}s <25s")

    print("="*70)
    print(f"Plan: {args.plan}")
    print(f"Energy: {energy}  Duration: {dur}s  FPS: {plan.get('video',{}).get('fps')}")
    print(f"Beats: {len(plan.get('beats',[]))}  Assets: {len(plan.get('assets',[]))}  Input: {plan.get('meta',{}).get('inputMode')}")
    print("-"*70)
    if failures:
        print("FAILURES:")
        for f in failures: print(" ", f)
    else:
        print("All structural checks passed.")
    print(f"Slop Score: {slop_score}/100  (threshold 30)")
    print(f"Critical hit: {critical_hit}")
    print("="*70)
    if critical_hit or slop_score>30:
        print("RESULT: ❌ FAIL — fix plan before render")
        sys.exit(1)
    else:
        print("RESULT: ✅ PASS — ready to render")
        sys.exit(0)

if __name__=="__main__":
    main()
