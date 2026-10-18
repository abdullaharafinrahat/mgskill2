# motion-broll-pro — High-Energy Pure-Code Motion (Built)

This skill builds on `push.mp4` analysis (2560×1440 25fps, 1 shape morph, 0 hard cuts). Default = **high-energy 12/15/20s**, medium only if user says "medium".

## Quick Start

**3 input modes:**
```bash
# Raw video (best) — auto-transcribe + cutout
python scripts/parse_script.py --script script.txt
python scripts/inspect_video.py --in /path/to/push.mp4 --out output/inspect.json

# Script only
echo "বর্তমানে সবচেয়ে বেশি competition..." > script.txt
python scripts/parse_script.py --script script.txt --out output/parse.json

# Voiceover only
python scripts/words.py --transcript script.txt --duration 15 --out output/beats.json
```

**Full pipeline:**
```bash
# 1. Plan (agent fills plan.json per prompts/planner.system.md)
# 2. Validate
python linters/slop-check.py --plan output/plan.json

# 3. Fetch real logos (Vercel, ChatGPT, etc.)
python scripts/fetch_assets.py --plan output/plan.json

# 4. Generate missing images (prompt must include palette)
# 5. TTS if needed → output/voice.mp3
# 6. Build scenes from templates/scene-*.html
python engine/build.py --plan output/plan.json

# 7. Render (4 subframes/frame → 180° blur)
node engine/render.js --plan output/plan.json

# 8. Sound + composite
python scripts/sound_pass.py --plan output/plan.json --beats output/beats.json
python scripts/composite.py --clipsDir output/clips --voice output/voice.mp3 --out output/final.mp4
```

## Structure
- `SKILL.md` — agent instructions + 20 quality checks + 15 slop blacklist
- `plan.schema.json` — strict JSON; must validate before any render
- `engine/motion.js` — pure `seek(t)` engine (no timers, springs S(tau,w,z))
- `prompts/` — planner, scene builder, asset decider (fetch vs generate vs mock)
- `templates/scene-*.html` — pill, phone, grid, ribbon (copy then swap)
- `linters/slop-check.py` — slop score, critical fails
- `scripts/` — inspect, parse, words, fetch, sound_pass, composite

## Quality
- Safe 8% inset, 3-size typography, contrast 4.5:1, icon stroke 2.2px, shadow 0 16px 40px
- High energy: max hold 1.4s, avg 0.7-1.1s, every beat re-themes (bg hue 30-60°), asymmetry ≥40%
- Every frame has drift — never frozen. Checked via 1fps diff.
- Sound: whoosh/pop/shutter/tick/chime mapped to SFX dir, ducked -21 LUFS

## Fetch vs Generate
- Real org (Vercel, Gemini, Claude, ChatGPT) → `fetch` logo SVG + description via web_search + fetch_page (never generate)
- Conceptual ($12M card) → `generate` with palette-aware prompt
- Stat without source → `mock` skeleton + "Example"

See `SKILL.md` for full 9-step workflow and blacklist.

