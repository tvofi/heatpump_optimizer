"""Round-4 review seat: revision 3's sweep poll at and past its own 600 s bound.

    python3 -I tools/poll_bound.py <rev3>/measure/rev

Revision 3 states (DESIGN-P2.md 4.3) that a gate attempt still running when the
sweep's 600 s poll ends is "left as it is, with a notice: red, never green". This
scores the TAIL arm (re-run attempts only) at 500, 580, 620 and 900 s on the
scenarios the round-3 seat's finding named (R7, I4) plus R3 and X4 (second reviews),
so the stated bound is shown to be where the liveness residual starts, and that past
it the box ends red (fail closed), never green against a red oracle."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as GS  # noqa: E402

pick = [x for x in GS.SCEN + GS.STRESS if x[0].split()[0] in ("R7", "I4", "R3", "X4")]
for tail in (500, 580, 620, 900):
    for chain in (True, False):
        rows = GS.score("REV2", chain, pick, tail=tail)
        bad = [f"{r[1]}(o={GS.fmt(r[2][0])} c={GS.fmt(r[2][1])} d={GS.fmt(r[2][2])} e={GS.fmt(r[2][3])})" for r in rows if not r[7]]
        greens = [r[1] for r in rows if not r[7] and r[2][0] is False and True in r[2][1:4]]
        notes = sorted({m for r in rows for m in r[6] if "bound" in m})
        print(f"tail {tail:3d} s {'chain  ' if chain else 'nochain'} END-BAD {len(bad)} false-green-at-end {len(greens)}  {'; '.join(bad)}  {' | '.join(notes)[:160]}", flush=True)
