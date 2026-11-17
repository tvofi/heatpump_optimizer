#!/usr/bin/env python3
"""D3.M2/M5 pre-screen for seat D3-s3: drive a chosen list of inventory sites
through tests/mutation_table.py's OWN machinery (worker worktrees, traced
baselines, reach-skip, null control, `killed()`), each mutant only by the
scripts of its measured closure (tests/closures.json) minus the brief's
pre-screen exclusions (stress.py, edge.py, backtest.py), with env_drift.py
driven as the gate drives it: `--all <ref>`, ref = HEAD^1 = the baseline.

Metric (one line): per mutant, the number of closure scripts whose run on the
mutated tree names more failing checks than the unmutated baseline run
(mutation_table.killed); a SURVIVOR is a mutant with 0.
Count key: the production line's delivered behaviour as the drivers observe
it -- the mutant is a one-line edit of the named production symbol.

Hooks: tests/mutation_table.py:main (via sampled_pool -> our pool),
       mutation_table.run_script (logs wall + child CPU per driver run),
       mutation_table.drive_pool (with --overlap: never stops at a kill, so
       every closure script runs on every mutant -- the kill-overlap matrix).
Production symbols driven: each site's enclosing def, named by its anchor.

Command (from the export root, after ONE marker commit so HEAD^1 = baseline):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D3/s3/prescreen.py \
    --sites dev/audit/rounds/round11/D3/s3/selection.txt --jobs 3 \
    --out dev/audit/rounds/round11/D3/s3/prescreen.json [--overlap]
Perturbation (the instrument's own control): --null-only drives the
mutation_table null control (a comment-only edit) as the pool; every mutant's
kill count must drop to 0 for it. Expected: survivors as in REPORT.md (exact
per mutant; a re-run on another BLAS may move an env_drift kill, which is the
point of claimed drift).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU.
Every wall/CPU number this prints is provisional (shared box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import resource
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
PRESCREEN_SKIP = {"tests/stress.py", "tests/edge.py", "tests/backtest.py",
                  # --scope full drops it (mt.scope_deferred); mirror that
                  *mt.scope_deferred("full")}

_ctx = threading.local()
RUNLOG: list[dict] = []
OUTCOMES: dict[str, dict[str, object]] = {}
VERDICTS: dict[str, str] = {}
LOCK = threading.Lock()


def make_cpu_wrapper(tmp: Path) -> Path:
    """An interpreter shim recording each driver process tree's CPU."""
    log = tmp / "cpu.log"
    shim = tmp / "pyshim.py"
    shim.write_text(
        "import os, sys, subprocess, time, resource, json\n"
        f"REAL = {sys.executable!r}\n"
        "t = time.monotonic()\n"
        "rc = subprocess.call([REAL, *sys.argv[1:]])\n"
        "ru = resource.getrusage(resource.RUSAGE_CHILDREN)\n"
        f"with open({str(log)!r}, 'a') as f:\n"
        "    f.write(json.dumps({'argv': sys.argv[1:3], 'cwd': os.getcwd(),\n"
        "        'rid': os.environ.get('D3S3_RUN'),\n"
        "        'pid': os.getpid(), 'wall': time.monotonic() - t,\n"
        "        'cpu': ru.ru_utime + ru.ru_stime, 'rc': rc}) + '\\n')\n"
        "sys.exit(rc)\n")
    sh = tmp / "python3"
    sh.write_text(f"#!/bin/sh\nexec {sys.executable} {shim} \"$@\"\n")
    sh.chmod(0o755)
    return sh


def load_sites(path: Path) -> list[dict]:
    want = []
    for ln in path.read_text().splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            fl, kind = ln.split()
            f, line = fl.rsplit(":", 1)
            want.append((mt.PKG + f if not f.startswith(mt.PKG) else f,
                         int(line), kind))
    budgets = mt.load_budgets()
    unpinned = mt.unpinned_sites(budgets, mt.inventory())
    by = {}
    for s in unpinned:
        by.setdefault((s["file"], s["line"], s["kind"]), s)
    out = []
    for w in want:
        if w not in by:
            raise SystemExit(f"not an unpinned inventory site: {w}")
        out.append(dict(by[w]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--overlap", action="store_true")
    ap.add_argument("--no-drift-reach", action="store_true")
    ap.add_argument("--timeout", type=int, default=6000)
    ap.add_argument("--only", default="",
                    help="comma list of drivers to keep (overlap subsets)")
    args = ap.parse_args()
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    pool = load_sites(Path(args.sites))
    closures = mt.load_closures()
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",")
             if s and s not in PRESCREEN_SKIP]
    if args.only:
        keep = set(args.only.split(","))
        allow = [s for s in allow if s in keep]
    for m in pool:
        m["drivers"] = mt.drivers_for(m["file"], closures, allow)

    tmp = Path(tempfile.mkdtemp(prefix="d3s3-prescreen-"))
    shim = make_cpu_wrapper(tmp)

    orig_run = mt.run_script

    def logged_run(script, cwd, timeout, extra_args=None, extra_env=None):
        mut = getattr(_ctx, "mut", None)
        with LOCK:
            rid = f"r{len(RUNLOG)}-{threading.get_ident()}-{time.monotonic_ns()}"
        run = orig_run(script, cwd, timeout, extra_args,
                       {**(extra_env or {}), "D3S3_RUN": rid})
        with LOCK:
            RUNLOG.append({"script": script, "cwd": str(cwd), "rid": rid,
                           "mutant": mut["anchor"] + f"@{mut['line']}"
                           if mut else "baseline-or-null",
                           "rc": run.rc, "failed": run.failed,
                           "wall": round(run.seconds, 1),
                           "timed_out": run.timed_out})
        return run

    mt.run_script = logged_run
    sys.executable = str(shim)   # every driver process tree's CPU is logged

    orig_drive_pool = mt.drive_pool

    def drive_pool(pool_, workers, cost, drive, **kw):
        def wrapped(w, mut, s):
            _ctx.mut = mut
            try:
                hit = drive(w, mut, s)
            finally:
                _ctx.mut = None
            key = f"{mut['file']}:{mut['line']} {mut['kind']}"
            with LOCK:
                OUTCOMES.setdefault(key, {})[s] = hit
            return False if args.overlap else hit
        free = kw.get("free")

        def free_logged(mut, s):
            skip = bool(free and free(mut, s))
            if skip:
                key = f"{mut['file']}:{mut['line']} {mut['kind']}"
                with LOCK:
                    OUTCOMES.setdefault(key, {})[s] = "reach-skip"
            return skip
        if free is not None:
            kw["free"] = free_logged
        res = orig_drive_pool(pool_, workers, cost, wrapped, **kw)
        for mut, v in res:
            VERDICTS[f"{mut['file']}:{mut['line']} {mut['kind']}"] = v
        return res

    mt.drive_pool = drive_pool

    # The finder wall removed dev/archive/backlog.md from this export, so
    # doc_claims.py's docs-build check is red at the unmutated baseline for
    # the environment, not the code (one check: the how-it-works.md link).
    # Tolerate exactly that red; killed() still needs MORE failing checks
    # than this baseline names, so a mutant kill is read as before.
    orig_refusal = mt.baseline_refusal

    def refusal(baseline, scope, recorded=None):
        keep = {}
        for s_, run in baseline.items():
            names = mt.failed_checks(run)
            if (s_ == "tests/doc_claims.py" and run.failed == 1
                    and len(names) == 1 and "dev/archive/backlog.md" in names[0]):
                print(f"  {s_}: baseline red ONLY on the finder-wall artifact "
                      f"(dev/archive/backlog.md absent); tolerated, kill = >1 FAIL")
                continue
            # entities.py in this export: exactly two machinery checks are red
            # at the unmutated baseline (closure.py's partial re-derive and the
            # PR-template acceptance arm), neither reading a production file.
            # Its other FAIL lines are the nightly probes' deliberate negatives.
            if (s_ == "tests/entities.py" and run.failed == 2
                    and "and is accepted when it does" in names
                    and any(n.startswith("the template arm turns the acceptance red")
                            for n in names)):
                print(f"  {s_}: baseline red ONLY on two machinery checks of "
                      f"this export (closure partial re-derive, PR-template "
                      f"acceptance); tolerated, kill = >2 FAIL")
                continue
            keep[s_] = run
        return orig_refusal(keep, scope, recorded)
    mt.baseline_refusal = refusal

    # Persist every traced baseline's reach (#1930 fold (e)) so the census
    # over the WHOLE D3.M1 universe (reach_census.py) reads which drivers
    # execute each unpinned line.
    reach_dir = Path(args.out).with_suffix("").parent / "reach"
    reach_dir.mkdir(exist_ok=True)
    orig_traced = mt.traced_baseline

    def traced(run, script, tree, timeout, extra_args, extra_env):
        got, reach = orig_traced(run, script, tree, timeout, extra_args,
                                 extra_env)
        rec = {"script": script, "rc": got.rc, "failed": got.failed,
               "seconds": round(got.seconds, 1), "reach": None}
        if reach is not None:
            rec["reach"] = {
                "hits": {k: v for k, v in reach["hits"].items()
                         if k.startswith(mt.PKG)},
                "reads": [r for r in reach["reads"] if r.startswith(mt.PKG)],
                "problems": mt.reach_problems(reach),
                "processes": reach["processes"]}
        (reach_dir / (script.replace("/", "_") + ".json")).write_text(
            json.dumps(rec, indent=0))
        return got, reach
    mt.traced_baseline = traced

    # env_drift.py's run cannot be traced (its capture child's PYTHONPATH is
    # rebuilt), so the lane drives it on every pair. drift_reach.py traced
    # that very child (`env_drift.py --capture <tree> <out> --all`, the only
    # process of the run that imports the mutated tree; the reference side
    # captures the unmutated HEAD^1 worktree). Substitute its reach so
    # env_drift is reach-skipped exactly where its capture never executes
    # the line. --no-drift-reach turns this off.
    cap = HERE / "reach" / "tests_env_drift.py_capture.json"
    if not args.no_drift_reach and cap.exists():
        crow = json.loads(cap.read_text())
        inner_traced = mt.traced_baseline

        def traced_with_drift(run, script, tree, timeout, extra_args, extra_env):
            got, reach = inner_traced(run, script, tree, timeout, extra_args,
                                      extra_env)
            if script == "tests/env_drift.py" and got.rc == 0 and not got.timed_out:
                r = crow["reach"]
                reach = {"hits": r["hits"], "reads": r["reads"], "foreign": [],
                         "untraced": [], "processes": r["processes"], "rc": 0}
                print("  tests/env_drift.py: reach = its traced --capture "
                      "child (drift_reach.py)")
            return got, reach
        mt.traced_baseline = traced_with_drift
    mt.sampled_pool = lambda *a, **k: (pool, 0)
    os.environ.setdefault("GOLDEN_REF", "HEAD^1")
    t0 = time.monotonic()
    rc = mt.main(["--scope", "full", "--jobs", str(args.jobs),
                  "--scripts", ",".join(allow), "--max", str(len(pool)),
                  "--timeout", str(args.timeout)])
    wall = time.monotonic() - t0
    cpu_log = [json.loads(x) for x in (tmp / "cpu.log").read_text().splitlines()
               ] if (tmp / "cpu.log").exists() else []
    result = {"rc": rc, "wall_s": round(wall, 1), "overlap": args.overlap,
              "drivers_allowed": allow,
              "pool": [{k: m[k] for k in ("file", "line", "kind", "old", "new",
                                          "anchor", "drivers")} for m in pool],
              "outcomes": OUTCOMES, "verdicts": VERDICTS, "runs": RUNLOG, "cpu": cpu_log}
    Path(args.out).write_text(json.dumps(result, indent=1, default=str))
    killed = [k for k, v in OUTCOMES.items() if any(x is True for x in v.values())]
    survivors = [f"{m['file']}:{m['line']} {m['kind']}" for m in pool]
    survivors = [k for k in survivors if k not in killed
                 and not str(VERDICTS.get(k, "")).startswith("SKIP")]
    print(f"RESULT mutants={len(pool)} count")
    print(f"RESULT driven={len(VERDICTS)} count")
    print(f"RESULT killed={len(killed)} count")
    print(f"RESULT survivors={len(survivors)} count")
    for k in survivors:
        print(f"SURVIVOR {k}")
    print(f"RESULT wall={wall:.0f} s (provisional)")
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
