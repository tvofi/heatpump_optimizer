#!/usr/bin/env python3
"""D3.M5 per-script table for seat D3-s3, round 11 (source-only aggregator).

Metric (one line): per gate script enumerate_m5.py prints, S = optimize()
calls and A = checks its green run reported (solves.py, which hooks
custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize),
A/S, and the run's wall and child CPU (provisional, box B3 under fan-out load)
against tests/closures.json's recorded seconds.
Command:  python3 dev/audit/rounds/round11/D3/s3/m5_table.py
Reads solves.out, solves2.out ... solves5.out (the last record of a script
wins) and tests/closures.json; runs nothing. Counts exact, seconds provisional.
Perturbation: solves.py --perturb-double doubles every S>0 (its own control);
this table moves with it because it only reads the records.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3 records.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RX = re.compile(r"^RESULT (.+?):(solves|asserts|wall|cpu|distinct_inputs)=(\S+)")


def main() -> int:
    rows: dict[str, dict] = {}
    for f in sorted(HERE.glob("solves*.out")):
        cur: dict[str, dict] = {}
        for ln in f.read_text().splitlines():
            m = RX.match(ln)
            if m:
                s = m.group(1).split()[0]
                cur.setdefault(s, {})[m.group(2)] = m.group(3)
        for s, r in cur.items():
            rows[s] = {**rows.get(s, {}), **r, "src": f.name}
    uni = subprocess.run([sys.executable, str(HERE / "enumerate_m5.py")],
                         capture_output=True, text=True, check=True).stdout
    n = done = 0
    for ln in uni.splitlines():
        s, rec = ln.split("\t")
        n += 1
        r = rows.get(s)
        if not r:
            print(f"NOT-MEASURED\t{s}\trecorded={rec}s")
            continue
        done += 1
        S = int(r.get("solves", "0"))
        A = int(r.get("asserts", "0"))
        aps = f"{A / S:.3f}" if S else "-"
        wall = r.get("wall", "?")
        ratio = (f"{float(wall) / float(rec):.2f}" if wall not in ("?",)
                 and float(rec) > 0 else "-")
        print(f"{s}\tS={S}\tA={A}\tA/S={aps}\twall={wall}s cpu={r.get('cpu','?')}s"
              f" (provisional)\trecorded={rec}s\twall/recorded={ratio}"
              f"\tdistinct={r.get('distinct_inputs', '-')}\t[{r['src']}]")
    print(f"RESULT m5_universe={n} count")
    print(f"RESULT m5_measured={done} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
