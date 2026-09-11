#!/usr/bin/env python3
"""A one-sided ratchet on package statement coverage and on `# pragma: no cover`.

Two numbers, both recorded in ``tests/coverage_budgets.json``, both moving in
one direction only.

**Coverage tightens until it reaches its ceiling, then stops.** Below the
ceiling an improvement must be re-recorded, exactly as ``tests/structure.py``
refuses an unrecorded improvement: a floor nobody raises is a floor that
protects last month's tree. At or above the ceiling the floor stays put and an
improvement is free. The ceiling exists because the last few per cent are not
worth what they cost -- see the pragma row, which is the reason.

The floor is compared and recorded at the tenth, rounded DOWN, so a recorded
floor is always a number the run that recorded it provably cleared.

**The pragma count only falls.** A coverage floor creates exactly one cheap
escape: mark the line ``# pragma: no cover`` and the statement leaves the
denominator. So the escape is itself ratcheted, and downward: a new exemption
fails this check, and removing one must be re-recorded. Without this row the
coverage floor is not a floor at all, it is an invitation.

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


def load_budgets() -> dict:
    return json.loads(BUDGETS.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", default="", help="coverage.json from the instrument")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--reason", default="")
    args = ap.parse_args()

    budgets = load_budgets()
    floor = float(budgets["package_percent_floor"])
    ceiling = float(budgets["package_percent_ceiling"])
    pragma_cap = int(budgets["pragmas"])

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
        # Rounded DOWN to the tenth the budget records, on both sides of the
        # comparison. Two reasons, and the first was measured the hard way: a
        # floor of 94.8 against a raw 94.7551 refuses the very tree it was
        # recorded from, which is how a gate teaches seats to distrust it.
        # Rounding to NEAREST fixes that case and leaves a second: 94.96 records
        # as 95.0, and the same tree measured anywhere that differs by a
        # hundredth of a point is then below its own floor. Rounding down makes
        # the recorded floor a number the measurement provably cleared, and
        # gives the next run the rest of the tenth as the tolerance a
        # suite-execution measurement needs and an AST count does not.
        pct = math.floor(raw * 10) / 10
        band = "at or above the ceiling" if floor >= ceiling else "below the ceiling"
        print(f"  {'ok  ' if pct >= floor else 'FAIL'} package coverage "
              f"{pct:.1f} % >= {floor:.1f} % "
              f"({statements - missed}/{statements} statements, "
              f"{raw:.2f} % measured, {band})")
        if pct < floor:
            failures.append(
                f"package coverage {pct:.1f} % < {floor:.1f} %. "
                f"{missed} of {statements} statements are uncovered."
            )
        elif floor < ceiling and pct > floor:
            improvements.append(
                f"package coverage {pct:.1f} % > {floor:.1f} % and the floor is "
                f"below its {ceiling:.1f} % ceiling, so it tightens: re-record."
            )
    else:
        print("  skip coverage -- no --coverage payload; the pragma row still ran")

    if args.record:
        if args.coverage:
            raw, _stmts, _missed = read_coverage(Path(args.coverage))
            budgets["package_percent_floor"] = min(
                math.floor(raw * 10) / 10, ceiling)
        budgets["pragmas"] = measured_pragmas
        budgets["recorded_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if args.reason:
            budgets["reason"] = args.reason
        BUDGETS.write_text(json.dumps(budgets, indent=2) + "\n")
        print(f"\nRECORDED floor={budgets['package_percent_floor']} "
              f"pragmas={budgets['pragmas']}")
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
