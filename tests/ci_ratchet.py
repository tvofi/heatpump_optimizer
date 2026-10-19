#!/usr/bin/env python3
"""The CI ratchet (round-9, tvofi's request): CI cost and code health may only improve.

One-way budgets, in the shape tests/structure.py established: every metric is
DERIVED from a measurement made by this run (never carried by hand), recorded
in tests/ci_budgets.json, and any metric that GREW fails the run. A deliberate
re-record needs --record "<reason>", and the reason belongs in the commit
message (CLAUDE.md rule 2). The inputs are produced by the CI jobs themselves
-- the emitter lines the gate and its instruments already write (run.sh's
scope decision, derive_closures.sh's rec(), coverage_tree.sh's measure()) --
because a ratchet whose input is typed by a human is not a ratchet
(qntm.org/ratchets; Betterer and eslint-seatbelt freeze the same
tool-produced baseline).

THE METRICS, each an answer to a named cost:

  archscore.<m>   tools/audit/archscore's score vector, measured on this
                  tree -- ratcheting THE architecture score's own number,
                  not a second one. Deterministic static counts, tolerance 0.
  script_runs_per_push    instrumented heavy-script executions in a push
                  run (the closures re-derive plus the coverage stage): the
                  "number of script re-runs" the round-9 consolidation
                  pre-study measured (3.8 per merge average, 7 worst case).
                  A `reused` coverage row executes nothing and is not
                  counted. Recorded at the every-script-measured-once count
                  (the closures lane's full plan less the composed script it
                  consumes, plus the coverage `fast` stage), so a push that
                  measures any script twice in one instrument grows it.
  script_runs_full_case_pr   the same count on a full-case pull-request run
                  (every script measured and re-derived once). Scoping's
                  ratchet: what a full-case PR costs may only shrink.
  critical_path_minutes   median wall minutes of the last completed push
                  Tests runs (the GitHub API run list, fetched by the job).
                  A NOISY metric: recorded at the window's p75 for headroom,
                  because shared runners vary far more than the medians do
                  (Bencher documents >30 % variance on shared runners); the
                  ratchet refuses beyond the headroom, not beyond the median.

WHAT IS DELIBERATELY NOT HERE, so nobody re-adds it wrongly:

  * a scoped-FRACTION ratchet. Measured before refusing it: 33 of the last
    60 merges are full-case BY DESIGN (gate files, closures.json, unscoped
    docs each force MODE: FULL -- CLAUDE.md rule 1's push-forces-full is the
    same defensive pattern), so a full-share ratchet would refuse legitimate
    merges the day two gate-file PRs land in one window. The flapping-gate
    and perverse-incentive pitfalls every ratchet source warns about. The
    per-event absolute counts above are the honest form.
  * complexity. tests/structure_budgets.json already ratchets max_cc,
    functions_cc_over_* and the rest, one-way; a second file with the same
    metric would be a duplicate owner. Pylint --fail-under, xenon and
    pitest/Stryker thresholds are the same pattern with one owner each.

Usage (the ci-ratchet job; stdlib only besides the archscore import):

    python3 tests/ci_ratchet.py --metrics-dir DIR [--runs-json FILE]
    python3 tests/ci_ratchet.py --metrics-dir DIR --runs-json FILE \
        --record "reason"

--metrics-dir holds the ci-metrics artifacts of this run and the recent
window, flat: lines of
  <lane>\t<script>\t<full|scoped|reused>\t<rc>\t<seconds>\t<event>\t<run id>
(the event and run id come from the runner environment, so a window's three
lane artifacts of one run group as one run), plus the fast lane's single
<fast>\tmode\t<full|scoped>\t<n_run>\t<n_skip>\t<event>\t<run id>.
--runs-json is the GitHub API workflow-runs listing for critical path.
--record re-records every metric from what was just derived, refusing without
a reason.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGETS = ROOT / "tests" / "ci_budgets.json"
METADATA_KEYS = {"recorded_at", "reason"}

LANES = ("closures", "coverage")


def _finite_number(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def budget_problems(table: dict) -> list[str]:
    """Refuse a table this ratchet cannot honestly grade."""
    problems = []
    if not isinstance(table, dict):
        return ["the table is not an object"]
    if "recorded_at" not in table:
        problems.append("no recorded_at -- a ratchet row must name the tree "
                        "it was measured on")
    counts = ("script_runs_per_push", "script_runs_full_case_pr")
    for key, value in table.items():
        if key in METADATA_KEYS:
            continue
        if not _finite_number(value):
            problems.append(f"{key}={value!r} is not a finite number")
            continue
        if key.startswith("archscore."):
            if not isinstance(value, int) or value < 0:
                problems.append(f"{key}={value!r} is not a non-negative "
                                "integer count")
        elif key in counts:
            if not isinstance(value, int) or value < 0:
                problems.append(f"{key}={value!r} is not a non-negative "
                                "integer count")
        elif key == "critical_path_minutes":
            if not 0 < value <= 600:
                problems.append(f"{key}={value!r} is outside 0..600 minutes")
        else:
            problems.append(f"{key} is not a metric this ratchet knows")
    return problems


def archscore_metrics(only: set[str] | None = None) -> dict[str, int]:
    """The score vector as ratchet keys; ``only`` is vector.measure's job filter (the census arm
    of tools/policy/field_coverage.mjs runs the card job alone)."""
    sys.path.insert(0, str(ROOT / "tools" / "audit"))
    from archscore import vector  # noqa: E402
    return {f"archscore.{k}": v for k, v in vector.measure(ROOT, only).items()}


def file_lane(path: Path) -> str:
    """The lane an artifact file is named for: each job writes its own
    ci-metrics-<lane>.tsv, and the window keeps that basename behind a
    w<artifact id>- prefix. A file naming no lane is refused, not guessed."""
    for lane in ("fast", *LANES):
        if path.name.endswith(f"ci-metrics-{lane}.tsv"):
            return lane
    raise SystemExit(f"ci-ratchet: {path.name} names no lane "
                     "(ci-metrics-<lane>.tsv); its rows cannot be "
                     "attributed (fail closed)")


def read_metrics(metrics_dir: Path) -> dict[tuple[str, str], list[dict]]:
    """Every emitter line, grouped into runs by the (event, run id) every
    line carries: one run's three lane artifacts land as three files, and
    the per-run counts must not read them as three runs.

    A row counts only from its own lane's file. A row of another lane inside
    a file was written by a child of that lane's instrument that inherited
    HPO_CI_METRICS -- closure.py's selftest driving derive_closures.sh under
    a stub put fixture `closures` rows in ci-metrics-fast.tsv, and a nested
    run.sh raced them to 69 on push run 38639862216. The emitters no longer
    export the variable; this keeps the artifacts already in the window, and
    any emitter added later, from being graded as cost."""
    runs: dict[tuple[str, str], list[dict]] = {}
    foreign = 0
    for f in sorted(metrics_dir.rglob("*.tsv")):
        lane = file_lane(f)
        for line in f.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            if parts[0] != lane:
                foreign += 1
                continue
            runs.setdefault((parts[5], parts[6]), []).append(
                {"lane": parts[0], "name": parts[1], "class": parts[2]})
    if foreign:
        print(f"ci-ratchet: not counted: {foreign} row(s) carried by another "
              "lane's artifact (a child that inherited HPO_CI_METRICS)",
              file=sys.stderr)
    return runs


def script_runs(run: list[dict]) -> int:
    """Instrumented script EXECUTIONS in one run. A `reused` coverage row is a
    copy of the base's per-script data, not an execution -- it runs nothing
    -- so it is no script run (R10-CI-LAYOUT PR 0). Counting it graded push
    run 39213675232's 19 copies as 19 runs, 73 against a budget of 68."""
    return sum(1 for r in run if r["lane"] in LANES)


def critical_path_minutes(runs_json: Path) -> float:
    """Median wall minutes over the window's COMPLETED push Tests runs."""
    runs = json.loads(runs_json.read_text())["workflow_runs"]
    minutes = []
    for r in runs:
        if r.get("name") != "Tests" or r.get("status") != "completed":
            continue
        start = datetime.fromisoformat(
            r["created_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(
            r["updated_at"].replace("Z", "+00:00"))
        minutes.append((end - start).total_seconds() / 60)
    if not minutes:
        raise SystemExit("ci-ratchet: no completed push Tests runs in "
                         "runs.json; cannot derive critical_path_minutes "
                         "(fail closed)")
    minutes.sort()
    n = len(minutes)
    mid = n // 2
    return minutes[mid] if n % 2 else (minutes[mid - 1] + minutes[mid]) / 2


def derive(metrics_dir: Path, runs_json: Path | None) -> dict[str, float]:
    derived: dict[str, float] = dict(archscore_metrics())
    events = read_metrics(metrics_dir)
    push_runs = [rows for (event, _), rows in events.items()
                 if event == "push"]
    if not push_runs:
        raise SystemExit("ci-ratchet: no push metrics in "
                         f"{metrics_dir}; the emitters the gate and its "
                         "instruments carry did not run (fail closed)")
    # A push event is one run; a window that ever carries more is graded on
    # its most expensive one -- the waste direction is the max.
    derived["script_runs_per_push"] = max(script_runs(r) for r in push_runs)
    # The full-case PR arm: the most expensive pull-request run in the
    # window whose own fast lane reported MODE: FULL. What a full-case PR
    # costs may only shrink -- that is scoping's ratchet.
    full_pr = [script_runs(rows) for (event, _), rows in events.items()
               if event == "pull_request"
               and any(x["lane"] == "fast" and x["class"] == "full"
                       for x in rows)]
    if full_pr:
        derived["script_runs_full_case_pr"] = max(full_pr)
    if runs_json is not None:
        derived["critical_path_minutes"] = critical_path_minutes(runs_json)
    return derived


def compare(budgets: dict, derived: dict) -> tuple[list[str], int]:
    grew = []
    lines = []
    for key in sorted(set(budgets) - METADATA_KEYS):
        budget = budgets[key]
        if key not in derived:
            lines.append(f"  ?     {key}: not derived this run "
                         "(missing input); not graded")
            continue
        cur = derived[key]
        mark = "ok" if cur <= budget else "GREW"
        if cur > budget:
            grew.append(key)
        lines.append(f"  {mark:<5} {key}: {cur} (budget {budget})")
    for key in sorted(set(derived) - set(budgets)):
        grew.append(key)
        lines.append(f"  GREW  {key}: {derived[key]} (no budget row; a new "
                     "metric starts unrecorded -- record it or remove it)")
    return lines, len(grew)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    record_reason = None
    if "--record" in argv:
        i = argv.index("--record")
        if i + 1 >= len(argv):
            print("ci-ratchet: --record needs a reason", file=sys.stderr)
            return 2
        record_reason = argv[i + 1]
        del argv[i:i + 2]
    metrics_dir = runs_json = None
    args = list(argv)
    for flag in ("--metrics-dir", "--runs-json"):
        if flag in args:
            i = args.index(flag)
            value = args[i + 1]
            if flag == "--metrics-dir":
                metrics_dir = Path(value)
            else:
                runs_json = Path(value)
            del args[i:i + 2]
    if metrics_dir is None or args:
        print(__doc__)
        return 2
    budgets = json.loads(BUDGETS.read_text())
    problems = budget_problems(budgets)
    if problems:
        for p in problems:
            print(f"ci-ratchet: refusing the budget table: {p}",
                  file=sys.stderr)
        return 1
    derived = derive(metrics_dir, runs_json)
    if record_reason is not None:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
        table = {**{k: v for k, v in derived.items()},
                 "recorded_at": head, "reason": record_reason}
        problems = budget_problems(table)
        if problems:
            for p in problems:
                print(f"ci-ratchet: refusing to record: {p}", file=sys.stderr)
            return 1
        BUDGETS.write_text(json.dumps(table, indent=1, sort_keys=True) + "\n")
        print(f"ci-ratchet: recorded {len(derived)} metric(s) at {head[:12]} "
              f"-- {record_reason}")
        return 0
    lines, grew = compare(budgets, derived)
    print("CI ratchet:")
    print("\n".join(lines))
    if grew:
        print(f"ci-ratchet: {grew} metric(s) grew; pay the debt or re-record "
              "deliberately with --record \"<reason>\" (CLAUDE.md rule 2)",
              file=sys.stderr)
        return 1
    print("ci-ratchet: every metric at or under its budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
