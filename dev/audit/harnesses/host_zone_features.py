#!/usr/bin/env python3
"""host_zone_features.py -- run suite scripts under several zones (R10-SUITE-HOST-DETERMINISM).

The stub's ``DEFAULT_TIME_ZONE`` is Home Assistant's configured zone, read
from ``HASTUB_TZ``; the process zone is ``TZ``. A check that names an instant
as a naive or UTC literal, while production reads the configured zone's wall
clock, passes under UTC and fails under some other zone. This harness runs
the script once per zone, with both variables set to it, in parallel, and
prints one RESULT line per zone; it exits 1 when any zone is red.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/host_zone_features.py
    python3 dev/audit/harnesses/host_zone_features.py --mutant all

    python3 dev/audit/harnesses/host_zone_features.py --suite --jobs 3

``--suite`` runs every script ``tests/run.sh`` invokes (its ``run`` and
``run_always`` lines, the rule run.sh's own wiring check reads), each under
every zone, and prints one ``RESULT <script>.<zone>`` line per pair and a
``RESULT zone.<zone>=<passed>/<total>`` count per zone. The ``gate`` row is
the gate's own environment (``TZ=UTC``, ``HASTUB_TZ`` unset), the null row.
A script ``tests/gate_lock.py needs-lease`` names ``lease`` measures the
machine, so it runs alone after the pool; no script runs beside itself.

``--golden-zones`` captures every golden payload (``env_drift.py --all``'s
set) under each zone and compares it with the gate row's capture, printing
one ``RESULT null.golden_zones.<zone>`` line per zone: golden.py's own drift
check compares against a baseline captured in the same zone, so it cannot
see a payload that moves with the zone. A ``tests/golden.py`` mutant is read
this way.

``--mutant NAME`` (or ``all``) runs a detached worktree of ``HEAD``
with one fixed site restored to its host-zone read, and reports each mutant
KILLED when at least one zone is red, SURVIVED otherwise; the unmutated run is
the null control. Each run is a full pass of the mutant's script per zone:
minutes, not seconds, so it is not one of ``tests/harness_headers.py``'s
executed headers.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import shlex
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
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


ROOT = repo_root(__file__)
ZONES = ("UTC", "America/New_York", "Asia/Tokyo", "Europe/Stockholm")
# The suite sweep: the gate's own environment, four whole-hour zones, a
# half-hour one, and Europe/London, a DST zone whose 2026 transitions fall on
# the EU dates the suite's own instants read (2026-03-29, 2026-10-25), with a
# winter offset of zero, so a leak shows only across the transition.
SUITE_ZONES = ("gate", "UTC", "America/New_York", "Asia/Tokyo", "Europe/Stockholm",
               "Asia/Kolkata", "Europe/London")
SUMMARY = re.compile(r"(ALL (\d+)|(\d+) of (\d+)) FEATURE CHECKS (PASSED|FAILED)")
FAIL = re.compile(r"^\s*FAIL\b:?\s*(.*)$")
# The card scripts read the plan payload tests/plan_view.py writes, one file
# per tree (run.sh runs plan_view first in their lane): each runs after
# plan_view in its own zone, and the group shares one lock.
PLAN_READERS = ("tests/card.mjs", "tests/setup_qa_render.mjs", "tests/card_drift.mjs")
INVOCATION = re.compile(r'^\s*run(?:_always)? ("\$PYTHON"|node) (tests/\S+)(.*)$')

# Each fixed site, as (file, fixed text, the host-zone read it replaced).
# A mutant is killed when a zone other than UTC reads it red.
MUTANTS = {
    # The instant arm's naive leaves, read as UTC whatever zone the store's
    # loader reads them in: round 2's finite_boundary leak.
    "finite_boundary_leaf_zone": (
        "tests/finite_boundary.py",
        '        zone = getattr(self, "_naive_zone", _dt.timezone.utc) or _dt.timezone.utc\n',
        "        zone = _dt.timezone.utc\n",
    ),
    # The seam check's clock, FROZEN itself again: a naive plan time read in
    # the host zone, off the UTC grid the chunks run on.
    "card_seam_clock": (
        "tests/card.mjs",
        "    const seamNow = Math.floor(FROZEN / CH) * CH + 6 * HOUR;\n",
        "    const seamNow = FROZEN;\n",
    ),
    "guard_idle_cooling": (
        "tests/guard_pins.py",
        "    now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)\n",
        "    now = datetime(2026, 1, 5, 12, 0, 0)\n",
    ),
    # The coordinator scenarios' configured zone, inherited from HASTUB_TZ
    # again: read by --golden-zones, since golden.py's own drift check
    # compares against a baseline captured in the same zone.
    "golden_scenario_zone": (
        "tests/golden.py",
        "    dt_util.DEFAULT_TIME_ZONE = SCENARIO_ZONE\n",
        "    dt_util.DEFAULT_TIME_ZONE = saved_zone\n",
    ),
    # The default-case contract reading the environment for its precondition
    # again, as it did before round 4.
    "ha_contract_default_zone": (
        "tests/ha_contract.py",
        "    assert _unconfigured_zone() is not None\n",
        '    assert __import__("os").environ.get("HASTUB_TZ") is None\n',
    ),
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


#: ``both`` sets the host zone (``TZ``) and Home Assistant's configured zone
#: (``HASTUB_TZ``) together; ``tz`` sets the host zone alone, leaving the
#: configured zone at the stub's default, which isolates a host-time read
#: from a check whose expectation is a function of the configured zone.
AXIS = os.environ.get("HOST_ZONE_AXIS", "both")


def zone_env(tree: Path, zone: str) -> dict:
    env = {**os.environ, "PYTHONPATH": str(tree / "tests" / "hastub"),
           "GOLDEN_MODE": os.environ.get("GOLDEN_MODE", "drift")}
    if zone == "gate":
        env.pop("HASTUB_TZ", None)
        env["TZ"] = "UTC"
    elif AXIS == "tz":
        env.pop("HASTUB_TZ", None)
        env["TZ"] = zone
    else:
        env.update(HASTUB_TZ=zone, TZ=zone)
    return env


def run_zone(tree: Path, script: str, zone: str) -> tuple[str, str, list[str]]:
    proc = subprocess.run([sys.executable, script], cwd=tree, env=zone_env(tree, zone),
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
    if script == "tests/golden.py":
        return golden_zones(tree, zones, label)
    if script != "tests/features.py":
        rows = {(script, z): v for (script, z), v in
                sweep(tree, [suite_command(script)], zones, len(zones)).items()}
        results = [(z, *rows[(script, z)]) for z in zones]
    else:
        with ThreadPoolExecutor(max_workers=len(zones)) as pool:
            results = list(pool.map(lambda z: run_zone(tree, script, z), zones))
    red = False
    for zone, verdict, fails in results:
        print(f"RESULT {label}.{zone.replace('/', '_')}={verdict}", flush=True)
        if not verdict.startswith("pass"):
            red = True
            for name in fails[:12]:
                print(f"  FAIL {name}")
    return red


# Every golden payload env_drift.py --all captures, as JSON on stdout.
GOLDEN_CAPTURE = (
    "import json, sys\n"
    "sys.path[:0] = ['tests', 'custom_components']\n"
    "import golden\n"
    "p = {n: golden.capture(n, s) for n, s in golden.SCENARIOS.items()}\n"
    "p.update((n, golden.capture_coordinator(c))"
    " for n, c in golden.coordinator_scenarios().items())\n"
    "p['config_flow'] = golden.capture_config_flow()\n"
    "print(json.dumps(p, sort_keys=True, default=str))\n"
)


def golden_zones(tree: Path, zones: tuple[str, ...], label: str) -> bool:
    """Whether any zone's golden payloads differ from the gate row's.

    golden.py's own drift check compares a capture with a baseline captured
    in the same zone, so a payload that moves with the zone on both sides
    reads equal there; this compares each zone with the gate's environment.
    Prints one RESULT per zone naming the payloads that moved.
    """
    def capture(zone):
        proc = subprocess.run([sys.executable, "-c", GOLDEN_CAPTURE], cwd=tree,
                              env=zone_env(tree, zone), capture_output=True,
                              text=True, check=False, stdin=subprocess.DEVNULL)
        if proc.returncode:
            return None
        return json.loads(proc.stdout.strip().splitlines()[-1])

    rows = ("gate", *[z for z in zones if z != "gate"])
    with ThreadPoolExecutor(max_workers=len(rows)) as pool:
        got = dict(zip(rows, pool.map(capture, rows)))
    if got["gate"] is None:
        raise SystemExit("golden capture failed in the gate environment")
    red = False
    for zone in rows[1:]:
        if got[zone] is None:
            verdict = "fail(capture)"
        else:
            moved = sorted(k for k in set(got["gate"]) | set(got[zone])
                           if got["gate"].get(k) != got[zone].get(k))
            verdict = (f"pass:{len(got['gate'])} payloads equal to gate" if not moved
                       else f"fail:{len(moved)}/{len(got['gate'])} {','.join(moved)}")
        red = red or not verdict.startswith("pass")
        print(f"RESULT {label}.golden_zones.{zone.replace('/', '_')}={verdict}", flush=True)
    return red


def suite_commands(tree: Path) -> list[list[str]]:
    """Every script tests/run.sh invokes, with its arguments, once each."""
    out, seen = [], set()
    for line in (tree / "tests" / "run.sh").read_text().splitlines():
        m = INVOCATION.match(line)
        if not m:
            continue
        runner, script, rest = m.groups()
        cmd = [sys.executable if runner == '"$PYTHON"' else "node", script,
               *(a.replace("$GOLDEN_REF", os.environ.get("GOLDEN_REF", "origin/main"))
                 for a in shlex.split(rest))]
        if tuple(cmd) not in seen:
            seen.add(tuple(cmd))
            out.append(cmd)
    return out


def suite_command(script: str) -> list[str]:
    return [sys.executable if script.endswith(".py") else "node", script]


def _label(cmd: list[str]) -> str:
    return " ".join(cmd[1:])


def _run_cmd(tree: Path, cmd: list[str], zone: str) -> tuple[str, list[str]]:
    if cmd[1] in PLAN_READERS:
        pre = subprocess.run([sys.executable, "tests/plan_view.py"], cwd=tree,
                             env=zone_env(tree, zone), capture_output=True, text=True,
                             check=False, stdin=subprocess.DEVNULL)
        if pre.returncode:
            return f"fail(plan_view rc={pre.returncode}) :: ", []
    proc = subprocess.run(cmd, cwd=tree, env=zone_env(tree, zone), capture_output=True,
                          text=True, check=False, stdin=subprocess.DEVNULL)
    out = proc.stdout + proc.stderr
    lines = [ln.strip() for ln in out.splitlines() if re.search(r"PASSED|FAILED", ln)]
    tail = lines[-1][:90] if lines else ""
    fails = [m.group(1) for ln in out.splitlines() if (m := FAIL.match(ln))]
    word = "pass" if proc.returncode == 0 else f"fail(rc={proc.returncode})"
    return f"{word} :: {tail}", fails


def _needs_lease(tree: Path, script: str) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write(script + "\n")
    try:
        got = subprocess.run([sys.executable, "tests/gate_lock.py", "needs-lease", fh.name],
                             cwd=tree, capture_output=True, text=True, check=False)
    finally:
        os.unlink(fh.name)
    return got.stdout.strip() == "lease"


def sweep(tree: Path, cmds: list[list[str]], zones: tuple[str, ...], jobs: int) -> dict:
    """(script label, zone) -> (verdict, fails); prints each as it lands."""
    group = threading.Lock()
    locks = {_label(c): group if c[1] in PLAN_READERS or c[1] == "tests/plan_view.py"
             else threading.Lock() for c in cmds}
    alone = [c for c in cmds if _needs_lease(tree, c[1])]
    pooled = [(c, z) for z in zones for c in cmds if c not in alone]
    results: dict = {}
    printing = threading.Lock()

    def one(item):
        cmd, zone = item
        with locks[_label(cmd)]:
            verdict, fails = _run_cmd(tree, cmd, zone)
        results[(_label(cmd), zone)] = (verdict, fails)
        with printing:
            print(f"RESULT {_label(cmd)}.{zone.replace('/', '_')}={verdict}", flush=True)
            if not verdict.startswith("pass"):
                for name in fails[:12]:
                    print(f"  FAIL {name}", flush=True)

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(one, pooled))
    for zone in zones:
        for cmd in alone:
            one((cmd, zone))
    return results


def suite_main(tree: Path, zones: tuple[str, ...], jobs: int) -> bool:
    cmds = suite_commands(tree)
    results = sweep(tree, cmds, zones, jobs)
    red = False
    for zone in zones:
        passed = sum(results[(_label(c), zone)][0].startswith("pass") for c in cmds)
        red = red or passed != len(cmds)
        print(f"RESULT zone.{zone.replace('/', '_')}={passed}/{len(cmds)}", flush=True)
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
    ap.add_argument("--suite", action="store_true",
                    help="every script tests/run.sh invokes, under the suite zones")
    ap.add_argument("--golden-zones", action="store_true",
                    help="every golden payload per zone, against the gate row")
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args()
    zones = tuple(z for z in args.zones.split(",") if z)
    if args.suite:
        if args.zones == ",".join(ZONES):
            zones = SUITE_ZONES
        return 1 if suite_main(ROOT, zones, args.jobs) else 0
    if args.golden_zones and not args.mutant:
        return 1 if golden_zones(ROOT, zones, "null") else 0
    if not args.mutant:
        return 1 if run_tree(ROOT, args.script, zones, "null") else 0
    names = list(MUTANTS) if args.mutant == "all" else [args.mutant]
    survived = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            tree = mutant_tree(name, Path(tmp))
            try:
                red = run_tree(tree, MUTANTS[name][0], zones, name)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                               cwd=ROOT, check=False)
            print(f"RESULT mutant.{name}={'KILLED' if red else 'SURVIVED'}", flush=True)
            if not red:
                survived.append(name)
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
