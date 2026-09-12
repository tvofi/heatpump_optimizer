#!/usr/bin/env python3
"""D3 round 4 -- suite resource accounting, from tests/closures.json and the
measured baseline this round took.

METRIC: (a) per script, closures.json's recorded seconds against the seconds
the same script actually costs when the gate runs it here; (b) per production
module, the CI seconds its measured closure selects; (c) the seconds a scoped
gate cannot avoid because env_drift.py is widened by rule.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/resource_r4.py

EXPECTED: counts and ratios only; the wall seconds it quotes come from
prescreen.json, which records load1 beside each. Deterministic given those two
files.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PKG = "custom_components/heatpump_optimizer/"


def main() -> int:
    raw = json.loads((ROOT / "tests" / "closures.json").read_text())
    cl, rec = raw["closures"], raw["recorded"]
    state = json.loads((HERE / "prescreen.json").read_text()) if (HERE / "prescreen.json").exists() else {}
    base = state.get("baseline", {})

    print("== (a) recorded seconds vs the seconds the gate actually spends ==")
    print(f"  {'script':30s} {'recorded':>9s} {'measured':>9s} {'ratio':>8s}")
    worst = []
    for s in sorted(set(rec) | set(base)):
        r = rec.get(s, {}).get("seconds")
        m = base.get(s, {}).get("seconds")
        if r is None or m is None:
            # env_drift is recorded under its cache-key form and measured under
            # the --all form the gate runs; line them up by hand.
            if s == "tests/env_drift.py --all":
                r = rec.get("tests/env_drift.py", {}).get("seconds")
            if r is None or m is None:
                continue
        ratio = m / r if r else float("inf")
        worst.append((ratio, s, r, m))
        print(f"  {s:30s} {r:9.1f} {m:9.1f} {ratio:8.1f}x")
    worst.sort(reverse=True)
    if worst:
        ratio, s, r, m = worst[0]
        print(f"RESULT worst_recorded_vs_measured_ratio={ratio:.0f} ratio  ({s}: {r}s recorded, {m}s measured)")

    print()
    print("== (b) CI seconds a one-line change to each production module selects ==")
    # env_drift.py ALWAYS runs when anything under custom_components/ changed,
    # whatever the closure says (tests/README.md, "How a closure is derived").
    def secs(script: str) -> float:
        if script == "tests/env_drift.py":
            return base.get("tests/env_drift.py --all", {}).get("seconds", 0.0)
        return base.get(script, {}).get("seconds", rec.get(script, {}).get("seconds", 0.0))

    per_module = {}
    for f in sorted({f for files in cl.values() for f in files if f.startswith(PKG)}):
        scripts = sorted({s for s in cl if f in cl[s]} | {"tests/env_drift.py"})
        per_module[f] = (scripts, sum(secs(s) for s in scripts))
    ordered = sorted(per_module.items(), key=lambda kv: -kv[1][1])
    for f, (scripts, tot) in ordered[:6] + [("...", ([], 0.0))] + ordered[-6:]:
        if f == "...":
            print("   ...")
            continue
        print(f"  {f[len(PKG):]:34s} {len(scripts):3d} script(s) {tot:8.1f}s")
    cheapest = min(v[1] for v in per_module.values())
    dearest = max(v[1] for v in per_module.values())
    print(f"RESULT module_gate_seconds_min={cheapest:.1f} wall")
    print(f"RESULT module_gate_seconds_max={dearest:.1f} wall")
    print(f"RESULT module_gate_seconds_spread={dearest / cheapest:.1f} ratio")

    print()
    print("== (c) the floor a scoped gate cannot go below for a production one-liner ==")
    floor_scripts = sorted({s for s in cl if any(
        f.startswith(PKG) for f in cl[s])} & set())  # placeholder, see below
    ed = secs("tests/env_drift.py")
    print(f"  env_drift.py --all, run by rule for ANY change under {PKG}: {ed:.1f}s")
    print(f"RESULT env_drift_all_seconds={ed:.1f} wall")
    print(f"RESULT env_drift_share_of_cheapest_module={100 * ed / cheapest:.0f} percent")

    print()
    print("== (d) duplicated coverage: which script killed each mutant ==")
    killers: dict[str, int] = {}
    for r in state.get("mutants", {}).values():
        k = r.get("killed_by") or "SURVIVED"
        killers[k] = killers.get(k, 0) + 1
    for k, n in sorted(killers.items(), key=lambda kv: -kv[1]):
        print(f"  {k:32s} {n:3d}")
    print(f"RESULT distinct_killers={len([k for k in killers if k != 'SURVIVED'])} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
