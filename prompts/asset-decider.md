# ASSET DECIDER — Fetch vs Generate vs Mock

Input: beat line + entities + inputMode
Output: asset {type, query, reason, fallback}

RULES:
1. Real org/brand/product with public logo/website → FETCH
   Examples: Vercel, ChatGPT, Claude, Gemini, PayPal, Stripe, YouTube, Figma, Next.js, GitHub
   → Must fetch logo SVG + 1-line description from official site (via web_search + fetch_page)
   → Reason: "Real brand needs official logo — AI redraw is slop and trademark risk"

2. Conceptual / bespoke UI that doesn't exist → GENERATE
   Examples: "$12,440,000 iPhone dashboard", "3-step funnel lime cards", "3D scissors icon black", "payment floating cards"
   → generate_image with prompt including sampled palette
   → Prompt template: "{subject}, dark navy #05122E, neon {accent} 2px stroke, soft shadow 0 16px 40px, {style}, 1024x1024, transparent bg"

3. Stat without source → MOCK
   Examples: "+340% growth", "$12M" without citation
   → mock skeleton bar + "Example" label 10px, never invent number

4. Fallback chain: fetch → if fail (no SVG found) → generate (but mark as mock style)
   image_search relevance <0.6 → fallback to generate

5. If inputMode=raw_video, never generate face/person. Always object-separated cutout.

Return JSON:
{"type":"fetch","query":"Vercel logo SVG official","reason":"Real org Vercel has public logo, must fetch","fallback":"generate"}
