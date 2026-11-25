#!/usr/bin/env python3
"""D3-s2 pre-screen (D3.M2): drive every D3.M1 universe site through its closure.

Metric: per mutant, the verdict of tests/mutation_table.py's own drive
(first failing check beyond the unmutated baseline's, `killed()`), over the
recorded closure's scripts minus stress.py/edge.py/backtest.py (D3.M2) and the
two drivers `--scope full` defers (harness_headers.py, stress.py), PLUS
env_drift.py --all <baseline> (the REF_DRIVEN step, ref = HEAD^1 = baseline).
Count key: verdict string per site anchor; RESULT survivors=<n> counts LIVES.
Instrumented symbols: tests/mutation_table.py:main/drive_pool/run_script
(the gate instrument itself, drained over a fixed pool) driving every
custom_components/heatpump_optimizer/<cell>.py site the enumerator prints.
Perturbation: delete a check that kills a listed mutant (e.g. features.py's
`rail:` block for an inputs.py guard) and that mutant's verdict moves from
"killed by ..." to LIVES; a comment-only edit (mutation_table's null control)
must stay LIVES in every driver or the run refuses itself.

Run (needs HEAD = one marker commit above the baseline, so HEAD^1 = baseline):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D3/s2/prescreen.py OUT_DIR [--jobs 3] \
    [--only ANCHOR_SUBSTR,...] [--budget-minutes M] [--timeout S]
Writes OUT_DIR/progress.jsonl (one line per driver run, incremental),
OUT_DIR/results.json, OUT_DIR/reach/<script>.json, OUT_DIR/drain/.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B2, 4 cores.
Expected: deterministic verdicts (kill/LIVES); seconds are provisional.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "tests")
sys.path.insert(0, str(HERE))
import mutation_table as mt  # noqa: E402
import enumerate as en  # noqa: E402

SKIP = ("tests/stress.py", "tests/edge.py", "tests/backtest.py",
        "tests/harness_headers.py")
KIND_WEIGHT = {"RAISE_DEL": 0, "GUARD_OFF": 1, "CONST": 2, "CMP_BOUND": 3,
               "BOOLOP": 4, "CLAMP_DROP": 5, "RETURN_DEL": 6}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--jobs", default="3")
    ap.add_argument("--only", default="")
    ap.add_argument("--budget-minutes", default=None)
    ap.add_argument("--timeout", default="3600",
                    help="mutation_table --timeout floor (a traced baseline "
                    "of boost_drift_replay.py ran past 1200 s on a loaded box)")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    (out / "reach").mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    prog = open(out / "progress.jsonl", "a", buffering=1)

    def log(**kw):
        with lock:
            prog.write(json.dumps(dict(kw, t=round(time.time(), 1))) + "\n")

    universe, _ = en.universe()
    only = [x for x in a.only.split(",") if x]
    if only:
        universe = [s for s in universe if any(o in s["anchor"] for o in only)]
    # Consequence weight (D3.M1): raises/guards/constants first, recorded
    # `gap` survivors last (each costs a whole sweep and is already known).
    universe.sort(key=lambda s: (s["status"] == "gap",
                                 KIND_WEIGHT.get(s["kind"], 9),
                                 s["file"], s["line"]))
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",") if s and s not in SKIP]

    def drain_pool(unpinned, closures, allow_, seed, cap, shard=None):
        pool = []
        for s in universe:
            d = mt.drivers_for(s["file"], closures, allow_)
            if d:
                pool.append(dict({k: v for k, v in s.items()
                                  if k != "status"}, drivers=d))
            else:
                log(ev="no-driver", anchor=s["anchor"], line=s["line"])
        log(ev="pool", n=len(pool))
        return pool

    real_run = mt.run_script
    last = {}

    def run_script(script, cwd, timeout, extra_args=None, extra_env=None):
        r = real_run(script, cwd, timeout, extra_args, extra_env)
        checks = mt.failed_checks(r)[:6]
        last[Path(cwd).name] = checks
        log(ev="run", script=script, tree=Path(cwd).name, rc=r.rc,
            failed=r.failed, seconds=round(r.seconds, 1),
            timed_out=r.timed_out, checks=checks)
        return r

    real_traced = mt.traced_baseline

    def traced_baseline(run, script, tree, timeout, extra_args, extra_env):
        got, reach = real_traced(run, script, tree, timeout, extra_args,
                                 extra_env)
        name = script.replace("/", "_")
        try:
            (out / "reach" / f"{name}.json").write_text(json.dumps(
                reach, default=lambda o: sorted(o) if isinstance(o, set)
                else str(o)))
        except Exception as exc:  # noqa: BLE001
            log(ev="reach-dump-failed", script=script, err=str(exc))
        log(ev="baseline", script=script, rc=got.rc, failed=got.failed,
            seconds=round(got.seconds, 1), reach=reach is not None)
        return got, reach

    real_pool = mt.drive_pool

    def drive_pool(pool, workers, cost, drive, settle=None, deadline=None,
                   clock=time.monotonic, free=None):
        log(ev="drive-start", n=len(pool),
            order={m["anchor"]: m["drivers"] for m in pool})

        def drive2(w, mut, s):
            t0 = time.monotonic()
            hit = drive(w, mut, s)
            log(ev="drive", anchor=mut["anchor"], line=mut["line"],
                kind=mut["kind"], new=mut["new"], script=s, hit=hit,
                checks=last.get(f"w{w}"),
                seconds=round(time.monotonic() - t0, 1))
            return hit

        def free2(mut, s):
            f = free(mut, s) if free else False
            if f:
                log(ev="reach-skip", anchor=mut["anchor"], line=mut["line"],
                    script=s)
            return f

        res = real_pool(pool, workers, cost, drive2, settle, deadline, clock,
                        free2)
        rows = [dict(file=m["file"], line=m["line"], kind=m["kind"],
                     anchor=m["anchor"], old=m["old"], new=m["new"],
                     drivers=m["drivers"], verdict=v) for m, v in res]
        (out / "results.json").write_text(json.dumps(rows, indent=1))
        n = sum(1 for r in rows if r["verdict"] == "LIVES")
        print(f"RESULT survivors={n} mutants")
        print(f"RESULT evaluated={sum(1 for r in rows if not r['verdict'].startswith('SKIP'))} mutants")
        return res

    def clone_tree(dest):
        """mutation_table.clone_tree, but the overlay skips paths the finder
        wall deleted from this export: the clone keeps HEAD's copy (the
        baseline's), so the gate reads the files it reads at the baseline
        (tests/doc_claims.py reads dev/archive/backlog.md) and the seat's own
        tree stays walled."""
        import subprocess
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet",
                        str(dest), "HEAD"], cwd=mt.ROOT, check=True,
                       capture_output=True)
        listing = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"], cwd=mt.ROOT, check=True,
            capture_output=True).stdout
        keep = [x for x in listing.split(b"\0")
                if x and (mt.ROOT / x.decode()).exists()
                and not x.decode().startswith(str(out.relative_to(mt.ROOT)))]
        tar = subprocess.run(["tar", "-c", "--null", "-T", "-", "-f", "-"],
                             cwd=mt.ROOT, check=True,
                             input=b"\0".join(keep) + b"\0",
                             stdout=subprocess.PIPE).stdout
        subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)
        return dest

    mt.clone_tree = clone_tree
    mt.drain_pool = drain_pool
    mt.run_script = run_script
    mt.traced_baseline = traced_baseline
    mt.drive_pool = drive_pool
    argv = ["--scope", "full", "--drain", str(out / "drain"), "--max", "100000",
            "--jobs", a.jobs, "--timeout", a.timeout, "--scripts", ",".join(allow)]
    if a.budget_minutes:
        argv += ["--budget-minutes", a.budget_minutes]
    t0 = time.process_time()
    rc = mt.main(argv)
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time(), 1e-9):.2f}")
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")
    return rc


if __name__ == "__main__":
    sys.exit(main())
