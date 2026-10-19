"""Round-4 review seat: revision 3's sweep poll under NON-uniform timing.

    python3 -I tools/jitter_perturb.py <rev3>/measure/rev [seeds] [maxtail]

The round-3 instruments and revision 3's own TAIL arm move one constant at a time,
uniformly over every attempt. Here every gate attempt (first or re-run) draws its own
read-to-completion tail from [0, maxtail] s and its own read offset, and every
`refresh` and `sweep` hook draws its own latency (refresh 1-120 s, sweep 1-300 s),
from a seeded RNG, so attempts overtake one another in every order. Rows: REV2
(revision 3's rules) in both chain arms over gate_sim's scenarios less the capped S2.
END-BAD = the final merge box differs from the oracle under some reading (planted
scenarios must end red under all three). The null control is the `poll` ablation
(revision 2's sweep) under the same draws: it must move."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as GS  # noqa: E402

SEEDS = int(sys.argv[2]) if len(sys.argv) > 2 else 20
MAXTAIL = int(sys.argv[3]) if len(sys.argv) > 3 else 300


class Todo(list):
    def __init__(self, w):
        super().__init__()
        self.w = w

    def append(self, item):
        if item[1] == "refresh":
            item = (self.w.t + self.w.rng.randint(1, 120),) + tuple(item[1:])
        elif item[1] == "sweep":
            item = (self.w.t + self.w.rng.randint(1, 300),) + tuple(item[1:])
        super().append(item)


class Jit(GS.World):
    def __init__(self, *a, seed=0, **k):
        super().__init__(*a, **k)
        self.rng = random.Random(seed)
        self.todo = Todo(self)

    def start_gate(self, r):
        super().start_gate(r)
        x = self.rng.randint(0, MAXTAIL)
        r["gate_len"] = GS.GATE + x
        r["gate_rd"] = self.rng.randint(2, GS.GATE - 2 + x)


def score(seed, chain, ablate=()):
    bad, att = [], 0
    for label, evs, truth, plant in GS.SCEN + GS.crosshead() + GS.STRESS:
        tag = label.split()[0]
        if tag in GS.CAPPED:
            continue
        w = Jit("REV2", truth, plant, ablate=ablate, chain=chain, seed=seed * 100003 + sum(map(ord, tag)) * 7919)
        s = w.run(evs, until=9000 + 40 * MAXTAIL)
        _, bc, bd, be, orc = s[-1]
        ok = (bc, bd, be) == (False, False, False) if tag in GS.MUST_FAIL else (bc == orc and bd == orc and be == orc)
        att = max(att, max(r["attempt"] for r in w.runs))
        if not ok:
            bad.append(f"{tag}(o={GS.fmt(orc)} c={GS.fmt(bc)} d={GS.fmt(bd)} e={GS.fmt(be)})")
    return bad, att


def main():
    tot = {(): 0, ("poll",): 0}
    for ab in ((), ("poll",)):
        name = "REV3" if not ab else "null: without poll"
        for seed in range(SEEDS):
            for chain in (True, False):
                bad, att = score(seed, chain, ab)
                tot[ab] += len(bad)
                print(f"{name:20s} seed {seed:2d} {'chain  ' if chain else 'nochain'} END-BAD {len(bad)} max-attempt {att:2d}  {'; '.join(bad)[:220]}", flush=True)
    print(f"JITTER maxtail {MAXTAIL} s, {SEEDS} seeds: REV3 END-BAD total {tot[()]}; without poll {tot[('poll',)]}")


main()
