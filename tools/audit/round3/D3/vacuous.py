#!/usr/bin/env python3
"""Assertions the suite cannot fail: quantifiers that ran over an empty set.

Metric definition: the number of `all(...)` / `any(...)` calls, executed on
a source line that is part of a check/assert call in a tests/ script, whose
iterable was EMPTY at run time -- `all(<empty>)` is True whatever production
does, so that assertion cannot fail.

Run (from the repository root):

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D3/vacuous.py \
        tests/entities.py tests/features.py tests/manual_plan.py \
        tests/config_flow_steps.py tests/ha_contract.py tests/typing_ruler.py

Expected value at the baseline: counts only, contention-immune, +- 0 on a
rerun.  It prints one RESULT line per script and writes
tools/audit/round3/D3/vacuous.json.
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
Machine: 8-core Apple M1, macOS Darwin 25.6.0, python3 3.11.5.

Instrumented symbol: builtins.all / builtins.any, wrapped in place, with the
call attributed to the tests/ frame that made it; the assertion sites are
read from the script's own AST (a call to check/assert on that line).

Perturbation: make one such iterable non-empty (give the check a case to
quantify over) and that line leaves the report; empty another and it joins.
Direction: the count falls when a check gains a case.
"""
from __future__ import annotations

import ast
import builtins
import io
import json
import os
import runpy
import sys
from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

CHECK_NAMES = {"check", "bad", "chk", "expect", "require", "issue", "_check"}

EMPTY: Counter = Counter()
NONEMPTY: Counter = Counter()
TARGET = {"path": ""}


def _record(kind, iterable):
    items = list(iterable)
    f = sys._getframe(2)
    # runpy.run_path keeps the path it was given, so normalise before
    # comparing: a relative co_filename must still match the target.
    if os.path.abspath(f.f_code.co_filename) == TARGET["path"]:
        (EMPTY if not items else NONEMPTY)[(f.f_lineno, kind)] += 1
    return items


def _all(iterable):
    return _all_orig(_record("all", iterable))


def _any(iterable):
    return _any_orig(_record("any", iterable))


_all_orig, _any_orig = builtins.all, builtins.any


def assertion_lines(path: str) -> set[int]:
    tree = ast.parse(Path(path).read_text())
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            for n in ast.walk(node):
                out.add(getattr(n, "lineno", node.lineno))
        elif isinstance(node, ast.Call):
            f = node.func
            name = (f.id if isinstance(f, ast.Name)
                    else f.attr if isinstance(f, ast.Attribute) else "")
            if name in CHECK_NAMES:
                for n in ast.walk(node):
                    ln = getattr(n, "lineno", None)
                    if ln is not None:
                        out.add(ln)
    return out


def source_line(path: str, lineno: int) -> str:
    lines = Path(path).read_text().splitlines()
    return lines[lineno - 1].strip()[:140] if 0 < lineno <= len(lines) else ""


def run_one(script: str) -> dict:
    EMPTY.clear()
    NONEMPTY.clear()
    TARGET["path"] = os.path.abspath(script)
    sites = assertion_lines(script)
    builtins.all, builtins.any = _all, _any
    buf = io.StringIO()
    rc = 0
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = exc.code if isinstance(exc.code, int) else 0
    except BaseException as exc:  # noqa: BLE001
        rc = -1
        buf.write(f"\nEXCEPTION {exc!r}\n")
    finally:
        builtins.all, builtins.any = _all_orig, _any_orig

    vac = []
    for (lineno, kind), n in sorted(EMPTY.items()):
        if lineno not in sites:
            continue
        if NONEMPTY.get((lineno, kind)):
            continue  # the same site DID quantify over something, elsewhere
        vac.append({"line": lineno, "kind": kind, "times": n,
                    "source": source_line(script, lineno)})
    return {"script": script, "rc": rc,
            "vacuous_sites": len(vac),
            "vacuous_calls": sum(v["times"] for v in vac),
            "quantifier_sites_in_checks":
                len({ln for (ln, _k) in list(EMPTY) + list(NONEMPTY)
                     if ln in sites}),
            "sites": vac}


def main() -> int:
    rows = []
    for script in sys.argv[1:]:
        r = run_one(script)
        rows.append(r)
        name = Path(script).name
        print(f"RESULT {name}:vacuous_assertion_sites={r['vacuous_sites']} sites")
        print(f"RESULT {name}:quantifier_sites_in_checks="
              f"{r['quantifier_sites_in_checks']} sites")
        for v in r["sites"]:
            print(f"       {name}:{v['line']}  {v['kind']}()x{v['times']}  {v['source']}")
        print(f"       rc={r['rc']}", flush=True)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00  (call counts; no CPU-time claim)")
    Path("tools/audit/round3/D3/vacuous.json").write_text(json.dumps(
        {"baseline_sha": "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1",
         "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
