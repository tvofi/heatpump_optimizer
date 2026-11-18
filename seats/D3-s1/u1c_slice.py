#!/usr/bin/env python3
"""D3-s1 box D3-u1c slice tally and D3.M4 answers.

Metric (one line): over the keys of state/keys-D3-u1c.txt, the fast-net
verdict prescreen.py `run --sub pre` recorded (KILLED by first driver /
SURVIVED / TIMEOUT / not driven), keys that resolve to no inventory mutant
(unparseable), mutants every closure driver skipped by reach, and, per
survivor, the D3.M4 answer: production line, file, and the closure drivers
whose unmutated traced baseline EXECUTES that line yet did not fail (the
checks that should have failed), plus the full-net verdict where
results/complete/ holds one.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_slice.py [--write-surv] [--json]
Reads only dev/audit/rounds/round11/D3/s1/state/; counts are exact.
Instrumented symbol: tests/mutation_table.py:killed / reach_skip verdicts of
prescreen.py:drive on each mutant's production line; reach from
state/baselines.json (mutation_table.traced_baseline).
Perturbation: posctl-D3-u1c (two ledger-pinned sites) reads KILLED 2/2 and
state/null-D3-u1c.json LIVES; a key file with a pinned site added raises
`killed` by one.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1c,
Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prescreen as ps  # noqa: E402

KEYS = HERE / "state" / "keys-D3-u1c.txt"
SURV = HERE / "state" / "keys-D3-u1c-surv.txt"


def main() -> int:
    keys = [k.strip() for k in KEYS.read_text().split() if k.strip()]
    inv = {ps.key(m): m for m in ps.unpinned() + ps.pinned()}
    base = ps.load_base()
    res = {k: json.loads((ps.RESULTS / "pre" / (k + ".json")).read_text())
           for k in keys if (ps.RESULTS / "pre" / (k + ".json")).exists()}
    comp = {k: json.loads((ps.RESULTS / "complete" / (k + ".json")).read_text())
            for k in keys if (ps.RESULTS / "complete" / (k + ".json")).exists()}
    unparse = [k for k in keys if k not in inv]
    c = Counter(r["verdict"] for r in res.values())
    first = Counter(r["killed_by"][0] for r in res.values() if r["killed_by"])
    allskip = [k for k, r in res.items() if not r["runs"]]
    print(f"RESULT keys={len(keys)}")
    print(f"RESULT unparseable={len(unparse)}")
    print(f"RESULT driven={len(res)}")
    for v in ("KILLED", "SURVIVED", "TIMEOUT"):
        print(f"RESULT {v.lower()}={c.get(v, 0)}")
    print(f"RESULT all_drivers_reach_skipped={len(allskip)}")
    print(f"RESULT driver_skips_by_reach={sum(len(r['skipped']) for r in res.values())}")
    print(f"RESULT driver_skips_relaxed={sum(len(r.get('relaxed_skipped', [])) for r in res.values())}")
    for s, n in first.most_common():
        print(f"  first-kill {s} {n}")
    kinds = Counter((r["mutant"]["kind"], r["verdict"]) for r in res.values())
    for (k, v), n in sorted(kinds.items()):
        print(f"  kind {k} {v} {n}")
    files = Counter((r["mutant"]["file"].rsplit("/", 1)[-1], r["verdict"]) for r in res.values())
    for (f, v), n in sorted(files.items()):
        print(f"  file {f} {v} {n}")
    cc = Counter(r["verdict"] for r in comp.values())
    print(f"RESULT complete_driven={len(comp)}")
    for v in ("KILLED", "SURVIVED", "TIMEOUT"):
        print(f"RESULT complete_{v.lower()}={cc.get(v, 0)}")
    for s, n in Counter(s for r in comp.values() for s in r["killed_by"]).most_common():
        print(f"  complete-kill {s} {n}")
    surv = sorted(k for k, r in res.items() if r["verdict"] == "SURVIVED")
    if "--write-surv" in sys.argv:
        SURV.write_text("\n".join(surv) + "\n")
    answers = {}
    for k in surv:
        r = res[k]
        m = r["mutant"]
        ds = [s for s in base if m["file"] in ps.mt.load_closures().get(s, ())]
        cls = {s: ps.classify(base, s, m) for s in ds}
        ex = sorted(s for s, v in cls.items() if v == "exec")
        cv = comp.get(k, {})
        answers[k] = {
            "anchor": m["anchor"], "file": m["file"], "line": m["line"],
            "kind": m["kind"], "old": m["old"].strip(), "new": m["new"].strip(),
            "fast_net_ran": sorted(r["runs"]), "deferred_slow": r.get("deferred_slow", []),
            "should_have_failed": ex or ["none of the closure executes the line: a "
                                         "direct check on " + m["anchor"].split(":", 1)[1].split()[0]],
            "full_net": cv.get("verdict", "not driven"),
            "full_net_killed_by": cv.get("killed_by", []),
        }
    if "--json" in sys.argv:
        (HERE / "m4_answers-D3-u1c.json").write_text(json.dumps(answers, indent=1))
    print(f"RESULT survivors_answered={len(answers)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
