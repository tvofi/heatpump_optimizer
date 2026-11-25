"""The fast lane's shard balance, priced in CI seconds (R11-CI-CASE-SELECT P2, #3885).

    python3 dev/audit/harnesses/r11_fast_shards_balance.py LOGDIR [--seed N]

LOGDIR holds `fast` job logs of FULL push runs (no `MODE: SCOPED` line), one file each, as
`dev/audit/harnesses/ci_script_seconds.py`'s job_log returns them. Each script's price is its
median over those logs' closing wall-clock tables. A shard's wall is run.sh's own shape over the
scripts it owns: the three lanes (units, golden, e2e; each lane's scripts in sequence, the lanes
side by side) and then the stress lane alone.

Prints, each with the rule that produced it:
  CALIBRATION  the same model over the unsharded suite against the logs' median TOTAL line;
  PLAN         tools/ci/shards.py's full plan at HEAD: each shard's modelled wall, the makespan;
  NULL random  the makespan of 200 random assignments to the same shard count (median, best);
  FLOOR        the longest single script's median, which no script-level shard can beat;
  SPLIT        per script tests/case_select.py splits: the best two-way contiguous span split,
               each half run with its `needs` closure (what a sound split must re-run), as the
               larger half's share of the script's recorded span seconds; NULL: the same split
               with every `needs` edge dropped (the unsound split).
EXPECTED RESULT: the plan's makespan is within 10% of FLOOR and under the random null's median;
the unsharded model reads within 20% of the logs' median TOTAL (each script at its own median,
summed along a lane, overstates a run whose scripts drew a fast host together); SPLIT reads above
0.9 for both scripts. Its null reads near 0.5 for features.py (the needs closure, not the
splitter, keeps it whole) and stays high for entities.py, whose one span `#558 D6 numeric schedule
companion` holds most of its seconds.
"""
from __future__ import annotations

import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import shards  # noqa: E402

LANE_FN = re.compile(r"^lane_(\w+)\(\) \{$")


def lanes_of_run_sh() -> dict[str, str]:
    """script -> the run.sh lane function its run line sits in."""
    out, lane = {}, None
    for line in (ROOT / "tests" / "run.sh").read_text().splitlines():
        m = LANE_FN.match(line)
        if m:
            lane = m.group(1)
            continue
        if line.startswith("}"):
            lane = None
        m = shards._RUN_LINE.match(line)
        if m and lane:
            out.setdefault(m.group(2), lane)
    return out


def medians(logdir: Path) -> tuple[dict[str, float], list[float], int]:
    per: dict[str, list[int]] = {}
    totals, used = [], 0
    for f in sorted(logdir.iterdir()):
        t = f.read_text(errors="replace")
        if "MODE: SCOPED" in t or "########## wall clock ##########" not in t:
            continue
        used += 1
        table = t.split("########## wall clock ##########", 1)[1]
        one: dict[str, int] = {}          # a script's lines in one run summed (env_drift runs twice)
        for line in table.splitlines():
            m = re.search(r"\s(\d+)s\s+TOTAL", line)
            if m:
                totals.append(float(m.group(1)))
                break
            m = re.search(r"\s(\d+)s\s+\S+ (.*)$", line)
            if m:
                s = next((a for a in m.group(2).split() if a.startswith("tests/")), None)
                if s:
                    one[s] = one.get(s, 0) + int(m.group(1))
        for s, v in one.items():
            per.setdefault(s, []).append(v)
    return {s: statistics.median(v) for s, v in per.items()}, totals, used


def wall(owned: set[str], price: dict[str, float], lane: dict[str, str]) -> float:
    by = {}
    for s in owned:
        by.setdefault(lane.get(s, "units"), 0.0)
        by[lane.get(s, "units")] += price.get(s, 0.0)
    return max([v for k, v in by.items() if k != "stress"], default=0.0) + by.get("stress", 0.0)


def main(argv: list[str]) -> int:
    logdir = Path(argv[0])
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 0
    price, totals, used = medians(logdir)
    lane = lanes_of_run_sh()
    scripts, always = shards.suite_scripts((ROOT / "tests" / "run.sh").read_text())
    print(f"logs read: {used} FULL fast logs; scripts priced: {len(price)}")
    model = wall(set(scripts), price, lane)
    print(f"CALIBRATION unsharded model {model:.0f}s vs median TOTAL {statistics.median(totals):.0f}s "
          f"(ratio {model / statistics.median(totals):.3f})")
    known = shards.timings(shards._show("HEAD", "tests/closures.json"),
                           shards._show("HEAD", "tests/case_closures.json"))
    p = shards.plan(scripts, always, shards.priced(scripts, known), None)
    n = p["n"]
    walls = [wall({s for s, k in p["s"].items() if k == i}, price, lane) for i in range(1, n + 1)]
    print(f"PLAN {n} shards: " + ", ".join(f"{i}/{n}={w:.0f}s" for i, w in enumerate(walls, 1))
          + f"; makespan {max(walls):.0f}s, spread max/min {max(walls) / max(min(walls), 1):.2f}")
    rng = random.Random(seed)
    nulls = []
    for _ in range(200):
        a = {s: rng.randint(1, n) for s in scripts}
        nulls.append(max(wall({s for s in scripts if a[s] == i}, price, lane) for i in range(1, n + 1)))
    print(f"NULL random ({n} shards, 200 draws, seed {seed}): median makespan {statistics.median(nulls):.0f}s, "
          f"best {min(nulls):.0f}s")
    top = max(price, key=price.get)
    print(f"FLOOR longest script {top} {price[top]:.0f}s")
    sys.path.insert(0, str(ROOT / "tests"))
    import case_select  # noqa: PLC0415
    table = case_select.load()
    for script in case_select.SCRIPTS:
        e = case_select.entry(table, script)
        sec = {k: v["seconds"] for k, v in e["spans"].items()}
        ids, tot = list(sec), sum(sec.values())
        for label, need in (("sound", {k: set(v["needs"]) for k, v in e["spans"].items()}),
                            ("NULL no-needs", {k: set() for k in ids})):
            def clos(start):
                out, st = set(start), list(start)
                while st:
                    for x in need[st.pop()]:
                        if x not in out:
                            out.add(x)
                            st.append(x)
                return sum(sec[i] for i in out)
            best = min(max(clos(ids[:k]), clos(ids[k:])) for k in range(1, len(ids)))
            print(f"SPLIT {script} {label}: larger half {best:.0f}s of {tot:.0f}s recorded = {best / tot:.3f}")
    print("PRICES " + json.dumps({s: price[s] for s in sorted(price, key=price.get, reverse=True)[:8]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
