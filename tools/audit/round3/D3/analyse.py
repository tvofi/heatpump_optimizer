#!/usr/bin/env python3
"""The D3 round-3 numbers, read off the merged pre-screen record.

Run (from the repository root, after merge_runs.py and verdicts.py):

    python3 tools/audit/round3/D3/analyse.py

Prints every RESULT the report cites.  Counts only; contention-immune.
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
"""
from __future__ import annotations

import json
from pathlib import Path

V = json.loads(Path("tools/audit/round3/D3/prescreened_verdicts.json").read_text())
REC = json.loads(Path("tests/closures.json").read_text())["recorded"]
SEL = json.loads(Path("tools/audit/round3/D3/closures_by_module.json").read_text())

rows = V["rows"]
surv = [r for r in rows if r["strict_status"] == "SURVIVOR"]
killed = [r for r in rows if r["strict_status"] == "KILLED"]
drift_ran = [r for r in rows
             if any(x["script"] == "tests/env_drift.py --all" for x in r["ran"])]
drift_only = [r for r in killed if r["strict_killed_by"] == ["tests/env_drift.py --all"]]

print(f"RESULT mutants={len(rows)} mutants")
print(f"RESULT survivors={len(surv)} mutants ({','.join(r['id'] for r in surv)})")
print(f"RESULT killed={len(killed)} mutants ({','.join(r['id'] for r in killed)})")
print(f"RESULT survival_rate={len(surv)/len(rows):.3f} fraction")
print(f"RESULT differential_gate_ran_for={len(drift_ran)} mutants")
print(f"RESULT killed_only_by_differential_gate={len(drift_only)} mutants "
      f"({','.join(r['id'] for r in drift_only)})")

kills: dict[str, set] = {}
ran: dict[str, set] = {}
for r in rows:
    for x in r["ran"]:
        ran.setdefault(x["script"], set()).add(r["id"])
    for s in r["strict_killed_by"]:
        kills.setdefault(s, set()).add(r["id"])
print("RESULT kills_by_script=" + json.dumps({s: len(v) for s, v in sorted(kills.items())}))
print("RESULT runs_by_script=" + json.dumps({s: len(v) for s, v in sorted(ran.items())}))
never = sorted(s for s in ran if not kills.get(s))
print(f"RESULT scripts_that_ran_and_never_killed={len(never)} " + json.dumps(never))
for s in never:
    secs = REC.get(s, {}).get("seconds")
    print(f"       {s}: ran for {len(ran[s])} mutants, killed 0, "
          f"recorded {secs}s per run")

# Duplicated coverage.
scripts = sorted(kills)
dup = 0
for i, a in enumerate(scripts):
    for b in scripts[i + 1:]:
        n = len(kills[a] & kills[b])
        if n:
            dup += 1
            print(f"RESULT overlap[{a}|{b}]={n} mutants")
print(f"RESULT killer_script_pairs_that_overlap={dup} pairs "
      f"of {len(scripts)*(len(scripts)-1)//2}")

# By module and by mutation kind.
bymod: dict[str, list] = {}
bykind: dict[str, list] = {}
for r in rows:
    bymod.setdefault(r["module"], []).append(r["strict_status"] == "SURVIVOR")
    bykind.setdefault(r["kind"], []).append(r["strict_status"] == "SURVIVOR")
print("RESULT survivors_by_module=" + json.dumps(
    {m: f"{sum(v)}/{len(v)}" for m, v in sorted(bymod.items())}))
print("RESULT survivors_by_kind=" + json.dumps(
    {k: f"{sum(v)}/{len(v)}" for k, v in sorted(bykind.items())}))

# Closure cost per module, from the recorded seconds only.
print("RESULT closure_cost_recorded_seconds=" + json.dumps(
    {m: round(sum(REC.get(s, {"seconds": 0})["seconds"] for s in v["run"]), 1)
     for m, v in sorted(SEL.items())}))

# Leave-one-out over the 17 modules the sample touched: the survival rate with
# each module's mutants dropped in turn.
by: dict[str, list] = {}
for r in rows:
    by.setdefault(r["module"], []).append(r["strict_status"] == "SURVIVOR")
loo = {}
for m in by:
    keep = [v for k, vs in by.items() if k != m for v in vs]
    loo[m] = round(sum(keep) / len(keep), 3)
per_cell = {m: round(sum(v) / len(v), 3) for m, v in by.items()}
print(f"RESULT leave_one_out_cells={len(by)} modules")
print(f"RESULT per_module_survival_min={min(per_cell.values())} fraction")
print(f"RESULT per_module_survival_max={max(per_cell.values())} fraction")
print(f"RESULT survival_rate_drop_most_favourable={min(loo.values())} fraction "
      f"(dropping {min(loo, key=loo.get)})")
print("RESULT leave_one_out=" + json.dumps(loo))
