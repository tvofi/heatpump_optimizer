#!/usr/bin/env python3
"""Derive PROBE_REFERENCE_S from probed runs on the hosted fleet itself.

    python3 tools/audit/seat/probe_bridge.py                 # the committed fleet record
    python3 tools/audit/seat/probe_bridge.py --repo OWNER/NAME [--last 16]   # live push runs
    python3 tools/audit/seat/probe_bridge.py --self-test

tests/ci_ratchet.py prices a probed job at wall * PROBE_REFERENCE_S[python] /
its probe's seconds, and PROBE_REFERENCE_S is the probe's seconds on the
REFERENCE HOST: the fleet's fast class (UNIT, below), the host the shipped
grade priced each heavy lane on, so critical_path_minutes keeps its unit.
Only the fleet can set it. The probe is pure Python and the fast lane's
scripts are solver-heavy, so the probe-to-script ratio is per machine: one
local bridge implied 17.50, another 18.29, and the fleet 22.4
(review of #3201 at 10e05b94f).

THE RULE, over probed runs (newest first):
  3.14  each `tests / fast (3.14)` job carrying a successful probe step and
        its scripts' seconds: its host factor is the median, over the
        scripts of >= 20 s in fast_scripts.json, of seconds / that script's
        60-run median; it implies reference = probe * UNIT / factor, UNIT
        the fast class's median factor (factors under 0.65, replay.py's).
        PROBE_REFERENCE_S["3.14"] is the median implied reference.
  3.13  no 3.13 job logs scripts with a 60-run history, so 3.13 is 3.14's
        reference times the interpreters' probe ratio on the fleet: the
        median ratio of the 3.13 and 3.14 heavy jobs' probe seconds paired
        by rank (each sample's quantiles at (k + 0.5) / n, n the smaller
        count). Every heavy job draws from the same fleet, so the two
        samples differ by the interpreter's scale; pairing by rank keeps a
        two-class mix (probes 22-24 s and 38-40 s on 3.14) from landing a
        median in the gap between the classes.
A job's scripts come from its record (`scripts_s`) or its log: tests/run.sh's
per-script `[HH:MM:SS] ok ... (Ns)` lines, or its closing wall-clock table
(`   367s  python3 tests/stress.py`), the one a log's tail always holds.

The fleet record (dev/audit/harnesses/r10_hotfix_ci_critpath_4/fleet.json)
is the probed runs the tree's PROBE_REFERENCE_S was derived from, cut to
ci_ratchet's run fields plus the fast lane's `scripts_s`. --self-test
re-derives the tree's values from it and refuses a difference over the
rounding: a constant moved without a fleet measurement turns governance's
`instrument-self-tests` red on the pull request that moves it.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests import ci_ratchet as cr  # noqa: E402

HARNESS = ROOT / "dev/audit/harnesses/r10_hotfix_ci_critpath_4"
FLEET = HARNESS / "fleet.json"
LANE = "tests / fast (3.14)"
MIN_SCRIPT_S = 20
FAST_CLASS_BELOW = 0.65
ROUNDING = 0.005   # PROBE_REFERENCE_S is kept to 2 decimals
OK = re.compile(r"\]\s+ok\s+(.+?) \((\d+)s\)\s*$")
ROW = re.compile(r"^\S*\s+(\d+)s  (.+?)\s*$")


def references(scripts: dict) -> tuple[dict, float]:
    """Each heavy script's 60-run median, and UNIT, from fast_scripts.json."""
    keys = {k for s in scripts.values() for k in s}
    ref = {k: statistics.median([s[k] for s in scripts.values() if k in s]) for k in keys}
    ref = {k: v for k, v in ref.items() if v >= MIN_SCRIPT_S}
    factors = [statistics.median([s[k] / ref[k] for k in ref if s.get(k)]) for s in scripts.values()]
    return ref, statistics.median([f for f in factors if f < FAST_CLASS_BELOW])


def log_seconds(text: str) -> dict:
    """Script seconds from a tests/run.sh log: its `ok` lines, else its
    wall-clock table (a 5000-line tail holds only the table)."""
    out, table = {}, {}
    for line in text.splitlines():
        m = OK.search(line)
        if m:
            out[re.sub(r"\b[0-9a-f]{40}\b", "SHA", m.group(1))] = int(m.group(2))
            continue
        m = ROW.match(line)
        if m and not m.group(2).startswith("TOTAL"):
            table[re.sub(r"\b[0-9a-f]{40}\b", "SHA", m.group(2))] = int(m.group(1))
    return {**table, **out}


def probe_s(job: dict) -> "tuple[str, float] | None":
    for s in job.get("steps") or []:
        name = str(s.get("name") or "")
        if name.startswith(cr.PROBE_STEP) and s.get("conclusion") == "success" \
                and s.get("started_at") and s.get("completed_at"):
            secs = (cr._at(s["completed_at"]) - cr._at(s["started_at"])).total_seconds()
            if secs > 0:
                return name[len(cr.PROBE_STEP):].strip().removeprefix("(python ").removesuffix(")"), secs
    return None


def _quantile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    pos = q * len(xs) - 0.5
    lo = max(0, min(len(xs) - 1, int(pos // 1)))
    hi = min(len(xs) - 1, lo + 1)
    frac = min(1.0, max(0.0, pos - lo))
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def rank_ratio(num: list[float], den: list[float]) -> float:
    """The median ratio of num to den paired by rank (module docstring)."""
    n = min(len(num), len(den))
    return statistics.median(_quantile(num, (k + 0.5) / n) / _quantile(den, (k + 0.5) / n)
                             for k in range(n))


def bridge(runs: list[dict], scripts_of, ref: dict, unit: float) -> dict:
    """The implied references over runs (newest first); scripts_of(job) ->
    that job's script seconds. A probe step that succeeded measured its
    host whatever the job's later steps did; only a successful fast lane
    implies a reference (its scripts all ran)."""
    implied, by_py = [], {}
    for r in runs:
        for j in r.get("jobs") or []:
            p = probe_s(j)
            if p is None:
                continue
            by_py.setdefault(p[0], []).append(p[1])
            if j.get("name") != LANE or j.get("conclusion") != "success":
                continue
            secs = scripts_of(j)
            ratios = [secs[k] / ref[k] for k in ref if secs.get(k)]
            if len(ratios) >= len(ref) // 2:
                implied.append(p[1] * unit / statistics.median(ratios))
    if not implied:
        raise SystemExit("probe_bridge: no probed fast (3.14) run with its script lines; nothing to derive")
    r14 = statistics.median(implied)
    out = {"runs": len(implied), "3.14": round(r14, 2),
           "spread": (round(min(implied), 2), round(max(implied), 2)),
           "implied": [round(x, 2) for x in implied]}
    if by_py.get("3.13") and by_py.get("3.14"):
        out["ratio"] = round(rank_ratio(by_py["3.13"], by_py["3.14"]), 4)
        out["3.13"] = round(r14 * out["ratio"], 2)
        out["probes"] = {k: sorted(v) for k, v in sorted(by_py.items())}
    return out


def from_record(path: Path = FLEET) -> dict:
    """bridge() over a fleet record, with fast_scripts.json's references."""
    runs = json.loads(path.read_text())["workflow_runs"]
    ref, unit = references(json.loads((HARNESS / "fast_scripts.json").read_text()))
    got = bridge(runs, lambda j: j.get("scripts_s") or {}, ref, unit)
    got["unit"] = round(unit, 4)
    return got


def disagreement(derived: dict, tree: dict) -> list[str]:
    """Each interpreter whose tree value is not the derived one."""
    return [f"{py}: tree {tree.get(py)} derived {derived.get(py)}"
            for py in ("3.13", "3.14")
            if derived.get(py) is None or tree.get(py) is None
            or abs(derived[py] - tree[py]) > ROUNDING]


def job_log(repo: str, job_id) -> str:
    """One Actions job's log through merge_train.job_log, the one reader that
    passes gh's escape-sequence flag where gh knows it."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import merge_train
    text = merge_train.job_log(None, repo, job_id)
    if text is None:
        raise SystemExit(f"probe_bridge: the log of job {job_id} could not be read")
    return text


def self_test() -> int:
    ref = {"python3 tests/a.py": 100.0, "python3 tests/b.py": 200.0}
    unit = 0.5

    def run(i, factor, probe, python="3.14", lane=LANE):
        return {"id": i, "jobs": [{"id": i, "name": lane, "conclusion": "success", "steps": [
            {"name": f"{cr.PROBE_STEP} (python {python})", "conclusion": "success",
             "started_at": "2026-11-05T00:00:00Z", "completed_at": f"2026-11-05T00:00:{probe:02d}Z"}],
            "_log": "\n".join(f"  [00:00:00] ok     {k} ({round(v * factor)}s)" for k, v in ref.items())}]}
    runs = [run(1, 1.0, 40), run(2, 0.5, 20), run(3, 1.0, 40)]
    logs = {r["id"]: r["jobs"][0]["_log"] for r in runs}

    def of(logs):
        return lambda j: log_seconds(logs.get(j["id"], ""))
    got = bridge(runs, of(logs), ref, unit)
    checks = [("a probe of 40 s on a factor-1 host and 20 s on a factor-0.5 host both imply 20 s "
               "on the UNIT (0.5) host", got["3.14"] == 20.0 and got["spread"] == (20.0, 20.0)),
              ("a run whose fast lane logged no script lines implies nothing (its null)",
               bridge(runs + [run(4, 1.0, 10)], of({**logs, 4: ""}), ref, unit)["3.14"] == 20.0)]
    table = ("2026-11-04T15:45:31.6Z ########## wall clock ##########\n"
             "2026-11-04T15:45:31.6Z       100s  python3 tests/a.py\n"
             "2026-11-04T15:45:31.6Z       200s  python3 tests/b.py\n"
             "2026-11-04T15:45:31.7Z      1900s  TOTAL (3 lane(s))")
    checks.append(("a log tail holding only the wall-clock table reads the same seconds",
                   log_seconds(table) == {"python3 tests/a.py": 100, "python3 tests/b.py": 200}
                   and bridge([run(1, 1.0, 40)], of({1: table}), ref, unit)["3.14"] == 20.0))
    runs13 = runs + [{"id": 9, "jobs": [{"id": 9, "name": "tests / closures", "conclusion": "success",
                                         "steps": run(9, 1, 44, "3.13")["jobs"][0]["steps"]}]}]
    g13 = bridge(runs13, of(logs), ref, unit)
    checks.append(("3.13 is 3.14's reference times the rank-paired probe ratio",
                   g13.get("3.13") == round(20.0 * rank_ratio([44], [40, 20, 40]), 2)
                   and g13["3.13"] != g13["3.14"]))
    two_class_14, two_class_13 = [22, 24, 32, 39, 39, 40], [22, 22, 38, 38, 39, 39]
    checks.append(("a two-class mix pairs by rank (0.987), where a median of medians lands in the "
                   "gap (38 / 35.5 = 1.070)",
                   abs(rank_ratio(two_class_13, two_class_14) - 0.987) < 0.001
                   and abs(statistics.median(two_class_13) / statistics.median(two_class_14) - 1.070) < 0.001))
    try:
        bridge([run(5, 1.0, 40, lane="tests / closures")], of(logs), ref, unit)
        checks.append(("no probed fast lane refuses", False))
    except SystemExit:
        checks.append(("no probed fast lane refuses", True))
    # The pin: the tree's constant is the fleet's, by this rule, from the
    # committed record. Its null control: the one-machine bridge's 17.50 /
    # 18.92, 21 % under the fleet, is refused by the same comparison.
    fleet = from_record()
    bad = disagreement(fleet, cr.PROBE_REFERENCE_S)
    checks.append((f"the committed fleet record ({fleet['runs']} probed fast (3.14) runs) re-derives "
                   f"tests/ci_ratchet.py's PROBE_REFERENCE_S {cr.PROBE_REFERENCE_S}"
                   + (f" -- {'; '.join(bad)}" if bad else ""), not bad))
    checks.append(("the one-machine bridge's 17.50 / 18.92 is refused by the same comparison",
                   len(disagreement(fleet, {"3.13": 18.92, "3.14": 17.50})) == 2))
    for name, ok in checks:
        print(f"  {'ok' if ok else 'FAIL'}   {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"probe_bridge self-test: {len(checks)} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--last", type=int, default=cr.PUSH_WINDOW)
    ap.add_argument("--fleet", type=Path, default=FLEET)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.repo:
        got = from_record(a.fleet)
        print(f"probe_bridge: {a.fleet.name}: {got['runs']} probed fast (3.14) runs imply 3.14 "
              f"{got['implied']} -> {got['3.14']}; probes {got.get('probes')}; 3.13/3.14 rank ratio "
              f"{got.get('ratio')} -> 3.13 {got.get('3.13')}; UNIT {got['unit']}; in the tree "
              f"{cr.PROBE_REFERENCE_S}: {'; '.join(disagreement(got, cr.PROBE_REFERENCE_S)) or 'agree'}")
        return 0
    import os
    import tempfile
    os.environ["GITHUB_REPOSITORY"] = a.repo
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "runs.json"
        cr.gather_runs(f, repo=a.repo, window=a.last)
        runs = [r for r in json.loads(f.read_text())["workflow_runs"] if r.get("status") == "completed"]
    ref, unit = references(json.loads((HARNESS / "fast_scripts.json").read_text()))
    got = bridge(runs, lambda j: log_seconds(job_log(a.repo, j["id"])), ref, unit)
    print(f"probe_bridge: {got['runs']} probed fast (3.14) push runs; PROBE_REFERENCE_S implied "
          f"3.14 {got['3.14']} (runs {got['spread'][0]}..{got['spread'][1]}), 3.13 {got.get('3.13')}; "
          f"in the tree {cr.PROBE_REFERENCE_S}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
