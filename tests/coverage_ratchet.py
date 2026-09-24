#!/usr/bin/env python3
"""A one-sided ratchet on package statement coverage and on `# pragma: no cover`.

Three numbers, all recorded in ``tests/coverage_budgets.json``, all moving in
one direction only.

**Coverage tightens until it reaches its ceiling, then stops.** Below the
ceiling an improvement must be re-recorded, exactly as ``tests/structure.py``
refuses an unrecorded improvement: a floor nobody raises is a floor that
protects last month's tree. At or above the ceiling the floor stays put and an
improvement is free. The ceiling exists because the last few per cent are not
worth what they cost -- see the pragma row, which is the reason.

The floor is recorded a tenth of a point below the measurement and compared
against the raw one, so it is always a number the recording run cleared with
room to spare -- see ``TOLERANCE``, which is why this is not the exact-equality
ratchet ``tests/structure.py`` uses.

**The pragma count only falls.** A coverage floor creates exactly one cheap
escape: mark the line ``# pragma: no cover`` and the statement leaves the
denominator. So the escape is itself ratcheted, and downward: a new exemption
fails this check, and removing one must be re-recorded. Without this row the
coverage floor is not a floor at all, it is an invitation.

**The module floor is per-MODULE, and the package floor cannot stand in for
it.** The Silver quality-scale rule ``test-coverage`` asks for "above 95 %
test coverage for all integration modules" -- a bar over every module, not
over the package average. ``package_percent_floor`` alone could not see the
difference (#1401, R6-D10-01): a module small enough to barely move the
average can fall all the way to zero -- most of this package's own modules
could, on the baseline -- while the package check stayed green, because the
floor is a ratio. This row records the LOWEST module percentage the same
instrument measured and refuses any module below it, so a single module
dropping is caught where the ratio was blind. It is one-sided like the others:
the record only rises, and a fall needs ``--allow-regression`` with its
reason. The bar is the rule's own 95 %, so a tree already under it records
the value it has and the register row (``tests/entities.py``) flips to todo
rather than the check orphaning -- the #951 keying, extended from the package
floor to the module floor.

**The config flow is pinned at full coverage, exactly.** The quality-scale
rule (register row ``config-flow-test-coverage``, Bronze) asks for FULL
statement coverage of the config flow -- not a bar to sit above but a
property to hold -- so this row records the raw module percentage with no
tolerance subtracted and no headroom: anything below the record refuses,
and the record cannot exceed the property. This is the standing record
``tests/entities.py`` keys that register row to (the #951 pin shape), which
is why it lives here rather than as a figure in a comment: the register's
row rotted once exactly because nothing executed against it. The escapes
are the ones the register's history already legitimises -- cover the branch
(``tests/config_flow_steps.py``), remove it as dead code (#542), or pragma
it under the cap above.

Measurement comes from the partition instrument rather than from a second
implementation::

    W5P_WORK=$(mktemp -d) tools/audit/w5-partition/coverage_tree.sh fast
    python3 tests/coverage_ratchet.py --coverage "$W5P_WORK/out/coverage.json"

With no ``--coverage`` the pragma row is still checked and the coverage row is
reported as unmeasured, which is a pass: a ratchet that fails when its
instrument did not run teaches seats to skip it.

    python3 tests/coverage_ratchet.py --record --coverage <json> --reason "..."
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUDGETS = ROOT / "tests" / "coverage_budgets.json"
PRODUCTION = ROOT / "custom_components" / "heatpump_optimizer"

#: Counted with a regex rather than by parsing, because a pragma is a COMMENT:
#: `ast` discards it, and `tokenize` would answer the same question at ten
#: times the cost. The pattern is coverage.py's own default, which is what
#: decides whether the line actually leaves the denominator.
PRAGMA = re.compile(r"#\s*pragma:\s*no\s?cover", re.IGNORECASE)

#: Percentage points of headroom left below the measurement when recording,
#: and the width of the dead band before an improvement must be re-recorded.
#:
#: `tests/structure.py` needs nothing like this: it counts an AST, so the same
#: tree gives the same number on any machine and a two-sided ratchet at exact
#: equality is fair. This number comes from RUNNING the suite under a tracer,
#: and what a run executes can differ between a developer's box and the runner
#: -- a platform branch, a script that fails early somewhere else, an
#: interpreter's own fast path. The size of that difference is not measured
#: here, and until it is, a floor recorded flush against its own measurement is
#: a gate that goes red for the machine rather than for the change. The first
#: record at the post-merge head measured 95.0016 %: a floor of 95.0 would have
#: had a quarter of a statement of margin.
#:
#: Both uses are the same number on purpose. Recording leaves this much room
#: below, so the next run has it; the improvement arm stays quiet until the
#: measurement clears the floor by this much PLUS a recordable step, so the
#: room it just left cannot immediately read as an unrecorded improvement.
TOLERANCE = 0.1


def count_pragmas() -> tuple[int, dict[str, int]]:
    """Every `no cover` pragma in the production package, and where."""
    per_file: dict[str, int] = {}
    for path in sorted(PRODUCTION.rglob("*.py")):
        n = sum(1 for line in path.read_text().splitlines() if PRAGMA.search(line))
        if n:
            per_file[str(path.relative_to(ROOT))] = n
    return sum(per_file.values()), per_file


def read_coverage(path: Path) -> tuple[float, int, int]:
    """(percent, statements, missed) for the production package."""
    data = json.loads(path.read_text())
    files = data.get("files", {})
    statements = sum(v["summary"]["num_statements"] for v in files.values())
    missed = sum(v["summary"]["missing_lines"] for v in files.values())
    if statements <= 0:
        raise SystemExit(
            "coverage payload reports zero statements; the instrument measured "
            "nothing and a percentage over an empty denominator is not a floor"
        )
    return 100.0 * (statements - missed) / statements, statements, missed


#: The module the quality-scale register's ``config-flow-test-coverage`` row
#: is about, keyed by filename inside the payload the instrument writes.
CONFIG_FLOW = "config_flow.py"

#: The Silver rule ``test-coverage``'s per-module bar, in percent: "above 95 %
#: for all integration modules". It is the top of the recorded
#: ``module_percent_floor`` -- a tree that clears it records the bar, a tree
#: under it records what it measured -- so the record's top and the register
#: row's key are the same number as the rule's.
MODULE_BAR = 95.0


def read_module_percent(path: Path, filename: str) -> float:
    """The RAW statement percentage of one module in the payload."""
    data = json.loads(path.read_text())
    for name, entry in data.get("files", {}).items():
        if name.endswith(f"/{filename}") or name == filename:
            summary = entry["summary"]
            return 100.0 * (
                summary["covered_lines"] / summary["num_statements"]
            )
    raise SystemExit(
        f"coverage payload reports nothing for {filename}; the instrument "
        "measured no such module and a floor over an absent denominator is "
        "not a floor"
    )


def module_percentages(path: Path) -> dict[str, float]:
    """Every module in the payload's RAW statement percentage, by basename."""
    data = json.loads(path.read_text())
    out: dict[str, float] = {}
    for name, entry in data.get("files", {}).items():
        summary = entry["summary"]
        out[name.rsplit("/", 1)[-1]] = 100.0 * (
            summary["covered_lines"] / summary["num_statements"]
        )
    if not out:
        raise SystemExit(
            "coverage payload reports no files; the instrument measured "
            "nothing and a per-module floor over no modules is not a floor"
        )
    return out


def modules_below(path: Path, floor: float) -> list[tuple[str, float]]:
    """(module, percent) for every module under `floor`, worst first."""
    rows = [(n, p) for n, p in module_percentages(path).items() if p < floor]
    rows.sort(key=lambda r: (r[1], r[0]))
    return rows


# A VERBATIM copy of tests/structure.py's cap_problem, the recorded-number
# barrier every ratchet shares (#1583's review). This grader is a single
# standard-library file on purpose -- a job may restore it from the base
# and run it under `python3 -I`, where a sibling import neither resolves
# nor stays the base's -- so it carries the copy, and tests/entities.py
# refuses any copy that differs from the original by one character.
def cap_problem(where: str, table: object, key: str, *, integer: bool = False,
                low: float = 0.0, low_open: bool = False,
                high: float | None = None) -> str | None:
    """Why ``table[key]`` cannot be a ratchet's recorded number, or None.

    The class this closes (#1583's review): Python's json reads ``NaN``,
    ``Infinity``, ``-Infinity`` and ``1e999`` as floats without complaint, and
    every comparison against NaN is False -- ``current > nan`` never fires and
    ``raw < nan`` never fires -- so a cap edited to NaN was an unlimited raise
    that this script printed as ``ok cut_views 110 <= nan``. Infinity passes
    by arithmetic. The other spellings fail differently per script and none of
    them says why: a string crashed one comparison and ``float()``-coerced in
    another (``"nan"`` into NaN), and a bool is 0 or 1 to Python.

    So every ratchet calls this on load and refuses before it compares. It
    refuses: an absent key, a bool, anything not an int or float, a
    non-finite number, a float where ``integer`` asks for a count, a value
    below ``low`` (or equal to it when ``low_open``), and one above ``high``.
    The message names the file, the key and the value, so the refusal is the
    fix's instructions.
    """
    if not isinstance(table, dict) or key not in table:
        return (f"{where}: {key} is absent -- a ratchet with no recorded "
                f"number compares against nothing")
    value = table[key]
    label = f"{where}: {key}={value!r:.40}"
    if isinstance(value, bool):
        return (f"{label} is a boolean, which Python compares as "
                f"{int(value)}; record the number")
    if not isinstance(value, (int, float)):
        return f"{label} is a {type(value).__name__}, not a number"
    # An int before isfinite: json reads a 400-digit integer as an exact int,
    # and math.isfinite (like every float() a ratchet then applies) raises
    # OverflowError on one no float can hold.
    if isinstance(value, int):
        if abs(value) > 2 ** 53:
            return (f"{label} is past the largest integer a float holds "
                    f"exactly, so no comparison with a measurement means "
                    f"anything")
    elif not math.isfinite(value):
        return (f"{label} is not finite: every comparison against NaN is "
                f"false and nothing exceeds Infinity, so this cap would be an "
                f"unlimited raise")
    if integer and not isinstance(value, int):
        return f"{label} is a float where a count is recorded"
    if value < low or (low_open and value == low):
        return f"{label} is {'at or ' if low_open else ''}below {low:g}"
    if high is not None and value > high:
        return f"{label} is above {high:g}"
    return None


def load_budgets() -> dict:
    return json.loads(BUDGETS.read_text())


def budget_problems(budgets: dict) -> list[str]:
    """Every recorded number here that cannot serve as a floor or cap.

    Through `cap_problem` (the verbatim copy above), the barrier every
    ratchet shares: `raw < nan` is False, so a NaN floor refused nothing, and
    the module floor's `p < nan` left every module above it (#1583's review). The percentages are
    finite numbers in [0, 100]; the pragma cap is a non-negative count. All
    five rows are required: the two floors the register keys to already fail
    when absent under `--coverage`, and without it they were never read.
    """
    where = BUDGETS.name
    out = [cap_problem(where, budgets, key, high=100.0)
           for key in ("package_percent_floor", "package_percent_ceiling",
                       "config_flow_percent_floor", "module_percent_floor")]
    out.append(cap_problem(where, budgets, "pragmas", integer=True))
    return [p for p in out if p]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", default="", help="coverage.json from the instrument")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--reason", default="")
    ap.add_argument(
        "--allow-regression", default="",
        help="record a pragma count HIGHER than the recorded cap, or a floor "
             "LOWER than the recorded one (package, config-flow or module). "
             "Both are the ratchet running backwards, so each needs its reason "
             "here and the same reason in the commit message "
             "(`tests/structure.py`'s idiom).",
    )
    args = ap.parse_args()

    budgets = load_budgets()
    malformed = budget_problems(budgets)
    if malformed:
        print("COVERAGE RATCHET REFUSED -- a recorded number that cannot be compared:")
        for problem in malformed:
            print(f"  - {problem}")
        return 1
    floor = float(budgets["package_percent_floor"])
    ceiling = float(budgets["package_percent_ceiling"])
    pragma_cap = int(budgets["pragmas"])
    module_floor = budgets.get("module_percent_floor")

    failures: list[str] = []
    improvements: list[str] = []

    measured_pragmas, per_file = count_pragmas()
    print(f"  {'ok  ' if measured_pragmas == pragma_cap else 'FAIL'} "
          f"pragmas {measured_pragmas} <= {pragma_cap}")
    if measured_pragmas > pragma_cap:
        failures.append(
            f"pragmas {measured_pragmas} > {pragma_cap}. A `# pragma: no cover` "
            "takes a statement out of the denominator, so it is the one cheap "
            "way past the coverage floor below. Cover the line, or say in the "
            "commit message why it cannot be reached and re-record."
        )
    elif measured_pragmas < pragma_cap:
        improvements.append(
            f"pragmas {measured_pragmas} < {pragma_cap}: an exemption was "
            "removed and the cap still allows it back."
        )
    for name, n in sorted(per_file.items()):
        print(f"       {name}: {n}")

    if args.coverage:
        raw, statements, missed = read_coverage(Path(args.coverage))
        # Compared against the RAW measurement, not a rounded one. An earlier
        # version rounded to the recorded tenth and a floor of 94.8 refused the
        # very tree it was recorded from at a raw 94.7551 -- which is how a gate
        # teaches seats to distrust it. The headroom that makes this survive a
        # re-measure elsewhere is left at RECORDING time instead, by TOLERANCE.
        band = "at or above the ceiling" if floor >= ceiling else "below the ceiling"
        tighten_at = floor + TOLERANCE + 0.1
        print(f"  {'ok  ' if raw >= floor else 'FAIL'} package coverage "
              f"{raw:.2f} % >= {floor:.1f} % "
              f"({statements - missed}/{statements} statements, {band})")
        if raw < floor:
            failures.append(
                f"package coverage {raw:.2f} % < {floor:.1f} %. "
                f"{missed} of {statements} statements are uncovered."
            )
        elif floor < ceiling and raw >= tighten_at:
            improvements.append(
                f"package coverage {raw:.2f} % is {raw - floor:.2f} points over "
                f"the {floor:.1f} % floor, past the {tighten_at:.1f} % at which "
                f"a full step can be recorded below its {ceiling:.1f} % "
                "ceiling: re-record."
            )
        # The config-flow row: the quality-scale rule asks for FULL coverage,
        # so this is an exact property rather than a bar with headroom -- the
        # record holds the raw module percentage and anything below refuses.
        # No TOLERANCE is subtracted and no improvement arm exists: the record
        # cannot exceed the property and cannot tighten past it.
        cf_recorded = budgets.get("config_flow_percent_floor")
        raw_cf = read_module_percent(Path(args.coverage), CONFIG_FLOW)
        if cf_recorded is None:
            failures.append(
                "no config_flow_percent_floor recorded: the register's "
                "config-flow-test-coverage row is keyed to this standing "
                "record and the record is absent"
            )
        else:
            cf_recorded = float(cf_recorded)
            print(f"  {'ok  ' if raw_cf >= cf_recorded else 'FAIL'} "
                  f"{CONFIG_FLOW} coverage {raw_cf:.2f} % >= {cf_recorded:.1f} %")
            if raw_cf < cf_recorded:
                failures.append(
                    f"{CONFIG_FLOW} coverage {raw_cf:.2f} % < {cf_recorded:.1f} %: "
                    "the register's config-flow-test-coverage row claims full "
                    "coverage of the config flow and the instrument no longer "
                    "shows it. Cover the missed branches in "
                    "tests/config_flow_steps.py, or remove a genuinely "
                    "unreachable branch (#542) -- do not lower this record "
                    "quietly."
                )
        # The module-floor row: the Silver test-coverage rule asks "above 95 %
        # for ALL integration modules", a bar the package ratio above cannot
        # see (#1401) because a small module barely moves the average. The
        # record holds the LOWEST module percentage measured, capped at the
        # rule's own 95 % bar, and every module in the payload must clear it.
        if module_floor is None:
            failures.append(
                "no module_percent_floor recorded: the register's "
                "test-coverage row is keyed to this standing per-module record "
                "and the record is absent, so nothing holds a single module to "
                "the Silver rule's bar"
            )
        else:
            module_floor = float(module_floor)
            below = modules_below(Path(args.coverage), module_floor)
            print(f"  {'ok  ' if not below else 'FAIL'} every module >= "
                  f"{module_floor:.1f} %  ({len(below)} below)")
            for name, pct in below:
                print(f"       {name}: {pct:.2f} %")
            if below:
                named = ", ".join(f"{n} {p:.2f} %" for n, p in below)
                failures.append(
                    f"{len(below)} module(s) below the {module_floor:.1f} % "
                    f"per-module floor: {named}. The Silver rule asks above "
                    "95 % coverage for ALL integration modules; the package "
                    "floor above is a ratio and cannot see one module fall. "
                    "Cover the module, or remove a genuinely unreachable "
                    "branch (#542) -- do not lower this record quietly."
                )
    else:
        print("  skip coverage -- no --coverage payload; the pragma row still ran")

    if args.record:
        # A recorder that writes whatever it measured is not a ratchet, it is a
        # transcript. Every row may only move one way without a stated reason,
        # and this refusal is the one that matters most: `--record` is what a
        # seat reaches for after a merge, and the merge is exactly where a cap
        # rises for somebody else's reason. Measured: this branch's own record
        # took the pragma cap 10 -> 11 in silence, on a pragma #875 added to
        # `optimizer.py` on `main`.
        backwards: list[str] = []
        new_floor = floor
        new_cf_floor = budgets.get("config_flow_percent_floor")
        new_module_floor = budgets.get("module_percent_floor")
        if args.coverage:
            raw, _stmts, _missed = read_coverage(Path(args.coverage))
            new_floor = min(math.floor((raw - TOLERANCE) * 10) / 10, ceiling)
            if new_floor < floor:
                backwards.append(
                    f"the floor would fall {floor:.1f} % -> {new_floor:.1f} %"
                )
            # Recorded as the RAW module percentage, capped at the property:
            # full coverage is the only value this row may hold at its top,
            # and no tolerance is left below it on purpose (see the module
            # docstring).
            new_cf_floor = min(
                round(read_module_percent(Path(args.coverage), CONFIG_FLOW), 2),
                100.0,
            )
            if (
                budgets.get("config_flow_percent_floor") is not None
                and new_cf_floor < float(budgets["config_flow_percent_floor"])
            ):
                backwards.append(
                    "the config-flow floor would fall "
                    f"{float(budgets['config_flow_percent_floor']):.2f} % -> "
                    f"{new_cf_floor:.2f} %"
                )
            # The module floor holds the LOWEST module percentage, capped at
            # the rule's own bar (MODULE_BAR): a tree clearing the bar records
            # the bar, a tree under it records the value it has -- the same
            # "record the property's top" shape as the config-flow row, and it
            # is one-sided like every row here.
            new_module_floor = min(
                round(min(module_percentages(Path(args.coverage)).values()), 2),
                MODULE_BAR,
            )
            if (
                budgets.get("module_percent_floor") is not None
                and new_module_floor < float(budgets["module_percent_floor"])
            ):
                backwards.append(
                    "the module floor would fall "
                    f"{float(budgets['module_percent_floor']):.2f} % -> "
                    f"{new_module_floor:.2f} %"
                )
        if measured_pragmas > pragma_cap:
            backwards.append(
                f"the pragma cap would rise {pragma_cap} -> {measured_pragmas}"
            )
        if backwards and not args.allow_regression:
            print("\nREFUSED to record: " + "; and ".join(backwards) + ".")
            print("  Every row is one-sided. If this is deliberate, say why:")
            print("    --allow-regression '<reason>', and the same reason in "
                  "the commit message.")
            return 1
        if args.allow_regression:
            budgets["allowed_regression"] = args.allow_regression
        elif "allowed_regression" in budgets:
            del budgets["allowed_regression"]
        budgets["package_percent_floor"] = new_floor
        budgets["pragmas"] = measured_pragmas
        budgets["recorded_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if new_cf_floor is not None:
            budgets["config_flow_percent_floor"] = new_cf_floor
        if new_module_floor is not None:
            budgets["module_percent_floor"] = new_module_floor
        if args.reason:
            budgets["reason"] = args.reason
        BUDGETS.write_text(json.dumps(budgets, indent=2) + "\n")
        print(f"\nRECORDED floor={budgets['package_percent_floor']} "
              f"pragmas={budgets['pragmas']} "
              f"config_flow={budgets.get('config_flow_percent_floor')} "
              f"module={budgets.get('module_percent_floor')}")
        return 0

    if failures:
        print("\nCOVERAGE RATCHET BREACHED")
        for f in failures:
            print(f"  - {f}")
        return 1
    if improvements:
        print("\nCOVERAGE RATCHET: improved and not yet recorded")
        for i in improvements:
            print(f"  - {i}")
        print("\n  You made this better. Write it down:")
        print("    python3 tests/coverage_ratchet.py --record "
              "--coverage <json> --reason '<what moved it>'")
        print("  and put the same reason in the commit message.")
        return 1
    print("\nCOVERAGE RATCHET PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
