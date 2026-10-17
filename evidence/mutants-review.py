"""Fix-review mutation proof for R10-UX-SETUP / PR 2346.

Re-runs the PR body's 8 mutants independently: each is an exact production-line
replacement applied to the head worktree copy, the closure (node tests/card.mjs)
is run and its FAIL lines recorded, then the file is restored from git.
M0 is the null control.
"""
import subprocess, os, json, sys

WT = "/private/tmp/r10-review-2346/mut"
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
PLANDATA = "/private/tmp/r10-review-2346/scratch/plandata.json"

MUT = [
    ("M0", "null control: no mutation", None, None),
    ("M1", "fitSlotRow wraps -> ellipsizes the label again",
     """    lines: wrapText(label, inner - SETUP_ROW_GAP - valueW, inner,
      SETUP_ROW_LINES, size),""",
     """    lines: [ellipsize(label, inner - SETUP_ROW_GAP - valueW, size, false)],"""),
    ("M2", "the unset slots fold -> become ordinary rows again",
     """      if (reading === null) {
        unsetRows.push({ slot: s });
      } else {""",
     """      if (reading === null) {
        liveRows.push({ slot: s, fit: fitSlotRow(s.label,
          [L("setup.not_configured")], inner, 12) });
      } else {"""),
    ("M8", "an OPEN folded block's height counted as the folded one",
     "      (b.foldLines ? b.foldLines.length + 1 : 0)",
     "      (b.foldLines && !b.open ? b.foldLines.length + 1 : 0)"),
    ("M3", "the card is painted -> left invisible",
     "        fill: var(--hpo-surface-2, #f7f9fb);",
     "        fill: none;"),
    ("M4", "one precision per unit -> Home Assistant's own precision",
     "  if (places === undefined) return formatted;",
     "  return formatted;"),
    ("M5", "the axis measures its label -> counts its characters (C1)",
     "      const half = textWidth(tick.label, size) / 2;",
     "      const half = (size * tick.label.length * CHAR_WIDTH_EM) / 2;"),
    ("M6", "noPlanHtml owns the empty state -> a second spelling (C4)",
     "      body = this.plan.noPlanHtml();",
     """      body = `<div class="empty">${L("errors.no_plan_data")}<br>
      ${this.plan.diagnose("space")}<br>
      ${this.plan.diagnose("dhw")}</div>`;"""),
    ("M7", "finiteNum owns the number test -> a second spelling (C4)",
     '    const money = (n) => (finiteNum(n) ? n.toFixed(2) : "—");',
     '    const money = (n) => (typeof n === "number" && Number.isFinite(n) ? n.toFixed(2) : "—");'),
]

out = []
env = {**os.environ, "HPO_PLANDATA": PLANDATA}
for name, why, old, new in MUT:
    p = os.path.join(WT, CARD)
    if old is not None:
        s = open(p).read()
        n = s.count(old)
        if n != 1:
            raise SystemExit(f"{name}: expected 1 occurrence, found {n}")
        open(p, "w").write(s.replace(old, new))
    r = subprocess.run(["node", "tests/card.mjs"], cwd=WT, env=env,
                       capture_output=True, text=True)
    fails = [l.strip()[6:].strip() for l in (r.stdout + r.stderr).split("\n")
             if l.strip().startswith("FAIL ")]
    tail = (r.stdout.strip().split("\n") or [""])[-1]
    out.append({"mutant": name, "why": why, "rc": r.returncode,
                "fails": fails, "tail": tail})
    print(f"{name} rc={r.returncode} fails={len(fails)} :: {why}")
    for f in fails:
        print(f"    FAIL {f}")
    if old is not None:
        subprocess.run(["git", "checkout", "--", CARD], cwd=WT, check=True)

json.dump(out, open("/private/tmp/r10-review-2346/evidence/mutants-review.json", "w"), indent=1)
