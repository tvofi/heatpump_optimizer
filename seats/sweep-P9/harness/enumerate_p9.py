"""Class P9 seam enumerator, round 11 (D14 method step 3).

P9: card UI -- a clipping ancestor, a missing colour token, or an unfloored
hit target. Generalises the six findings' seams to every declaration of the
card that can produce one, by a line scan of the card source:

  TARGET  a pointer target sized outside the floor list: a literal
          `min-height: <N>px` with N < 44 on a selector, or a `stroke-width`
          under an `.editing` selector (an SVG stroke used as a hit band)
          [D4-s1-01 .setup-svg.editing .setup-pipe; D4-s1-03 .hl-fold-head]
  TYPE    a `font-size` not drawn from the type scale: neither
          var(--hpo-text-*) nor max(12px, ...)          [D4-s3-03, D4-s3-05]
  COLOUR  a colour bypassing the token layer: a *_READABLE constant
          interpolated into CSS, or a direct Home Assistant status-colour var
          (--error-color / --warning-color / --success-color)   [D4-s3-04]
  CLIP    an `overflow: hidden` ancestor
  STACK   a value hung `display: block` under its own label inside a stats
          grid row (`.hl-value`-shape: display:block; margin-top)  [D4-s3-02]

Run: python3 enumerate_p9.py [--card PATH] [--fixture clean|perturbed]
--fixture clean      a stylesheet drawn only from tokens and the floor list -> seams=0
--fixture perturbed  plus one line `.x-btn { min-height: 32px; }`             -> seams=1
"""
import argparse, re, tempfile

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
RX = {
    "TARGET": re.compile(r"min-height:\s*(\d+(?:\.\d+)?)px"),
    "TYPE": re.compile(r"font-size[:=]\s*[\"']?([^;\"'}]+)"),
    "COLOUR": re.compile(r"\$\{(ERROR|SUCCESS|WARNING)_READABLE(_DARK)?\}|var\(--(error|warning|success)-color"),
    "CLIP": re.compile(r"overflow:\s*hidden"),
    "STACK": re.compile(r"\.hl-value\s*\{[^}]*display:\s*block|display:\s*block;\s*margin-top"),
}
EDIT_STROKE = re.compile(r"\.editing[^{]*\{[^}]*stroke-width:\s*[\d.]+")
CLEAN = """.a { font-size: var(--hpo-text-sm, 13px); color: var(--hpo-crit, #b3261e); }
.b { font-size: max(12px, 0.8em); min-height: ${targetFloorPx}px; }
"""
PERTURB = ".x-btn { min-height: 32px; }\n"


def scan(text):
    out = []
    lines = text.splitlines()
    sel = ""
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith(("//", "* ", "/*", "*")) and not s.startswith("*{"):
            continue
        m = re.match(r"([^{}]+)\{", s)
        if m:
            sel = m.group(1).strip()
        mt = RX["TARGET"].search(s)
        if mt and float(mt.group(1)) < 44 and float(mt.group(1)) > 0:
            out.append(("TARGET", i, sel, s))
        if EDIT_STROKE.search(s) or (".editing" in sel and "stroke-width" in s):
            out.append(("TARGET", i, sel, s))
        mf = RX["TYPE"].search(s)
        if mf:
            v = mf.group(1).strip()
            if "--hpo-text" not in v and not v.startswith("max(12px") and not v.startswith("inherit"):
                out.append(("TYPE", i, sel, s))
        if RX["COLOUR"].search(s):
            out.append(("COLOUR", i, sel, s))
        if RX["CLIP"].search(s):
            out.append(("CLIP", i, sel, s))
        if RX["STACK"].search(s):
            out.append(("STACK", i, sel, s))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default=CARD)
    ap.add_argument("--fixture", choices=["clean", "perturbed"])
    a = ap.parse_args()
    text = CLEAN + (PERTURB if a.fixture == "perturbed" else "") if a.fixture else open(a.card, encoding="utf-8").read()
    seams = scan(text)
    for fam, ln, sel, s in seams:
        print(f"SEAM {fam} card:{ln} [{sel[:60]}] | {s[:110]}")
    c = {k: sum(1 for x in seams if x[0] == k) for k in RX}
    print(f"RESULT seams={len(seams)} " + " ".join(f"{k}={v}" for k, v in c.items()))


if __name__ == "__main__":
    main()
