#!/usr/bin/env python3
"""Measure every text and graphic colour pair the product page draws, in both themes, with the repository's WCAG
formula (color.py, ported from tests/card.mjs). Text needs 4.5:1, large display text and graphics 3:1."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from color import contrast
T = {
 "light": dict(bg="#f3f8fc", surface="#ffffff", s2="#eef4f9", ink="#0f2233", ink2="#4d5d6c", accent="#026aa8", accent_ink="#ffffff",
               heat="#b4501a", heat_mark="#d2601f", well="#e8f0f6", hero_a="#e3eef7", line="#d6e0e8"),
 "dark": dict(bg="#0b1a28", surface="#11263a", s2="#16304a", ink="#eaf2f8", ink2="#a9bccb", accent="#4fb3f0", accent_ink="#0b1a28",
              heat="#f08a3c", heat_mark="#f08a3c", well="#16304a", hero_a="#10263b", line="#24405a"),
}
PAIRS = [  # (what, fg, bg, kind)
 ("body text on page", "ink", "bg", "text"), ("body text on hero top", "ink", "hero_a", "text"),
 ("secondary text on page", "ink2", "bg", "text"), ("secondary text on hero top", "ink2", "hero_a", "text"),
 ("secondary text on surface", "ink2", "surface", "text"), ("secondary text on well (note, tabs)", "ink2", "well", "text"),
 ("h1 ember phrase on hero top", "heat", "hero_a", "large"), ("h1 ember phrase on page", "heat", "bg", "large"),
 ("link and tile value on page", "accent", "bg", "text"), ("link on surface (docs cards)", "accent", "surface", "text"),
 ("primary button label", "accent_ink", "accent", "text"), ("step and list numerals", "accent", "surface", "large"),
 ("icon on well", "accent", "well", "graphic"), ("limit rule on surface", "heat_mark", "surface", "graphic"),
 ("focus ring on page", "accent", "bg", "graphic"), ("body text on well (code)", "ink", "well", "text"),
]
NEED = {"text": 4.5, "large": 3.0, "graphic": 3.0}
out, ok = [], True
for th, c in T.items():
    for what, fg, bg, kind in PAIRS:
        r = round(contrast(c[fg], c[bg]), 2)
        p = r >= NEED[kind]; ok &= p
        out.append(dict(theme=th, pair=what, fg=c[fg], bg=c[bg], kind=kind, ratio=r, need=NEED[kind], pass_=p))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CONTRAST.json"), "w"), indent=1)
for o in out:
    print(f"{o['theme']:5} {'pass' if o['pass_'] else 'FAIL'} {o['ratio']:5} (need {o['need']}) {o['pair']}")
print("RESULT:", f"all {len(out)} pairs pass" if ok else "FAILURES")
sys.exit(0 if ok else 1)
