#!/usr/bin/env python3
"""host_zone_features.py -- run tests/features.py under several zones (R10-SUITE-HOST-DETERMINISM).

The stub's ``DEFAULT_TIME_ZONE`` is Home Assistant's configured zone, read
from ``HASTUB_TZ``; the process zone is ``TZ``. A check that names an instant
as a naive or UTC literal, while production reads the configured zone's wall
clock, passes under UTC and fails under some other zone. This harness runs
the script once per zone, with both variables set to it, in parallel, and
prints one RESULT line per zone; it exits 1 when any zone is red.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/host_zone_features.py
    python3 dev/audit/harnesses/host_zone_features.py --mutant all

``--mutant NAME`` (or ``all``) runs a detached worktree of ``HEAD``
with one fixed site restored to its host-zone read, and reports each mutant
KILLED when at least one zone is red, SURVIVED otherwise; the unmutated run is
the null control. Each run is a full features.py pass per zone: minutes, not
seconds, so it is not one of ``tests/harness_headers.py``'s executed headers.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ZONES = ("UTC", "America/New_York", "Asia/Tokyo", "Europe/Stockholm")
SUMMARY = re.compile(r"(ALL (\d+)|(\d+) of (\d+)) FEATURE CHECKS (PASSED|FAILED)")
FAIL = re.compile(r"^\s*FAIL\s+(.*)$")

# Each fixed site, as (file, fixed text, the host-zone read it replaced).
# A mutant is killed when a zone other than UTC reads it red.
MUTANTS = {
    "nometer_month": (
        "tests/features.py",
        "    zone = _bo_dt.DEFAULT_TIME_ZONE\n",
        "    zone = _BO_TZ\n",
    ),
    "sysid_night_t0": (
        "tests/features.py",
        "    t0 = datetime(2026, 1, 5, 2, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)\n",
        "    t0 = datetime(2026, 1, 5, 2, 0, tzinfo=UTC)\n",
    ),
    "outage_naive_tick": (
        "tests/features.py",
        "    .astimezone(dt_util.DEFAULT_TIME_ZONE).replace(tzinfo=None).isoformat()\n",
        "    .replace(tzinfo=None).isoformat()\n",
    ),
    "humidity_now": (
        "tests/features.py",
        "_T6_HUM_NOW = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)\n",
        "_T6_HUM_NOW = datetime(2026, 2, 1, 12, 0, 0)\n",
    ),
}


def run_zone(tree: Path, script: str, zone: str) -> tuple[str, str, list[str]]:
    env = {**os.environ, "HASTUB_TZ": zone, "TZ": zone,
           "PYTHONPATH": str(tree / "tests" / "hastub")}
    proc = subprocess.run([sys.executable, script], cwd=tree, env=env,
                          capture_output=True, text=True, check=False)
    out = proc.stdout + proc.stderr
    found = SUMMARY.findall(out)
    if not found:
        return zone, f"no-summary(rc={proc.returncode})", []
    whole, _all, bad, total, verdict = found[-1]
    fails = [m.group(1) for line in out.splitlines() if (m := FAIL.match(line))]
    if verdict == "PASSED":
        return zone, f"pass:{_all}", fails
    return zone, f"fail:{bad}/{total}", fails


def run_tree(tree: Path, script: str, zones: tuple[str, ...], label: str) -> bool:
    with ThreadPoolExecutor(max_workers=len(zones)) as pool:
        results = list(pool.map(lambda z: run_zone(tree, script, z), zones))
    red = False
    for zone, verdict, fails in results:
        print(f"RESULT {label}.{zone.replace('/', '_')}={verdict}", flush=True)
        if not verdict.startswith("pass:"):
            red = True
            for name in fails:
                print(f"  FAIL {name}")
    return red


def mutant_tree(name: str, workdir: Path) -> Path:
    path, fixed, host_read = MUTANTS[name]
    # A detached worktree, not a ``git archive`` copy: features.py's #363
    # check reads ``recorded_at`` from git, and an archive reads it red on
    # every mutant, the null included.
    tree = workdir / name
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(tree), "HEAD"],
                   cwd=ROOT, check=True)
    target = tree / path
    text = target.read_text()
    if text.count(fixed) != 1:
        raise SystemExit(f"mutant {name}: the fixed text is not in {path} exactly once")
    target.write_text(text.replace(fixed, host_read))
    return tree


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="tests/features.py")
    ap.add_argument("--zones", default=",".join(ZONES))
    ap.add_argument("--mutant", choices=[*MUTANTS, "all"])
    args = ap.parse_args()
    zones = tuple(z for z in args.zones.split(",") if z)
    if not args.mutant:
        return 1 if run_tree(ROOT, args.script, zones, "null") else 0
    names = list(MUTANTS) if args.mutant == "all" else [args.mutant]
    survived = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            tree = mutant_tree(name, Path(tmp))
            try:
                red = run_tree(tree, args.script, zones, name)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                               cwd=ROOT, check=False)
            print(f"RESULT mutant.{name}={'KILLED' if red else 'SURVIVED'}", flush=True)
            if not red:
                survived.append(name)
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
