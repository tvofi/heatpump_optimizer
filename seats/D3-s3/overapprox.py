#!/usr/bin/env python3
"""D3.M5: what the scoped gate runs on a body-only edit of each of seat
D3-s3's production files that the selected script cannot execute.

Metric (one line): for each production .py file F in the seat's cells, the
scripts tests/closure.py:select([F]) puts in RUN whose traced, unmutated
run (reach/*.json, written by prescreen.py / trace_extra.py / drift_reach.py
with tests/mutation_table.py's own tracer) executes NO line inside any
function body of F and does not read F as text -- WASTED(F); the count of
(F, script) wasted pairs, and their summed cost in tests/closures.json
`recorded.seconds` (env_drift.py and golden.py, recorded as ~1 s stubs, are
costed at their measured --all wall from the pre-screen baseline, marked
provisional). Count key: what select() delivers (the gate's own plan) and
what production code objects fire LINE events on -- never a closure entry
or a script attribute alone. A script with no usable trace (stress.py,
card*.mjs, golden.py itself, harness_headers.py, typing_ruler.py's mypy) is
never counted wasted: UNKNOWN, conservative.
A body-only edit is the shape of most behavioural diffs; an edit to
module-level code (constants, class bodies, signatures) executes at import
and is not claimed here.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/overapprox.py [--perturb-drop N] [--null-any-line]
Perturbation: --perturb-drop N rewrites a private copy of tests/closures.json
(closure.CLOSURES patched in memory) with the first N wasted (F, script)
pairs' F removed from that script's closure, skipping env_drift.py (the
any-integration-change belt re-adds it) and PRODUCERS (re-added as a
producer): wasted_pairs must fall by exactly N. Null control: --null-any-line keys WASTED on "executes no
line of F at all" (import included): the file-granular excess. Measured 28
= 21 stale entries (D3-s3-01, stale_closure.py) + 7 env_drift belt pairs;
the body-granular excess this finding claims is wasted_imported_pairs, the
pairs that remain when those are taken out.
Expected: exact counts (deterministic traces); seconds are recorded values
(exact) except the two stub-recorded scripts (provisional).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import shutil
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(HERE))
import closure  # noqa: E402  (the gate's selector, the instrument under test)
import enumerate as en  # noqa: E402
import mutation_table as mt  # noqa: E402
import reach_census as rc  # noqa: E402  (its --lenient acceptance rule)

# measured --all walls of the two stub-recorded scripts (pre-screen baseline
# of env_drift.py --all HEAD^1 on this box, provisional; golden.py's default
# mode execs the same step)
STUB_WALL = {"tests/env_drift.py": 313.0, "tests/golden.py": 313.0}


def body_lines(path: Path) -> set[int]:
    tree = ast.parse(path.read_text())
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for st in node.body:
                out.update(range(st.lineno, (st.end_lineno or st.lineno) + 1))
    return out


def load_rows() -> dict[str, dict]:
    rows = {}
    for p in sorted((HERE / "reach").glob("*.json")):
        r = json.loads(p.read_text())
        rows[r["script"]] = r
    for p in sorted((HERE / "reach_red").glob("*.json")):
        r = json.loads(p.read_text())
        if rows.get(r["script"], {}).get("reach") is None:
            rows[r["script"]] = r
    usable = {}
    for s, r in rows.items():
        if r["reach"] is None:
            continue
        bad = [p for p in r["reach"]["problems"] if not rc.accepted(s, p)]
        if not bad:
            usable[s.replace("[capture]", "")] = r
    return usable


def main() -> int:
    argv = sys.argv[1:]
    drop_n = int(argv[argv.index("--perturb-drop") + 1]) if "--perturb-drop" in argv else 0
    any_line = "--null-any-line" in argv
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    rows = load_rows()
    rec = json.loads(closure.CLOSURES.read_text())["recorded"]
    files = sorted(f for f in en.cells()
                   if f.startswith(mt.PKG) and f.endswith(".py"))

    imported: list = []   # wasted pairs whose run DID import F (executes
                          # module-level lines): granularity, not staleness

    def measure():
        wasted, unknown, ran = [], Counter(), Counter()
        imported.clear()
        per_file = {}
        for f in files:
            plan = closure.select([f])
            assert plan["mode"] == "scoped", (f, plan["reason"])
            body = body_lines(ROOT / f)
            w_s = 0.0
            for s in plan["run"]:
                ran[f] += 1
                r = rows.get(s)
                if r is None:
                    unknown[f] += 1
                    continue
                hits = set(r["reach"]["hits"].get(f, ()))
                seen = hits if any_line else hits & body
                if not seen and f not in r["reach"]["reads"]:
                    cost = STUB_WALL.get(s, float(rec.get(s, {}).get("seconds", 0.0)))
                    wasted.append((f, s, cost))
                    w_s += cost
                    if hits:
                        imported.append((f, s, cost))
            per_file[f] = w_s
        return wasted, unknown, ran, per_file

    if drop_n:
        wasted0, *_ = measure()
        tmp = Path(tempfile.mkdtemp(prefix="d3s3-overapprox-"))
        cj = tmp / "closures.json"
        shutil.copy(closure.CLOSURES, cj)
        data = json.loads(cj.read_text())
        dropped = []
        for f, s, _ in wasted0:
            if len(dropped) == drop_n:
                break
            if s == "tests/env_drift.py" or any(
                    s in prods for prods in closure.PRODUCERS.values()):
                continue  # the belt / a PRODUCERS edge re-adds it regardless
            data["closures"][s] = [x for x in data["closures"][s] if x != f]
            dropped.append((f, s))
        cj.write_text(json.dumps(data))
        closure.CLOSURES = cj
        print(f"perturbation: removed {len(dropped)} wasted pair(s) from a "
              f"private closures.json: {dropped}")

    wasted, unknown, ran, per_file = measure()
    by_script = Counter(s for _, s, _ in wasted)
    secs_by_script = Counter()
    for _, s, c in wasted:
        secs_by_script[s] += c
    total_pairs = sum(ran.values())
    print(f"RESULT files={len(files)} count")
    print(f"RESULT selected_pairs={total_pairs} count")
    print(f"RESULT unknown_pairs={sum(unknown.values())} count (no usable trace; never counted wasted)")
    print(f"RESULT wasted_pairs={len(wasted)} count")
    print(f"RESULT wasted_share={len(wasted) / total_pairs:.3f} ratio")
    print(f"RESULT wasted_imported_pairs={len(imported)} count (the run imports "
          f"F, executing its module-level lines, and no function body line)")
    print(f"RESULT wasted_imported_seconds_sum={sum(c for *_, c in imported):.0f} s")
    print(f"RESULT wasted_imported_recorded_only_sum="
          f"{sum(c for _, s_, c in imported if s_ not in STUB_WALL):.0f} s")
    for s, n in by_script.most_common():
        print(f"RESULT wasted[{s}]={n} files, {secs_by_script[s]:.0f} s summed")
    vals = sorted(per_file.values())
    mean = sum(vals) / len(vals)
    print(f"RESULT wasted_seconds_per_body_edit_mean={mean:.0f} s "
          "(recorded seconds; env_drift/golden at provisional measured wall)")
    # leave-one-out over the files (cells): range and mean without the cell
    # that most favours the claim (the largest waste)
    top = max(per_file, key=per_file.get)
    loo = (sum(vals) - per_file[top]) / (len(vals) - 1)
    print(f"RESULT loo_cells={len(vals)} count")
    print(f"RESULT loo_min={vals[0]:.0f} s")
    print(f"RESULT loo_max={vals[-1]:.0f} s ({top})")
    print(f"RESULT loo_mean_drop_max={loo:.0f} s")
    no_env = [per_file[f] - sum(c for g, s, c in wasted
                                if g == f and s in STUB_WALL) for f in files]
    print(f"RESULT wasted_seconds_per_body_edit_mean_recorded_only="
          f"{sum(no_env) / len(no_env):.0f} s (stub-recorded scripts excluded)")
    for f in sorted(files, key=lambda f: -per_file[f])[:12]:
        ws = [s.split('/')[-1] for g, s, _ in wasted if g == f]
        print(f"  {f.split('/')[-1]}: {per_file[f]:.0f} s over {len(ws)} of "
              f"{ran[f]} selected: {', '.join(ws)}")
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(
            {"wasted": wasted, "per_file": per_file,
             "unknown": dict(unknown), "ran": dict(ran)}, indent=0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
