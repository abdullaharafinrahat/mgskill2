#!/usr/bin/env python3
"""fetch_assets.py — fetch real logos/data for plan.json assets where type=fetch
Uses web_search + fetch_page + image_search via bash wrappers.
This stub validates plan and writes fetch manifest; real fetch is done by agent tool calls.
"""
import json, argparse, pathlib, re
from pathlib import Path

BRAND_COLORS={
 "vercel":{"primary":"#000000","bg":"#FFFFFF","desc":"Frontend Cloud — Build, scale, and secure workflows"},
 "chatgpt":{"primary":"#10A37F","bg":"#FFFFFF","desc":"AI chat by OpenAI"},
 "claude":{"primary":"#D97706","bg":"#F5F0E6","desc":"AI by Anthropic"},
 "gemini":{"primary":"#4285F4","bg":"#FFFFFF","desc":"Google AI model"},
}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--plan", default="output/plan.json")
    p.add_argument("--outDir", default="output/assets")
    args=p.parse_args()
    plan=json.loads(Path(args.plan).read_text())
    Path(args.outDir).mkdir(parents=True, exist_ok=True)
    manifest=[]
    for a in plan.get("assets",[]):
        if a["type"]=="fetch":
            name=a["query"].lower()
            # simple lookup for well-known brands
            key=next((k for k in BRAND_COLORS if k in name), None)
            entry={"id":a["id"],"query":a["query"],"expectedPath":f"{args.outDir}/fetch_{a['id']}.svg","brand":BRAND_COLORS.get(key,{}),"action":"agent must run web_search + image_search + fetch_page for this query"}
            manifest.append(entry)
    out=Path(args.outDir)/"fetch_manifest.json"
    out.write_text(json.dumps(manifest, indent=2))
    print(f"Fetch manifest: {len(manifest)} assets → {out}")
    for m in manifest: print(f"  {m['id']}: {m['query']} → {m['expectedPath']}")
