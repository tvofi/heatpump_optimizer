#!/usr/bin/env python3
"""Does a full-net kill by a slow driver reproduce? (box D3-u1b, D3.M3)

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/entities_failline.py \
         [--script tests/entities.py] [--jobs N] [--reps R] [--out FILE.jsonl] (<key> ... | --null | --keys FILE)

prescreen.py `complete` records a kill when a driver is red with more failing
checks than its traced baseline, but keeps only the tail of the driver's
stdout, so a kill by tests/entities.py or tests/features.py rarely names the
check that fired. This harness re-drives recorded mutants
(state/results/complete/<key>.json, the `mutant` old->new line edit) one per
private detached worktree of HEAD under the temp root, runs the driver alone
there with its full stdout kept, and reports rc, the driver's own summary
line and the FAIL lines not printed by the unmutated tree (digits normalised,
because self-test probes print FAIL lines with timings on a green run too).
`--null` drives the unmutated tree: the null control, which must stay rc=0.
`--shared-env` leaves TMPDIR and HPO_PLANDATA as inherited, shared by every
tree, which is how prescreen.py runs its workers. `--jobs N` runs N trees at once, the concurrency prescreen.py's 4 workers had.

Instrumented symbol: the driver (tests/entities.py, tests/features.py) on the
production line each mutant edits. Metric (one line): per key and rep, rc of
the driver alone on the mutated tree; reproduced = rc != 0 in every rep.
Count key: the driver's exit status and its own "N of M ... FAILED" summary.
Perturbation: the unmutated tree (--null) drives reproduced to 0; a mutant
that breaks the published entity set (e.g. one raising in a sensor) drives
it to 1.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RES = HERE / "state" / "results" / "complete"
SHARED = False
NORM = re.compile(r"\d+(\.\d+)?")


def drive(key, script, rep):
    tmp = Path(tempfile.mkdtemp(prefix="d3s1-efl-"))
    tree = tmp / "t"
    subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-q", "--detach", str(tree), "HEAD"], check=True)
    t0 = time.time()
    try:
        if key != "NULL":
            m = json.loads((RES / f"{key}.json").read_text())["mutant"]
            f = tree / m["file"]
            lines = f.read_text().splitlines(keepends=True)
            assert lines[m["line"] - 1].rstrip("\n") == m["old"], (key, lines[m["line"] - 1])
            lines[m["line"] - 1] = m["new"] + "\n"
            f.write_text("".join(lines))
        env = dict(os.environ, PYTHONPATH="tests/hastub")
        if not SHARED:  # private temp + plan data per tree; --shared-env runs as prescreen.py does
            env.update(HPO_PLANDATA=str(tmp / "plandata"), TMPDIR=str(tmp))
        p = subprocess.run([sys.executable, script], cwd=tree, env=env,
                           capture_output=True, text=True, timeout=3600)
        fails = sorted({NORM.sub("N", ln.strip())[:300] for ln in p.stdout.splitlines()
                        if re.match(r"\s*FAIL\b", ln)})
        summ = [ln.strip() for ln in p.stdout.splitlines()
                if re.search(r"CHECKS (FAILED|PASSED)|FAILED|PASSED", ln)][-1:]
        return {"key": key, "script": script, "rep": rep, "rc": p.returncode,
                "summary": summ[0] if summ else "", "fails": fails,
                "stderr_tail": p.stderr[-600:], "wall": round(time.time() - t0, 1)}
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(tree)])
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--keys-file")
    ap.add_argument("--script", default="tests/entities.py")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--out")
    ap.add_argument("--shared-env", action="store_true")
    a = ap.parse_args()
    global SHARED
    SHARED = a.shared_env
    keys = list(a.keys)
    if a.keys_file:
        keys += [l.strip() for l in open(a.keys_file) if l.strip()]
    if a.null:
        keys.append("NULL")
    done = set()
    if a.out and os.path.exists(a.out):
        for ln in open(a.out):
            r = json.loads(ln)
            done.add((r["key"], r["script"], r["rep"]))
    work = [(k, rep) for rep in range(a.reps) for k in keys if (k, a.script, rep) not in done]
    with ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(lambda kr: drive(kr[0], a.script, kr[1]), work):
            print(f"RUN key={r['key']} rep={r['rep']} rc={r['rc']} wall={r['wall']}s summary={r['summary']!r}", flush=True)
            if a.out:
                with open(a.out, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    if a.out:
        rows = [json.loads(ln) for ln in open(a.out) if json.loads(ln)["script"] == a.script]
        null_fails = set().union(*[set(r["fails"]) for r in rows if r["key"] == "NULL"]) if any(r["key"] == "NULL" for r in rows) else set()
        by = {}
        for r in rows:
            by.setdefault(r["key"], []).append(r)
        red_null = sum(r["rc"] != 0 for r in by.get("NULL", []))
        print(f"RESULT null_runs={len(by.get('NULL', []))} null_red={red_null}")
        rep = [k for k, rs in by.items() if k != "NULL" and all(r["rc"] != 0 for r in rs)]
        nrep = [k for k, rs in by.items() if k != "NULL" and not all(r["rc"] != 0 for r in rs)]
        print(f"RESULT mutants={len(by) - ('NULL' in by)} reproduced={len(rep)} not_reproduced={len(nrep)}")
        for k in rep:
            new = sorted(set().union(*[set(r["fails"]) for r in by[k]]) - null_fails)
            print(f"  reproduced {k} {by[k][0]['summary']!r} new_fail={new[:3]}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
