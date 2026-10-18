#!/usr/bin/env python3
"""parse_script.py — script → sentences + language + entity detection"""
import argparse, re, json
from pathlib import Path

BENGALI_RE = re.compile(r"[\u0980-\u09FF]")

def detect_lang(text):
    bn = len(BENGALI_RE.findall(text))
    total = len(text.split())
    if bn/len(text) > 0.08: return "bn"
    if bn>0: return "mixed"
    return "en"

def extract_entities(text):
    ents=[]
    # orgs/logos
    orgs=["vercel","chatgpt","openai","claude","anthropic","gemini","google","figma","notion","payPal","stripe","youtube","github","next.js","nextjs"]
    for o in orgs:
        if o.lower() in text.lower():
            ents.append({"type":"org","name":o,"need":"fetch"})
    # money / percent
    for m in re.findall(r"\$[\d,\.]+|[\d,]+%|\+\$[\d,\.]+\+? *\$?[\d]*", text):
        ents.append({"type":"stat","value":m,"need":"mock_or_fetch"})
    return ents

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--script", required=True)
    p.add_argument("--out", default="output/parse.json")
    args=p.parse_args()
    text=Path(args.script).read_text(encoding="utf-8")
    sents=re.split(r"[।\.\n]+", text)
    sents=[s.strip() for s in sents if s.strip()]
    lang=detect_lang(text)
    ents=extract_entities(text)
    est_dur = len(text.split()) / (2.8 if lang in ("bn","mixed") else 3.2)
    out={"language":lang,"sentences":sents,"entities":ents,"estDuration":round(est_dur,2),"wordCount":len(text.split())}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
