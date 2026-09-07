#!/usr/bin/env python3
"""The typing ruler (#303): three numbers, pinned, and none of them may grow.

    python3 tests/typing_ruler.py            # source-only; the gate runs this
    .venv-typing/bin/python tests/typing_ruler.py --mypy   # the `typing` job
    python3 tests/typing_ruler.py --print-requirements     # the pins, as pip lines

#303 is not fixed by reducing its error count. It is fixed by making that
count a number nobody can game, after which reduction is ordinary work. So
this file lands before any annotation does, and it ratchets THREE numbers:

  errors        total mypy --strict errors under the pinned, stub-free ruler
  by_code       the same errors split by error code, ratcheted PER CODE
  type_ignores  `# type: ignore` occurrences, a separate hard metric at 0

The third is not a flag on the first. ``--warn-unused-ignores`` is in the
command and does NOT prevent ignore-stuffing: the judge measured annotating
four ``button.py`` ``__init__`` signatures properly at 427 -> 423, and adding
four ``# type: ignore[no-untyped-def]`` comments instead at 427 -> 423 --
identical, with the flag on throughout. It cannot fire, because a live ignore
is a *used* ignore and that flag only catches stale ones. Keep it for
staleness; count the ignores separately.

WHY by_code IS RATCHETED PER CODE. Partial annotation relabels rather than
reduces: typing the same members as ``object`` instead of ``Any`` moved the
count -3 where ``Any`` moved it -33, because ``object`` generates its own
downstream errors. A total that holds still while the mix churns is a change
that did nothing. A code absent from the recorded table has a budget of zero,
so relabelling into a fresh code fails rather than passing unseen.

THE SPLIT, AND WHY IT IS A SPLIT. ``type_ignores`` is a source scan needing no
toolchain, so it runs in the ordinary gate on every pull request. ``errors``
and ``by_code`` need the pinned toolchain, which no gate lane has, so they run
in the `typing` CI job -- the shape ``card_browser.mjs`` and ``nightly_ha.py``
already have. Making the one metric that needs nothing depend on a job that
installs a toolchain over the network would be the wrong way round: the guard
against ignore-stuffing would go unchecked exactly when the toolchain fails.

FOUR GUARDS, because a count is only worth what its guards are worth. Each
names the lever it exists to stop:

1. **The construction guard.** Total ``error:`` lines must EQUAL the lines
   under ``custom_components/heatpump_optimizer/``. That is what makes the
   number production-only *by construction* rather than by subtraction, and
   it is also how stub leakage is caught: with ``tests/hastub`` on the path
   there are error lines located inside it (55, measured), so the two numbers
   part company and this refuses. ``run.sh`` exports
   ``PYTHONPATH=$PWD/tests/hastub``, so that is not a hypothetical.
2. **The pin guard.** The installed mypy and homeassistant-stubs versions must
   equal the recorded pins, and the interpreter must meet ``python_min``. A
   number from an unpinned tool is not the census.
3. **The exit-status guard.** mypy must exit 0 or 1. A toolchain that dies
   emits a line or two and a naive counter reads that as a near-perfect score;
   guard 1 catches it too, from the other side, since the dying line's path is
   inside the stubs package rather than the integration.
4. **The suppression-surface guard.** No mypy configuration may exist in the
   tree. ``disable_error_code`` in a config file drives the count down with
   zero improvement and neither the total nor the per-code table can see it
   happen -- the same shape as ignore-stuffing, one level up.

WHAT THIS DOES NOT DO. It does not annotate anything, and it does not close
#303. It also cannot run on a box below Python 3.13.2: the pinned stubs will
not install there, so ``--mypy`` refuses instead of quietly measuring
something else. See #504 -- the ruler is authoritative in CI, and a local
``--mypy`` is available only where the pins install.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_REL = "custom_components/heatpump_optimizer"
PACKAGE_DIR = REPO_ROOT / PACKAGE_REL
BUDGET_FILE = REPO_ROOT / "tests" / "typing_budgets.json"

# One `# type: ignore`, however spaced, and the module-level hammer that does
# the same job for a whole file at once. Counted per OCCURRENCE, not per line:
# `grep -c` counts lines, and two ignores on one line are two ignores.
IGNORE_RE = re.compile(r"#\s*type:\s*ignore|#\s*mypy:\s*ignore-errors")

# `path:line: error: message  [code]`, with an optional column. `--no-error-summary`
# removes the trailing total; `note:` lines are not errors and are not counted.
ERROR_RE = re.compile(
    r"^(?P<path>[^:]+):(?P<line>\d+):(?:\d+:)?\s*error:\s*(?P<msg>.*?)"
    r"(?:\s*\[(?P<code>[A-Za-z0-9_-]+)\])?$"
)

# Files mypy would read configuration from. None of these exist in this tree
# and guard 4 keeps it that way.
CONFIG_CANDIDATES = ("mypy.ini", ".mypy.ini", "setup.cfg", "pyproject.toml")


class Report:
    def __init__(self, title: str) -> None:
        self.title = title
        self.failures = 0
        self.checks = 0
        print(f"\n=== {title} ===")

    def check(self, name: str, ok: object, detail: str = "") -> bool:
        self.checks += 1
        if ok:
            print(f"  ok   {name}")
        else:
            self.failures += 1
            print(f"  FAIL {name}" + (f"  [{detail}]" if detail else ""))
        return bool(ok)

    def note(self, name: str, detail: str = "") -> None:
        print(f"  ..   {name}" + (f"  [{detail}]" if detail else ""))

    def close(self, label: str) -> int:
        if self.failures:
            print(f"\n{self.failures} of {self.checks} {label} FAILED")
            return 1
        print(f"\nALL {self.checks} {label} PASSED")
        return 0


def budgets() -> dict:
    return json.loads(BUDGET_FILE.read_text())


def head_sha() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    return out.stdout.strip() or "unknown"


# ---------------------------------------------------------------------------
# source-only measurements: no toolchain, so the ordinary gate runs them


def count_type_ignores() -> tuple[int, list[str]]:
    """Occurrences of a type-ignore comment in the integration, with evidence.

    The rule, stated because a number without its rule is not re-derivable
    (`fixer.md` step 8): every match of IGNORE_RE in every ``*.py`` under
    ``custom_components/heatpump_optimizer``, counted per match rather than
    per line, with no exclusions.
    """
    total = 0
    where: list[str] = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT)
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for _ in IGNORE_RE.finditer(line):
                total += 1
                where.append(f"{rel}:{lineno}: {line.strip()}")
    return total, where


def find_mypy_config() -> list[str]:
    """Configuration files mypy would read, that carry mypy settings.

    ``setup.cfg`` and ``pyproject.toml`` are only a finding when they actually
    carry a mypy section -- they have other jobs, and this check must not
    become a reason nobody may add a ``pyproject.toml``.
    """
    found = []
    for name in CONFIG_CANDIDATES:
        path = REPO_ROOT / name
        if not path.exists():
            continue
        if name in ("mypy.ini", ".mypy.ini"):
            found.append(name)
            continue
        text = path.read_text()
        if "[mypy" in text or "[tool.mypy" in text:
            found.append(name)
    return found


# ---------------------------------------------------------------------------
# the pinned ruler itself


def installed_version(dist: str) -> str | None:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version(dist)
    except PackageNotFoundError:
        return None


def requirement_lines(budget: dict) -> list[str]:
    ruler = budget["ruler"]
    lines = [
        f"mypy=={ruler['mypy']}",
        f"homeassistant-stubs=={ruler['homeassistant_stubs']}",
    ]
    lines += [f"{name}=={ver}" for name, ver in sorted(ruler["third_party"].items())]
    return lines


def check_pins(report: Report, budget: dict) -> bool:
    """Guard 2. The interpreter and the two load-bearing pins."""
    ruler = budget["ruler"]
    minimum = tuple(int(p) for p in ruler["python_min"].split("."))
    running = sys.version_info[: len(minimum)]
    ok = report.check(
        f"interpreter is at least Python {ruler['python_min']}",
        running >= minimum,
        f"running {'.'.join(str(p) for p in running)}; "
        f"homeassistant-stubs=={ruler['homeassistant_stubs']} will not install below "
        f"{ruler['python_min']} (#504)",
    )
    for dist, pin in (
        ("mypy", ruler["mypy"]),
        ("homeassistant-stubs", ruler["homeassistant_stubs"]),
    ):
        got = installed_version(dist)
        ok &= report.check(
            f"{dist} is pinned at {pin}", got == pin, f"found {got or 'nothing'}"
        )
    for name, pin in sorted(ruler["third_party"].items()):
        got = installed_version(name)
        ok &= report.check(
            f"{name} is pinned at {pin}", got == pin, f"found {got or 'nothing'}"
        )
    return bool(ok)


def run_mypy(budget: dict) -> tuple[int, list[str]]:
    """The issue's pinned invocation, with the stub excluded by construction.

    ``MYPYPATH`` and ``PYTHONPATH`` are stripped rather than merely unset by
    convention: ``tests/run.sh`` exports ``PYTHONPATH=$PWD/tests/hastub`` for
    every script it runs, and the whole point of this ruler is that the fake
    Home Assistant is not on the path.
    """
    import os

    env = {k: v for k, v in os.environ.items() if k not in ("MYPYPATH", "PYTHONPATH")}
    with tempfile.TemporaryDirectory() as cache:
        proc = subprocess.run(
            [
                sys.executable, "-m", "mypy",
                "--strict",
                "--warn-unused-ignores",
                "--show-error-codes",
                "--no-error-summary",
                "--no-incremental",
                "--cache-dir", cache,
                "--python-version", budget["ruler"]["python_version_flag"],
                PACKAGE_REL,
            ],
            cwd=REPO_ROOT, capture_output=True, text=True, env=env,
        )
    return proc.returncode, (proc.stdout + proc.stderr).splitlines()


def parse_errors(lines: list[str]) -> tuple[list[tuple[str, str]], int]:
    """Every ``error:`` line as (path, code), plus the total seen.

    The total is returned separately from the parsed list so guard 1 can
    compare "error lines anywhere" against "error lines under the package"
    rather than trusting one number to describe both.
    """
    parsed: list[tuple[str, str]] = []
    total = 0
    for line in lines:
        if ": error:" not in line:
            continue
        total += 1
        m = ERROR_RE.match(line)
        if m:
            parsed.append((m.group("path"), m.group("code") or "no-code"))
        else:
            parsed.append((line.split(":", 1)[0], "unparsed"))
    return parsed, total


def measure(report: Report, budget: dict) -> dict | None:
    """The census: errors, by_code and type_ignores, or None if a guard refused."""
    rc, lines = run_mypy(budget)

    # Guard 3.
    if not report.check(
        "mypy exited 0 or 1 (clean, or errors found)",
        rc in (0, 1),
        f"exit {rc}; a toolchain that dies emits one or two lines and a naive "
        f"counter reads that as a near-perfect score. First line: "
        f"{lines[0] if lines else '(no output)'}",
    ):
        return None

    parsed, total_lines = parse_errors(lines)
    under_package = [p for p in parsed if p[0].startswith(PACKAGE_REL + "/")]

    # Guard 1.
    outside = [p for p in parsed if not p[0].startswith(PACKAGE_REL + "/")]
    if not report.check(
        "production-only by construction: every error line is under "
        f"{PACKAGE_REL}/",
        not outside,
        f"{total_lines} error line(s), {len(under_package)} under the package; "
        f"{len(outside)} elsewhere, first at {outside[0][0] if outside else ''}. "
        "Error lines outside the integration mean the stub is on the path, or "
        "the toolchain itself failed to parse -- either way the count no longer "
        "describes this codebase",
    ):
        return None

    by_code: dict[str, int] = {}
    for _, code in under_package:
        by_code[code] = by_code.get(code, 0) + 1

    ignores, _ = count_type_ignores()
    return {
        "errors": len(under_package),
        "by_code": dict(sorted(by_code.items())),
        "type_ignores": ignores,
    }


# ---------------------------------------------------------------------------
# the ratchet


def ratchet(report: Report, recorded: dict, measured: dict) -> list[tuple]:
    """Fail anything that grew; return the rows that IMPROVED and are unrecorded.

    The improvement rows are not decoration. Between a budget and a better
    tree the gate is not loose, it is ABSENT -- the improvement can be given
    back with nothing failing (structure.py, #350). They are also the control
    on a census transcribed by hand: a recorded number that is too high shows
    up here, loudly, on every run including the one that recorded it.
    """
    improved: list[tuple] = []

    def one(key: str, budget: int, current: int) -> None:
        if current > budget:
            report.check(
                f"{key} did not grow", False,
                f"recorded {budget}, measured {current} ({current - budget:+})",
            )
        else:
            report.check(f"{key} did not grow", True)
            if current < budget:
                improved.append((key, budget, current))

    one("errors", recorded["errors"], measured["errors"])

    codes = sorted(set(recorded["by_code"]) | set(measured["by_code"]))
    for code in codes:
        # A code absent from the record has a budget of ZERO. That is what
        # stops relabelling: errors moved into a fresh code fail on arrival
        # instead of arriving under a total that did not move.
        one(f"by_code[{code}]", recorded["by_code"].get(code, 0),
            measured["by_code"].get(code, 0))
    return improved


def report_improvements(rows: list[tuple]) -> None:
    if not rows:
        return
    print()
    print("########## %d number(s) IMPROVED and not yet recorded ##########" % len(rows))
    print("  %-32s %10s %10s %8s" % ("number", "recorded", "measured", "delta"))
    for key, budget, current in rows:
        print("  %-32s %10s %10s %8s  BETTER (lower is better)"
              % (key, budget, current, f"{current - budget:+}"))
    print()
    print("  Write it down in the PR that earned it. Until then the gate is not")
    print("  loose here, it is ABSENT, and the gain can be given back silently.")


# ---------------------------------------------------------------------------
# entry points


def source_checks(report: Report, budget: dict) -> None:
    ignores, where = count_type_ignores()
    for line in where[:20]:
        report.note("type-ignore", line)
    budgeted = budget["type_ignores"]
    if ignores > budgeted:
        report.check(
            "type_ignores did not grow", False,
            f"recorded {budgeted}, measured {ignores} ({ignores - budgeted:+}). "
            "--warn-unused-ignores cannot catch this: a live ignore is a USED "
            "ignore. Annotate instead, or record the increase deliberately",
        )
    else:
        report.check("type_ignores did not grow", True)
        if ignores < budgeted:
            report_improvements([("type_ignores", budgeted, ignores)])

    # Guard 4.
    configs = find_mypy_config()
    report.check(
        "no mypy configuration exists to suppress error codes from",
        not configs,
        f"found {', '.join(configs)}; disable_error_code there drives the count "
        "down with zero improvement, and neither the total nor the per-code "
        "table can see it happen",
    )

    census = budget.get("census")
    if census is None:
        report.note(
            "census not recorded yet",
            "the `typing` CI job produces it; this lane owns type_ignores only",
        )
    else:
        report.note(
            "census recorded",
            f"{census['errors']} errors across {len(census['by_code'])} codes "
            f"at {str(census.get('recorded_at', '?'))[:12]}",
        )


def mypy_checks(report: Report, budget: dict, emit: str | None) -> None:
    if not check_pins(report, budget):
        print()
        print("REFUSING to measure. A count from an unpinned tool is not the")
        print("census (#504). Install exactly what --print-requirements names.")
        return

    measured = measure(report, budget)
    if measured is None:
        return

    if emit:
        Path(emit).write_text(json.dumps(measured, indent=1) + "\n")
        print(f"\nmeasurement written to {emit}")

    census = budget.get("census")
    if census is None:
        report.check(
            "the census is recorded", False,
            "this ruler has never recorded its numbers, so nothing is ratcheted",
        )
        print()
        print("########## the census, measured here ##########")
        print("  errors        %d" % measured["errors"])
        print("  type_ignores  %d" % measured["type_ignores"])
        print("  by code:")
        for code, n in measured["by_code"].items():
            print("    %-24s %4d" % (code, n))
        print()
        print("  Record it by putting this in tests/typing_budgets.json as")
        print('  "census", then commit. The ratchet enforces it from the next run:')
        print()
        block = dict(measured)
        block.pop("type_ignores", None)
        block["recorded_at"] = head_sha()
        for line in json.dumps(block, indent=2).splitlines():
            print("    " + line)
        return

    improved = ratchet(report, census, measured)
    ignores_budget = budget["type_ignores"]
    if measured["type_ignores"] > ignores_budget:
        report.check(
            "type_ignores did not grow", False,
            f"recorded {ignores_budget}, measured {measured['type_ignores']}",
        )
    else:
        report.check("type_ignores did not grow", True)
        if measured["type_ignores"] < ignores_budget:
            improved.append(("type_ignores", ignores_budget, measured["type_ignores"]))
    report_improvements(improved)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--mypy", action="store_true",
        help="run the pinned ruler and ratchet all three numbers "
             "(needs the pinned toolchain; the `typing` CI job runs this)",
    )
    ap.add_argument(
        "--print-requirements", action="store_true",
        help="print the pins as pip requirement lines and exit",
    )
    ap.add_argument("--emit", metavar="PATH", help="write the measurement as JSON")
    args = ap.parse_args()

    budget = budgets()

    if args.print_requirements:
        print("\n".join(requirement_lines(budget)))
        return 0

    if args.mypy:
        ruler = budget["ruler"]
        report = Report(
            f"typing ruler (mypy {ruler['mypy']}, "
            f"homeassistant-stubs {ruler['homeassistant_stubs']}, stub-free)"
        )
        mypy_checks(report, budget, args.emit)
        return report.close("typing-ruler checks")

    report = Report("typing ruler, source-only (no toolchain needed)")
    source_checks(report, budget)
    return report.close("typing-ruler source checks")


if __name__ == "__main__":
    sys.exit(main())
