---
name: motion-broll-pro
description: High-energy pure-code motion graphics skill — creates 12/15/20s videos from raw talking video, script, or voiceover with 15 slop blacklist, fetch-vs-generate asset router, and beat-locked SFX
license: MIT
compatibility: claude-code, arena, cursor, cline
allowed-tools: Bash, Read, Write, Edit, WebSearch, WebFetch, ImageSearch, GenerateImage, GenerateSpeech
metadata:
  author: abdullaharafinrahat
  version: 1.0.0
  engine: pure-code motion.js + ffmpeg 180° shutter
---

# motion-broll-pro — High-Energy Pure-Code Motion Skill

> **Input:** raw talking video (priority) OR script.txt OR voiceover.mp3 — user gives ANY ONE.
> **Output:** 2560×1440 25fps MP4 (12/15/20s high-energy, 45-90s medium if user says "medium"), beat-synced motion + SFX, pure-code via engine/motion.js.
> **Default energy:** HIGH. Switch to MEDIUM only if user explicitly says "medium energy" / "calm" / "slow".

---

## 1. YOU ARE A CRAFT MOTION EDITOR, NOT A SLOP GENERATOR

Before any code, read `linters/slop-check.py` blacklist (15 signs). If your plan looks like purple glass Pinterest, you failed. Rule: **Every frame is hero frame** — no frozen frames, no 80% purple flood, no fake faces.

## 2. INPUT ROUTER (3 MODES)

**Detect input type in order:**
1. **Has `input.mp4` / `push.mp4` / raw_video path?** → `RAW VIDEO MODE`
   - Run: `python scripts/inspect_video.py --in <video>` → W,H,FPS,duration, PIP boxes
   - Run: `object-separation` (BiRefNet) → cutout with 1.5px white stroke, no halo
   - Whisper transcribe → `scripts/words.py` → word timings `beats.js` map
   - Sample 5 frames → extract palette (dominant 3 colors) → base for theme. DO NOT RECOLOR user room to purple.

2. **Has `voiceover.mp3`?** → `VOICEOVER MODE`
   - Audio duration = truth. Whisper → timings. No TTS.

3. **Has `script.txt` only?** → `SCRIPT-ONLY MODE`
   - `scripts/parse_script.py --script script.txt` → sentences, word count, lang bn/en
   - Estimate duration: bn 2.8 w/s, en 3.2 w/s. If TTS later, re-time with real audio.
   - TTS later via `generate_speech` with correct `bn-BD` / `en-US` voice.

**Never ask for assets the user didn't give.** If mode=raw video, NEVER generate_image of a person.

## 3. 9-STEP WORKFLOW

1. **Parse** → `parse_script.py` → detect entities ($, orgs like Vercel/Gemini, stats)
2. **Time** → `words.py` → beats map, `M.crossTimes()` hit points
3. **Plan** → Use `prompts/planner.system.md` + `plan.schema.json` → write `output/plan.json` (must validate schema before continue)
4. **Fetch** → `scripts/fetch_assets.py` for every `asset.type=fetch` → web_search + image_search + fetch_page → `output/assets/fetch_*`
5. **Generate** → `generate_image` for `asset.type=generate` → `output/assets/gen_*` (transparent if needed, min 1024px)
6. **TTS (if needed)** → `add_voice` + `generate_speech` → `output/voice.mp3` → re-time beats
7. **Code** → For each beat, write `output/scenes/XX-*.html` from `templates/scene-*.html` + `prompts/scene.system.md` → must use `M.track`, `M.vis`, `SH/SEQ`, never CSS transition/timers
8. **Render** → `node engine/render.js` per scene → 4 subframes/frame → ffmpeg blend 180° shutter → `output/clips/*.mp4` (+ `.mov` transparent for panels)
9. **Sound + Composite** → `python linters/slop-check.py --plan output/plan.json` must pass → `python scripts/sound_pass.py --beats output/beats.json` → `scripts/composite.py` → `output/final.mp4` + `compare.html` + `viewer.html` + `TIMING.md`

## 4. HIGH-ENERGY SPEC (DEFAULT)

**Duration options:** 12s / 15s / 20s. Medium only if user says "medium" → 45-90s.

| Rule | High | Medium (if requested) |
|------|------|------------------------|
| Avg shot hold | 0.7-1.1s | 1.8-3.2s |
| Max hold | 1.4s (linter fails >1.4) | 4.0s |
| BPM | 124-136 | 92-105 |
| Re-theme per beat | YES — bg hue shift 30-60° + SH w/h/r/cam change | every 2 beats |
| Stagger between pops | ≥120ms, max 3 concurrent | ≥180ms |
| Who triggers | Every visual push = whoosh, tick per Bengali word hit |

**Retheme enforcement:** `SH` must rotate: pill → phone → grid → ribbon → split. Never same template 2x consecutively. `SEQ` cam `fx` must be ≠0 for ≥40% beats (asymmetry).

## 5. FETCH vs GENERATE ROUTER

**FETCH (real org/logo/data exists online):** Vercel, ChatGPT, Claude, Gemini, PayPal, Stripe, YouTube, Figma, Notion, etc.
```
→ web_search "Vercel logo SVG official"
→ fetch_page https://vercel.com → brand color #000000, tagline, description
→ image_search or fetch SVG → assets/fetch/vercel-logo.svg
→ Use with clear space 0.5× logo height, never stretch/recolor, caption from fetched data
```

**GENERATE (conceptual, no real reference):** "$12M dashboard", "3-step funnel glass cards", "3D scissors icon"
```
→ generate_image prompt includes sampled palette + "dark navy #05122E, neon cyan 2px stroke, soft shadow 0 16px 40px"
→ min 1024px, transparent bg if overlay
```

Decision in `plan.json` per asset: `{"type":"fetch","query":"Vercel logo","fallback":"generate"}`. Linter checks fetch assets exist and are not AI-drawn fakes.

## 6. EVERY FRAME PRIORITY

- Zero frozen frames. Even hold has drift: `Y sin 0.9s ±4px` or parallax 0.3× cam.
- Check: render every 25th frame → must have motion vs prev (diff >2% pixels) else fail.
- Gap to black >0.2s = fail. Shape always morphing via `M.track`, never disappearing.

## 7. MOTION ENGINE RULES (engine/motion.js)

- Frame = pure function `seek(t)`. No `setTimeout`, no CSS transition. Springs `S(tau,w,z)` closed-form.
- Shape: `SH {name:{w,h,r,bg,cam}}`, `SEQ [[t,name]...]`, `tr(k)=M.track(P0[k], SEQ.map(...), sp)`
- Layers: `{el,tin,tout,o:{din:0.07,lin:0.26,lout:0.12,blur:12}, update(t,g)}` with `M.vis()` + `M.apply()`
- Cursor: `M.path(CK)` + `M.presses(clicks,drags)` if needed.
- Springs: MORPH [15,0.84], FAST [27,0.86], SOFT [10,0.95], CAM [7.5,1] — rotate, never same 2 beats.

Example (from reference):
```js
const trW = M.track(P0.w, SEQ.map(([t,n])=>[t,SH[n].w]), M.MORPH);
seek = (t)=>{ let g={w:trW(t), bg: M.ctrack(...) , s:cam(t)}; world.style.transform=`translate(${CX - s*fx}px) scale(${s})`; }
```

## 8. SOUND DESIGN MAP

Use `skills/sound-effects/sfx/` + `MUSIC.md` top picks. Call `scripts/sound_pass.py`.

| Visual | SFX File | Offset |
|--------|----------|--------|
| Wipe/push | whoosh-soft-01.wav (0.18s) | tin -0.04s |
| Pill/card pop | pop-cork-02.wav | tin +0.06s |
| Phone/monitor snap | shutter-01.wav | tin |
| Bengali word hit | click-soft.wav | M.crossTimes per word |
| Money/success | chime-success.wav | on green arrow |
| Reveal | swoosh-hit.wav | tout -0.02s |

Rules: ≤1 SFX per 0.4s, quantize to 1/8 beat, duck -21 LUFS under voice -16 LUFS.

## 9. 20-POINT QUALITY CHECKLIST (Non-Negotiable)

Every `plan.json` and render must pass `linters/slop-check.py`:

1. Safe 8% inset
2. 3-size typography only, Geist + Noto Sans Bengali
3. Contrast ≥4.5:1
4. Icon stroke 2.2px normalized
5. Shadow 0 16px 40px on floating
6. Logo clear space 0.5×, no stretch
7. ≥1024px generated, SVG for logos
8. ≥30% negative space
9. Zero linear motion
10. Hold ≥0.8s readable
11. 180° blur on >400px/s
12. ≤3 concurrent, ≥120ms stagger
13. Hold ≤1.4s (high) / 4.0s (med)
14. Cam asymmetry ≥40% beats
15. Story 5-8 beats: Hook→Problem→Pillars→Proof→CTA
16. Numbers sourced or skeleton ___ + "Example"
17. Bengali joined correctly, bn-BD voice
18. Palette sampled from input, not purple flood
19. Every beat has SFX mapped
20. Every frame has drift (no freeze)

PLUS 15 AI slop blacklist (see linters/slop-check.py header) — any CRITICAL (1,7,8,14) = instant fail.

## 10. OUTPUTS

- `output/final.mp4` (H.264 1805kb/s, AAC 64kb/s HE-AAC)
- `output/clips/*.mp4` + `*.mov` transparent panels
- `output/TIMING.md` in/out per beat
- `output/compare.html` (wipe/side-by-side)
- `output/viewer.html` (frame scrub)

## 11. HOW TO RUN

```
/motion-broll-pro --in raw.mp4 --style high
/motion-broll-pro --script script.txt --style high --duration 15
/motion-broll-pro --voice voice.mp3 --style medium  (only if user says medium)
```

No human questions in script-only. Auto-continue after schema validation.

