"""Round-3 review seat: perturb revision 2's gate_sim timing, which its 41/41 is
scored at one fixed point (PRELUDE 5, GATE_READ 5, GATE 15, REFRESH 10, SWEEP 20).

    python3 -I tools/timing_perturb.py <rev2>/measure/rev

Arm U (uniform): every gate attempt takes the same time; the constants are swept.
Arm H (heterogeneous): a hook's RE-RUN attempt of `gate` waits for a runner and so
takes longer than a first attempt (RERUN_EXTRA s queued before it is listed
in_progress is NOT modelled: the attempt is listed at once, as gate_sim does; the
extra time is spent between its read and its completion, the slow tail).
Only REV2 is scored, under both chain arms, over gate_sim's own 41 scenarios and
its own oracle and readings. A row is END-BAD when the final merge box disagrees
with the oracle under any reading (the false-green window is reported apart, since
it scales with REFRESH by design)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as GS  # noqa: E402

BASE = dict(PRELUDE=5, GATE_READ=5, GATE=15, REFRESH=10, SWEEP=20)


class Het(GS.World):
    extra = 0

    def start_gate(self, r):
        super().start_gate(r)
        r["gate_len"] = GS.GATE + (self.extra if r["attempt"] > 1 else 0)

    def gate_tick(self, r, phase):
        t0 = r.get("gate_t0")
        if t0 is None or r["status"] != "in_progress":
            return
        if phase == "read" and r["gate_read"] is None and self.t >= t0 + GS.GATE_READ:
            r["gate_read"] = self.eval_gate(r)
        if phase == "finish" and self.t >= t0 + r.get("gate_len", GS.GATE):
            self.finish_gate(r)


def score(chain, scen, world=GS.World, extra=0):
    bad, fgmax = [], 0
    for label, evs, truth, plant in scen:
        tag = label.split()[0]
        if tag in GS.CAPPED:
            continue
        w = world("REV2", truth, plant, chain=chain)
        if extra:
            w.extra = extra
        s = w.run(evs, until=12000)
        _, bc, bd, be, orc = s[-1]
        if tag in GS.MUST_FAIL:
            ok = (bc, bd, be) == (False, False, False)
        else:
            ok = bc == orc and bd == orc and be == orc
            fgmax = max(fgmax, GS.max_win(s))
        if not ok:
            bad.append(f"{tag}(o={GS.fmt(orc)} c={GS.fmt(bc)} d={GS.fmt(bd)} e={GS.fmt(be)})")
    return bad, fgmax


def setc(**kw):
    for k, v in {**BASE, **kw}.items():
        setattr(GS, k, v)


def main():
    scen = GS.SCEN + GS.crosshead() + GS.STRESS
    total = 0
    print("## arm U: uniform gate attempts, constants swept (REV2, END-BAD rows per chain arm)")
    grid = [dict()]
    grid += [dict(GATE=g, GATE_READ=r) for g in (15, 30, 60, 120) for r in (5, g - 2) if not (g == 15 and r == 5)]
    grid += [dict(REFRESH=x) for x in (1, 60, 300)]
    grid += [dict(SWEEP=x) for x in (1, 5, 60, 300)]
    grid += [dict(PRELUDE=x) for x in (1, 30)]
    for kw in grid:
        setc(**kw)
        for chain in (True, False):
            b, fg = score(chain, scen)
            total += len(b)
            print(f"  {str(kw or 'gate_sim as committed'):40s} {'chain  ' if chain else 'nochain'} END-BAD {len(b):2d}"
                  f"  false-green max {fg:5d} s  {' '.join(b)[:300]}")
    print("\n## arm H: a hook's re-run attempt is slower than a first attempt (slow tail after its read)")
    for extra in (10, 30, 60, 120, 300):
        setc()
        for chain in (True, False):
            b, fg = score(chain, scen, world=Het, extra=extra)
            total += len(b)
            print(f"  re-run attempt +{extra:3d} s {'chain  ' if chain else 'nochain'} END-BAD {len(b):2d}"
                  f"  false-green max {fg:5d} s  {' '.join(b)[:300]}")
    print(f"\nTIMING-PERTURB END-BAD total {total}")


main()
