#!/usr/bin/env python3
"""R10-HOTFIX-CI-CRITPATH-3: replay critical_path_minutes' statistic on real runs.

    python3 dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py

Reads only the tree and runs.json beside this file: the 40 completed ci.yml
push runs on main 41363452534..41577822624 (2026-11-01T23:43Z..
2026-11-03T04:23Z) with their jobs, cut to the fields tests/ci_ratchet.py
reads. No network. Every figure is tests/ci_ratchet.py's own
window_work_minutes / critical_path_minutes over a window of PUSH_WINDOW
runs; `retired` is the statistic it replaced at #3180's first head
(563c8e6db: the other-work floor keyed on the window MAXIMUM, every
non-skipped conclusion pricing), kept here as the comparison arm only.

  1. record    -- the newest window's grade, every window's value, the record
                  (largest window) against tests/ci_budgets.json, and the
                  band's need: how far a window reads past the record of every
                  window before it, against critical_path_minutes_band.
  2. outlier   -- the newest run's lane set to 3.2x the window's fastest run
                  of it (one slow or hung draw): must not move the grade.
  3. growth    -- +300 s on a lane in every run: must move the grade (the
                  null control of 2); then in only the newest k runs (the
                  detection lag), beside the retired statistic.
  4. slow fleet -- each fast draw of a lane in the newest 15 runs made 1.9x
                  slower: disclosed, not asserted (the minimum prices the
                  fastest host the window drew).

Exit 0 when 1-3 hold, 1 otherwise.
"""
from __future__ import annotations

import copy
import json
import statistics
import sys
from datetime import timedelta
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


HERE = Path(__file__).resolve().parent
ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))

from tests import ci_ratchet as cr  # noqa: E402

LANES = ("tests / closures", "tests / fast (3.14)", "tests / arch-instrument")
FAST_BELOW_S = {"tests / closures": 1700, "tests / fast (3.14)": 1500,
                "tests / arch-instrument": 1400}
W = cr.PUSH_WINDOW


def retired(window: list[dict]) -> "float | None":
    chains, work = [], {}
    for r in window:
        walked = cr._walk(r)
        if walked is None:
            continue
        chains.append(cr.run_chain(r))
        concl = {}
        for j in r["jobs"]:
            if j.get("completed_at"):
                concl.setdefault(j["name"], []).append(j.get("conclusion"))
        for w in walked:
            if concl[w["name"]].pop(0) != "skipped":
                work.setdefault(w["name"], []).append(w["work"])
    if not chains:
        return None
    price = {n: min(w for w in seen if w >= max(seen) * cr.OTHER_WORK_FRACTION)
             for n, seen in work.items()}
    return round(max(sum(price.get(n, 0.0) for n in ch) for ch in chains) / 60, 3)


def with_work(r: dict, lane: str, fn) -> dict:
    r = copy.deepcopy(r)
    for j in r["jobs"]:
        if j["name"] == lane and j.get("started_at") and j.get("completed_at"):
            s = cr._at(j["started_at"])
            w = (cr._at(j["completed_at"]) - s).total_seconds()
            j["completed_at"] = (s + timedelta(seconds=fn(w))).strftime("%Y-%m-%dT%H:%M:%SZ")
    return r


def work_s(r: dict, lane: str) -> "float | None":
    for j in r["jobs"]:
        if j["name"] == lane and j.get("conclusion") == "success":
            return (cr._at(j["completed_at"]) - cr._at(j["started_at"])).total_seconds()
    return None


def main() -> int:
    runs = sorted(json.loads((HERE / "runs.json").read_text())["workflow_runs"],
                  key=lambda r: r["created_at"], reverse=True)
    budgets = json.loads((ROOT / "tests/ci_budgets.json").read_text())
    new = cr.window_work_minutes
    ok = True

    vals = [new(runs[i:i + W]) for i in range(len(runs) - W + 1)]
    old = [retired(runs[i:i + W]) for i in range(len(runs) - W + 1)]
    chron = vals[::-1]
    need = max(round(chron[i] - max(chron[:i]), 3) for i in range(1, len(chron)))
    base, record = vals[0], max(vals)
    print(f"1. record: {len(runs)} runs, {len(vals)} windows of {W}; grade {base}; "
          f"windows {min(vals)}..{record} (retired {min(old)}..{max(old)}); "
          f"record {record}, budget {budgets['critical_path_minutes']}; "
          f"band need {need}, band {budgets['critical_path_minutes_band']}")
    ok &= record == budgets["critical_path_minutes"]
    ok &= need <= budgets["critical_path_minutes_band"]

    print("2. outlier: the newest run's lane at 3.2x the window's fastest (new / retired)")
    for lane in LANES:
        fastest = min(x for x in (work_s(r, lane) for r in runs[:W]) if x)
        w = [with_work(runs[0], lane, lambda _x: 3.2 * fastest)] + runs[1:W]
        d, dr = round(new(w) - base, 3), round(retired(w) - old[0], 3)
        print(f"   {lane}: {d:+} / {dr:+}")
        ok &= d == 0

    print("3. growth: +300 s on a lane in the newest k runs (new / retired)")
    for lane in LANES[:2]:
        row = []
        for k in (1, 4, 8, 12, 15, 16):
            w = [with_work(r, lane, lambda x: x + 300) for r in runs[:k]] + runs[k:W]
            d, dr = round(new(w) - base, 3), round(retired(w) - old[0], 3)
            row.append(f"k={k} {d:+}/{dr:+}")
            if k == W:
                ok &= d >= 3.0
        print(f"   {lane}: " + "  ".join(row))

    print("4. slow fleet: each fast draw in the newest 15 runs made 1.9x (disclosed)")
    for lane in LANES:
        w = [with_work(r, lane, lambda x, t=FAST_BELOW_S[lane]: x * 1.9 if x < t else x)
             for r in runs[:15]] + runs[15:W]
        print(f"   {lane}: {round(new(w) - base, 3):+}")

    print("RESULT:", "holds" if ok else "does NOT hold")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
