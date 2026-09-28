#!/usr/bin/env python3
"""The #195 tranche partition, derived from the tree rather than read off a list.

#505 is what happens when a partition is a list of module names: the roster named
climate.py / open_meteo.py / frontend.py (W5-G5), diagnosis.py / curve_learning.py /
grid_fee.py / switch.py (W5-G6) and coordinator.py (W5-G7), the tree moved, and the
below-bar tail belonged to no tranche. How long that tail is at any commit is what this
script prints -- it had already grown past the count #505 recorded by the time #505 was
read, which is the defect restating itself. A fresher list has the same defect one merge
later, so what this encodes is a *predicate* whose complement is a real tranche.

THE RULE, in full:

    A module of custom_components/heatpump_optimizer/ is below the bar when its
    statement coverage, measured by tools/audit/w5-partition/coverage_tree.sh, is
    below BAR. Every below-bar module belongs to exactly one #195 tranche:

        coordinator.py  -> W5-G7
        everything else -> W5-G8, the residual

    W5-G8 is not a name list. It is the complement, so the partition is total by
    construction and stays total when a module is added, renamed, or crosses the
    bar in either direction. A seat takes its scope by running this script at its
    own merge base, never by reading a list out of a roster string.

Two conditions are refused, and each is reachable:

  1. The roster does not carry the residual group. The predicate above is total only
     while a group exists to receive it; delete W5-G8 from the roster and the
     partition silently stops covering the tail again, which is #505 exactly. The
     refusal makes that edit fail rather than pass quietly.
  2. A module a *done* tranche drove to the bar is below it again. A done group
     cannot take new work, so such a module lands in W5-G8 and its regression is
     invisible in the roster; naming it here is the only place a reader sees it.

DONE_SCOPES below is a list of names, deliberately and without contradiction: it
records what two merged pull requests actually drove, which is a closed fact, not a
forward scope that the tree can outgrow.

Usage:

    W=$(mktemp -d); W5P_WORK=$W tools/audit/w5-partition/coverage_tree.sh all
    python3 tools/audit/w5-partition/partition.py --coverage $W/out/coverage.json

    --bar F        coverage bar in percent (default 95.0)
    --roster PATH  wave roster to check for the residual group
    --self-test    run the refusals against synthetic inputs and exit
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BAR = 95.0
DEFAULT_ROSTER = REPO_ROOT / ".claude" / "workflows" / "wave-5-groups.json"

COORDINATOR_GROUP = "W5-G7"
RESIDUAL_GROUP = "W5-G8"

# What the merged tranches drove to the bar. A closed fact about two pull requests,
# not a scope: nothing the tree does later can add a module to a group that merged.
DONE_SCOPES = {
    "W5-G5": ("climate.py", "open_meteo.py", "frontend.py"),
    "W5-G6": ("diagnosis.py", "curve_learning.py", "grid_fee.py", "switch.py"),
}


def tranche_for(module: str) -> str:
    """The partition rule. Total over every below-bar module by construction."""
    return COORDINATOR_GROUP if module == "coordinator.py" else RESIDUAL_GROUP


def below_bar(coverage: dict, bar: float) -> list[tuple[str, float, int, int]]:
    """(module, percent, statements, missing) for every module under `bar`."""
    rows = []
    for path, entry in coverage["files"].items():
        summary = entry["summary"]
        pct = summary["percent_covered"]
        if pct < bar:
            rows.append(
                (
                    os.path.basename(path),
                    pct,
                    summary["num_statements"],
                    summary["missing_lines"],
                )
            )
    rows.sort(key=lambda r: (-r[3], r[0]))
    return rows


def roster_groups(roster: dict) -> set[str]:
    return {g.get("group") for g in roster.get("groups", [])}


def run(coverage: dict, roster: dict, bar: float, out) -> int:
    rows = below_bar(coverage, bar)
    groups = roster_groups(roster)
    errors: list[str] = []

    if RESIDUAL_GROUP not in groups:
        errors.append(
            f"the roster carries no {RESIDUAL_GROUP}; the residual predicate has no "
            "group to assign to, so the tail of the below-bar set belongs to nothing "
            "-- this is #505"
        )

    totals = coverage["totals"]
    print(
        f"RESULT coverage_total_pct={totals['percent_covered']:.1f} pct",
        file=out,
    )
    print(f"RESULT coverage_statements={totals['num_statements']} count", file=out)
    print(f"RESULT coverage_missing={totals['missing_lines']} count", file=out)
    print(f"RESULT modules_measured={len(coverage['files'])} count", file=out)
    print(f"RESULT modules_below_bar={len(rows)} count", file=out)

    unassigned = 0
    for module, pct, stmts, missing in rows:
        group = tranche_for(module)
        if group not in groups:
            unassigned += 1
            group = "NONE"
        share = 100.0 * missing / totals["missing_lines"] if totals["missing_lines"] else 0.0
        print(
            f"{module:28s} {pct:6.1f} pct  {stmts:6d} stmts  {missing:5d} missed  "
            f"{share:5.1f} pct of deficit  -> {group}",
            file=out,
        )
    print(f"RESULT modules_unassigned={unassigned} count", file=out)

    at_bar = {r[0] for r in rows}
    for group, modules in sorted(DONE_SCOPES.items()):
        regressed = [m for m in modules if m in at_bar]
        if regressed:
            errors.append(
                f"{group} merged with {', '.join(regressed)} at the bar and they are "
                f"below it again; a done group cannot take new work, so the regression "
                f"lands in {RESIDUAL_GROUP} and nothing in the roster says so"
            )

    for message in errors:
        print(f"REFUSED: {message}", file=out)
    return 1 if errors or unassigned else 0


def _synthetic(files: dict[str, tuple[float, int, int]]) -> dict:
    return {
        "files": {
            f"custom_components/heatpump_optimizer/{name}": {
                "summary": {
                    "percent_covered": pct,
                    "num_statements": stmts,
                    "missing_lines": missing,
                }
            }
            for name, (pct, stmts, missing) in files.items()
        },
        "totals": {
            "percent_covered": 90.0,
            "num_statements": sum(s for _, s, _ in files.values()),
            "missing_lines": sum(m for _, _, m in files.values()),
        },
    }


def self_test() -> int:
    import io

    failures = 0

    def check(name: str, got, want) -> None:
        nonlocal failures
        if got == want:
            print(f"  ok   {name}")
        else:
            failures += 1
            print(f"  FAIL {name}: got {got!r}, want {want!r}")

    full_roster = {"groups": [{"group": COORDINATOR_GROUP}, {"group": RESIDUAL_GROUP}]}
    no_residual = {"groups": [{"group": COORDINATOR_GROUP}]}

    # A module no list ever named is assigned anyway -- the property #505 says the
    # old partition lacked.
    cov = _synthetic({"a_module_nobody_named.py": (0.0, 36, 36)})
    buf = io.StringIO()
    rc = run(cov, full_roster, DEFAULT_BAR, buf)
    check("an unnamed below-bar module is assigned", rc, 0)
    check("...to the residual", f"-> {RESIDUAL_GROUP}" in buf.getvalue(), True)

    # Null control: the same module at the bar is not in the partition at all.
    cov_ok = _synthetic({"a_module_nobody_named.py": (99.0, 36, 0)})
    buf = io.StringIO()
    rc = run(cov_ok, full_roster, DEFAULT_BAR, buf)
    check("an at-bar module is not partitioned", rc, 0)
    check("...and no line names it", "a_module_nobody_named.py" in buf.getvalue(), False)

    # Refusal 1 is reachable: drop the residual group from the roster.
    buf = io.StringIO()
    rc = run(cov, no_residual, DEFAULT_BAR, buf)
    check("a roster without the residual group is refused", rc, 1)
    check("...and the tail is reported unassigned", "modules_unassigned=1" in buf.getvalue(), True)
    # Null control for refusal 1: with only coordinator.py below bar, a roster
    # missing the residual group still assigns every below-bar module...
    cov_coord = _synthetic({"coordinator.py": (83.0, 4071, 688)})
    buf = io.StringIO()
    rc = run(cov_coord, no_residual, DEFAULT_BAR, buf)
    check("...but the missing group is still refused on its own", rc, 1)
    check("...with nothing unassigned", "modules_unassigned=0" in buf.getvalue(), True)

    # Refusal 2 is reachable: a done tranche's module crosses back below the bar.
    cov_regress = _synthetic({"grid_fee.py": (89.4, 199, 21)})
    buf = io.StringIO()
    rc = run(cov_regress, full_roster, DEFAULT_BAR, buf)
    check("a done tranche's module below the bar again is refused", rc, 1)
    check("...naming the module", "grid_fee.py at the bar" in buf.getvalue(), True)
    # Null control for refusal 2: the same module above the bar does not refuse.
    cov_no_regress = _synthetic({"grid_fee.py": (96.0, 199, 8)})
    buf = io.StringIO()
    rc = run(cov_no_regress, full_roster, DEFAULT_BAR, buf)
    check("...and it does not fire when that module is at the bar", rc, 0)

    print(f"{'FAILED' if failures else 'ok'}: partition.py self-test")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage")
    ap.add_argument("--roster", default=str(DEFAULT_ROSTER))
    ap.add_argument("--bar", type=float, default=DEFAULT_BAR)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.coverage:
        ap.error("--coverage PATH is required; coverage_tree.sh writes it under "
                 "W5P_WORK, deliberately outside the worktree")

    with open(args.coverage) as fh:
        coverage = json.load(fh)
    with open(args.roster) as fh:
        roster = json.load(fh)
    return run(coverage, roster, args.bar, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
