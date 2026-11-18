"""P9 sweep probe (round 11): does a card rule paint a status role from the token layer?

Reads cardStyleBlock's rule for SELECTOR in the card source and lists its colour
declarations (color / stroke / fill / background / border*). Exits 1 when one reads a
Home Assistant status colour directly (var(--error-color|--warning-color|--success-color))
or a *_READABLE constant -- the bypass D4-s3-04 judged -- and 0 when every one reads
var(--hpo-*) (CARD_TOKENS).
Run: python3 probe_token.py '<selector>' [--perturb]
  '.setup-pipe.invalid'         the seam (fails: var(--error-color, #db4437) = a third error shade
                                beside --hpo-crit #b3261e and ERROR_READABLE #ca4c46)
  '.status-pill.tone-crit'      null control (reads --hpo-crit)
  --perturb                     re-points the one line at var(--hpo-crit, #b3261e) in memory -> 0
"""
import re, sys
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
sel = sys.argv[1]
src = open(CARD, encoding="utf-8").read()
if "--perturb" in sys.argv:
    src = src.replace("stroke: var(--error-color, #db4437);", "stroke: var(--hpo-crit, #b3261e);", 1)
m = re.search(r"(?m)^\s*" + re.escape(sel) + r"\s*\{([^}]*)\}", src)
if not m:
    sys.exit(f"rule {sel!r} not found")
decls = [d.strip() for d in m.group(1).split(";") if re.match(r"\s*(color|stroke|fill|background|border[a-z-]*)\s*:", d)]
bad = [d for d in decls if re.search(r"var\(--(error|warning|success)-color|_READABLE", d)]
print(f"PROBE {sel}: colour decls {decls} -> bypass {len(bad)} {'FAIL' if bad else 'ok'}")
sys.exit(1 if bad else 0)
