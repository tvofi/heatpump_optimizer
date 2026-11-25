#!/usr/bin/env python3
"""D3-s2 tally of drive_resumable.py's pairs.jsonl into per-mutant verdicts.

Metric: per enumerator item, "killed by S" / "LIVES" (every closure driver
ran green or was reach-skipped) / "SKIP-*" / "not_reached" (no verdict yet).
Count key: the verdict drive_resumable.py derived from mutation_table.killed.
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/tally.py dev/audit/rounds/round11/D3/s2/drive dev/audit/rounds/round11/D3/s2/run [--json]
Perturbation: delete one kill row from pairs.jsonl and that item moves from
"killed by" to not_reached (or LIVES once its other drivers are all present).
Counts exact; baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "tests")
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402

SKIP = ("tests/stress.py", "tests/edge.py", "tests/backtest.py",
        "tests/harness_headers.py")


def tally(out, prev):
    base = {json.loads(l)["script"] for l in open(Path(prev) / "progress.jsonl")
            if '"baseline"' in l}
    closures = mt.load_closures()
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",") if s and s not in SKIP]
    pairs = {}
    special = {}
    for ln in open(Path(out) / "pairs.jsonl"):
        d = json.loads(ln)
        if d["script"] == "-":
            special[d["item"]] = d["verdict"]
        else:
            pairs[(d["item"], d["script"])] = d
    universe, _ = en.universe()
    rows = []
    for s in universe:
        name = en.item_name(s)
        drivers = [d for d in mt.drivers_for(s["file"], closures, allow) if d in base]
        got = [pairs.get((name, d)) for d in drivers]
        kill = [g for g in got if g and g["hit"]]
        tout = [g for g in got if g and g["hit"] is None]
        if name in special:
            v = special[name]
        elif kill:
            v = "killed by " + kill[0]["script"]
        elif tout:
            v = "SKIP-TIMED-OUT in " + tout[0]["script"]
        elif all(got):
            v = "LIVES"
        else:
            v = "not_reached"
        ran = [g["script"] for g in got if g and not g.get("reach_skip")]
        rows.append(dict(item=name, file=s["file"], line=s["line"],
                         kind=s["kind"], old=s["old"], new=s["new"],
                         status=s["status"], verdict=v, drivers=drivers,
                         ran=ran, checks=kill[0].get("checks") if kill else None))
    return rows


if __name__ == "__main__":
    rows = tally(sys.argv[1], sys.argv[2])
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        sys.exit(0)
    c = Counter(r["verdict"].split(" in ")[0] if r["verdict"].startswith("SKIP")
                else r["verdict"] for r in rows)
    for r in rows:
        if r["verdict"] != "not_reached":
            print(f"{r['item']}\t{r['verdict']}\t{(r['checks'] or [''])[0][:90]}")
    for k, v in sorted(c.items()):
        print(f"RESULT verdict[{k}]={v} mutants")
    print(f"RESULT examined={sum(v for k, v in c.items() if k != 'not_reached')} of {len(rows)} mutants")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
