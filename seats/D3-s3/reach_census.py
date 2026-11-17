#!/usr/bin/env python3
"""D3.M1/M2 reach census and D3.M5 closure over-approximation, seat D3-s3.

Metric (one line): for each unpinned inventory site in the seat's cells
(enumerate.py's universe), the set of pre-screen drivers whose TRACED,
unmutated baseline executed that line (tests/mutation_table.py's reach
tracer, sys.monitoring LINE events, #1930 fold (e)); a site no driver
executed and no driver read as text is REACH-DEAD: no fast script can see its
mutant (mutation_table.never_reaches is the production rule that already
skips such pairs). Count key: the line numbers the production module's code
objects fire LINE events on, i.e. what production executes, never a script
attribute.
M5 half: for each (driver, cell file) pair tests/closures.json records, BODY =
the driver executed at least one line inside a function body of that file
(not only the import-time def/class/constant lines). A pair with BODY false
is closure over-approximation for every body edit: closure.py selects the
driver on such a diff, yet its run cannot execute the edited line.

Hooks: tests/mutation_table.py:traced_baseline / collect / reach_problems /
executable_lines, via prescreen.py, which persists each driver's reach under
reach/ next to this file.
Command (after prescreen.py has written reach/*.json):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D3/s3/reach_census.py [--sites-out PATH]
Perturbation: --drop DRIVER removes one driver's reach row; every site only
that driver executed moves to REACH-DEAD (count goes up, never down); with
--drop of a driver that executed nothing in the cells the count is unchanged
(null control).
Expected: exact counts (deterministic suite; a different BLAS can change which
branch a solver-path line takes, so a handful of solver-adjacent sites may
move). Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3.
Source and trace only: no timing is printed.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402  (this seat's M1 enumerator)


def body_lines(path: Path) -> set[int]:
    """Lines inside any function body (not executed by a bare import)."""
    tree = ast.parse(path.read_text())
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for st in node.body:
                out.update(range(st.lineno, (st.end_lineno or st.lineno) + 1))
    return out


def main() -> int:
    argv = sys.argv[1:]
    drop = set()
    sites_out = None
    while argv:
        a = argv.pop(0)
        if a == "--drop":
            drop.add(argv.pop(0))
        elif a == "--sites-out":
            sites_out = argv.pop(0)
    rows = {}
    for p in sorted((HERE / "reach").glob("*.json")):
        r = json.loads(p.read_text())
        if r["script"] not in drop:
            rows[r["script"]] = r
    # A row whose run reach_problems refuses (a child it did not trace, a
    # non-Python process) is no proof of never-executed: count its hits, but
    # only a problem-free row may say a line was NOT executed.
    traced_any = {s: r for s, r in rows.items() if r["reach"] is not None}
    clean = {s: r for s, r in traced_any.items()
             if not r["reach"]["problems"]}
    universe = en.universe()
    cells = en.cells()
    closures = mt.load_closures()
    exe_cache: dict[str, set[int]] = {}
    per_kind = Counter()
    dead_kind = Counter()
    by_count = Counter()
    sole = Counter()
    out_rows = []
    dead_files = Counter()
    for s in universe:
        f, ln = s["file"], s["line"]
        if f not in exe_cache:
            exe_cache[f] = mt.executable_lines(ROOT / f)
        executed = sorted(d for d, r in traced_any.items()
                          if ln in set(r["reach"]["hits"].get(f, ())))
        readers = sorted(d for d, r in clean.items()
                         if f in r["reach"]["reads"])
        unclean = sorted(d for d in rows if d not in clean)
        # An untraced driver (no clean reach row) could still see the line;
        # env_drift.py is covered by drift_reach.py's traced capture child
        # (row "tests/env_drift.py[capture]"), the only process of it that
        # imports production code.
        open_untraced = sorted(
            d for d in unclean
            if f in closures.get(d, []) and not (
                f"{d}[capture]" in clean))
        no_instr = ln not in exe_cache[f]
        dead = (not executed and not readers and not no_instr
                and not open_untraced)
        per_kind[s["kind"]] += 1
        by_count[min(len(executed), 5)] += 1
        if len(executed) == 1:
            sole[executed[0]] += 1
        if dead:
            dead_kind[s["kind"]] += 1
            dead_files[f.rsplit("/", 1)[-1]] += 1
        out_rows.append({"site": f"{f}:{ln} {s['kind']}", "anchor": s["anchor"],
                         "executed_by": executed, "read_by": readers,
                         "untraced_drivers": unclean, "open_untraced": open_untraced,
                         "no_instruction": no_instr,
                         "reach_dead": dead})
    n = len(universe)
    nd = sum(r["reach_dead"] for r in out_rows)
    print(f"drivers with a clean trace: {len(clean)}; untraced (drive every "
          f"pair): {sorted(set(rows) - set(clean))}")
    for d, r in sorted(rows.items()):
        probs = (r["reach"] or {}).get("problems") if r["reach"] else ["no trace"]
        print(f"  {d}: rc={r['rc']} problems={probs}")
    print(f"RESULT universe={n} count")
    print(f"RESULT reach_dead={nd} count")
    print(f"RESULT reach_dead_share={nd / n:.3f} ratio")
    for k in sorted(per_kind):
        print(f"RESULT reach_dead[{k}]={dead_kind[k]}/{per_kind[k]} count")
    for c in sorted(by_count):
        print(f"RESULT executed_by_{c}{'+' if c == 5 else ''}_drivers="
              f"{by_count[c]} count")
    for d, c in sole.most_common():
        print(f"RESULT sole_executor[{d}]={c} count")
    print("REACH-DEAD by file: " + ", ".join(f"{k}={v}" for k, v in
                                               dead_files.most_common()))
    # M5: closure over-approximation for the seat's production files.
    pairs = 0
    import_only = []
    for d, r in sorted(clean.items()):
        for f in closures.get(d.replace("[capture]", ""), []):
            if f not in cells or not f.startswith(mt.PKG) or not f.endswith(".py"):
                continue
            pairs += 1
            hits = set(r["reach"]["hits"].get(f, ()))
            body = body_lines(ROOT / f)
            if not (hits & body) and f not in r["reach"]["reads"]:
                import_only.append((d, f, len(hits)))
    print(f"RESULT closure_pairs_traced={pairs} count")
    print(f"RESULT closure_pairs_import_only={len(import_only)} count")
    per_driver = Counter(d for d, _, _ in import_only)
    rec_of = lambda d: d.replace("[capture]", "")  # noqa: E731
    rec = json.load(open(ROOT / "tests/closures.json"))["recorded"]
    for d, c in per_driver.most_common():
        print(f"RESULT import_only[{d}]={c} files "
              f"(recorded {rec.get(rec_of(d), {}).get('seconds')} s per forced run)")
    if sites_out:
        Path(sites_out).write_text(json.dumps(
            {"sites": out_rows, "import_only": import_only}, indent=0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
