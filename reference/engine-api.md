# Engine API — motion.js

Copy from repo-push `motion-broll` engine. 90 lines core.

- `M.track(v0, keys, def, period)` → function(t) → value. keys: [[t, target, w, z]]
- `M.ctrack(h0, keys)` → color lerp
- `M.vis(t,tin,tout,{din,lin,lout,blur})` → {o,blur,s}
- `M.apply(el,{o,blur,s})` → set opacity/filter/transform
- `M.path(CK)` → cursor path
- `M.presses(clicks,drags)` → press scale track
- `M.scene(cfg)` → seek(t) pure function, exposes window.seek + window.DURATION

cfg: {W,H,center,bg,SH,start,SEQ,layers,cursor,shapePress,intro,T,geom,extra,spring,camSpring}

Layers: [{el,tin,tout,anchor,o,update}]

Render: headless Chromium captures 4 subframes per frame (t-0.015 etc), ffmpeg blend → motion blur.
