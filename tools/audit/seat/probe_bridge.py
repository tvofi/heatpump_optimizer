#!/usr/bin/env python3
"""Re-derive PROBE_REFERENCE_S from probed push runs on the hosted fleet itself.

    python3 tools/audit/seat/probe_bridge.py --repo OWNER/NAME [--last 16]
    python3 tools/audit/seat/probe_bridge.py --self-test

R10-HOTFIX-CI-CRITPATH-4 set tests/ci_ratchet.py's PROBE_REFERENCE_S -- the
probe step's seconds on the reference host -- by a bridge measured on one
machine (dev/audit/harnesses/r10_hotfix_ci_critpath_4/bridge.json), whose two
solo scripts read that machine at 0.72 and 0.87 of the fleet's factor-1 host:
a cross-machine bridge carries ~9 % of uncertainty. A probed push run removes
it: its `tests / fast (3.14)` job runs the probe AND the 13 scripts whose
60-run medians define the host factor (replay.py section 2), on one runner.

THE RULE. Over the newest `--last` completed push runs whose fast (3.14) job
carries a successful probe step: the job log's tests/run.sh `ok ... (Ns)`
lines give each script's seconds; the run's factor is the median, over the
scripts of >= 20 s in fast_scripts.json, of seconds / that script's 60-run
median; the run implies reference = probe seconds * UNIT / factor, UNIT the
fast class's median factor (replay.py's). PROBE_REFERENCE_S["3.14"] is the
median implied reference; ["3.13"] is it times the median 3.13 probe over the
median 3.14 probe across the same runs' heavy jobs (the fleet's mix is the
same for every lane, so the ratio is the interpreters'). It prints both with
the tree's, and the spread; it changes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests import ci_ratchet as cr  # noqa: E402

HARNESS = ROOT / "dev/audit/harnesses/r10_hotfix_ci_critpath_4"
LANE = "tests / fast (3.14)"
MIN_SCRIPT_S = 20
FAST_CLASS_BELOW = 0.65
OK = re.compile(r"\]\s+ok\s+(.+?) \((\d+)s\)\s*$")


def references(scripts: dict) -> tuple[dict, float]:
    """Each heavy script's 60-run median, and UNIT, from fast_scripts.json."""
    keys = {k for s in scripts.values() for k in s}
    ref = {k: statistics.median([s[k] for s in scripts.values() if k in s]) for k in keys}
    ref = {k: v for k, v in ref.items() if v >= MIN_SCRIPT_S}
    factors = [statistics.median([s[k] / ref[k] for k in ref if s.get(k)]) for s in scripts.values()]
    return ref, statistics.median([f for f in factors if f < FAST_CLASS_BELOW])


def log_seconds(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        m = OK.search(line)
        if m:
            out[re.sub(r"\b[0-9a-f]{40}\b", "SHA", m.group(1))] = int(m.group(2))
    return out


def probe_s(job: dict) -> "tuple[str, float] | None":
    for s in job.get("steps") or []:
        name = str(s.get("name") or "")
        if name.startswith(cr.PROBE_STEP) and s.get("conclusion") == "success" \
                and s.get("started_at") and s.get("completed_at"):
            secs = (cr._at(s["completed_at"]) - cr._at(s["started_at"])).total_seconds()
            if secs > 0:
                return name[len(cr.PROBE_STEP):].strip().removeprefix("(python ").removesuffix(")"), secs
    return None


def bridge(runs: list[dict], log_of, ref: dict, unit: float) -> dict:
    """The implied references over runs (newest first), log_of(job id) -> text."""
    implied, by_py = [], {}
    for r in runs:
        for j in r.get("jobs") or []:
            p = probe_s(j) if j.get("conclusion") == "success" else None
            if p is None:
                continue
            by_py.setdefault(p[0], []).append(p[1])
            if j.get("name") != LANE:
                continue
            secs = log_seconds(log_of(j["id"]))
            ratios = [secs[k] / ref[k] for k in ref if secs.get(k)]
            if len(ratios) >= len(ref) // 2:
                implied.append(p[1] * unit / statistics.median(ratios))
    if not implied:
        raise SystemExit("probe_bridge: no probed fast (3.14) run with its script lines; nothing to derive")
    r14 = statistics.median(implied)
    out = {"runs": len(implied), "3.14": round(r14, 2),
           "spread": (round(min(implied), 2), round(max(implied), 2))}
    if by_py.get("3.13") and by_py.get("3.14"):
        out["3.13"] = round(r14 * statistics.median(by_py["3.13"]) / statistics.median(by_py["3.14"]), 2)
    return out


def gh(path: str) -> str:
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"probe_bridge: gh api {path} failed: {p.stderr.strip()[:300]}")
    return p.stdout


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
    got = bridge(runs, logs.get, ref, unit)
    checks = [("a probe of 40 s on a factor-1 host and 20 s on a factor-0.5 host both imply 20 s "
               "on the UNIT (0.5) host", got["3.14"] == 20.0 and got["spread"] == (20.0, 20.0)),
              ("a run whose fast lane logged no script lines implies nothing (its null)",
               bridge(runs + [run(4, 1.0, 10)], {**logs, 4: ""}.get, ref, unit)["3.14"] == 20.0)]
    runs13 = runs + [{"id": 9, "jobs": [{"id": 9, "name": "tests / closures", "conclusion": "success",
                                         "steps": run(9, 1, 44, "3.13")["jobs"][0]["steps"]}]}]
    g13 = bridge(runs13, logs.get, ref, unit)
    checks.append(("3.13 is 3.14's reference times the median probe ratio (44 / 40)",
                   g13.get("3.13") == 22.0))
    try:
        bridge([run(5, 1.0, 40, lane="tests / closures")], logs.get, ref, unit)
        checks.append(("no probed fast lane refuses", False))
    except SystemExit:
        checks.append(("no probed fast lane refuses", True))
    for name, ok in checks:
        print(f"  {'ok' if ok else 'FAIL'}   {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"probe_bridge self-test: {len(checks)} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--last", type=int, default=cr.PUSH_WINDOW)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.repo:
        ap.error("--repo is required")
    import os
    import tempfile
    os.environ["GITHUB_REPOSITORY"] = a.repo
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "runs.json"
        cr.gather_runs(f, repo=a.repo, window=a.last)
        runs = [r for r in json.loads(f.read_text())["workflow_runs"] if r.get("status") == "completed"]
    ref, unit = references(json.loads((HARNESS / "fast_scripts.json").read_text()))
    got = bridge(runs, lambda jid: gh(f"repos/{a.repo}/actions/jobs/{jid}/logs"), ref, unit)
    print(f"probe_bridge: {got['runs']} probed fast (3.14) runs; PROBE_REFERENCE_S implied "
          f"3.14 {got['3.14']} (runs {got['spread'][0]}..{got['spread'][1]}), 3.13 {got.get('3.13')}; "
          f"in the tree {cr.PROBE_REFERENCE_S}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
