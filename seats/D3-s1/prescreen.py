#!/usr/bin/env python3
"""D3-s1 pre-screen: does the measured closure notice a one-line mutant?

Metric (per mutant): KILLED by <driver> | SURVIVED <drivers run> -- a kill is
`tests/mutation_table.py:killed` (red AND more failing checks than the
unmutated, traced baseline of the same driver); a driver whose traced baseline
never executed the mutated line (`mutation_table.reach_skip`, the gate's own
rule) is skipped and named. Count key: the mutant's verdict over the drivers
the GATE runs (`tests/closures.json` closure of its file, `--scripts` default
set, minus the brief's stress/edge/backtest), plus `tests/env_drift.py --all
HEAD^1` (HEAD^1 = 2c84a85c, whose custom_components/ is byte-identical to the
baseline: `git diff --stat HEAD^1 HEAD -- custom_components` is empty).

Instrumented symbols: the production line of each mutant (inventory of
`tests/mutation_table.py:inventory`, site `anchor`), driven through
`mutation_table.run_script` / `killed` / `traced_baseline`.
Perturbation: `--null` drives the comment-only null control (must LIVE);
any mutant listed with `--force-kill-check` (the identity edit) must survive
and a known-pinned site (a `killed_by` ledger row) must be killed.

Commands (repo root, PYTHONPATH=tests/hastub):
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py baseline --workers 3
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --workers 3 [--limit N] [--anchors FILE]
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --full --anchors FILE   # no early stop (kill matrix)
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py null
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py reach      # whole-universe reach table
  python3 dev/audit/rounds/round11/D3/s1/prescreen.py report
Expected: null control LIVES; verdict counts in `report` (exact counts are
contention-immune; every seconds figure is provisional).
Box D3-m5 (D3.M5(b), the kill-overlap matrix, no early stop over every
closure script):
  D3S1_RELAX=0 D3S1_FRESH_TREE=1 D3S1_EXTRA_DRIVERS=tests/edge.py,tests/backtest.py,tests/golden.py,tests/card.mjs,tests/card_drift.mjs \
    python3 dev/audit/rounds/round11/D3/s1/prescreen.py baseline --workers 4
  D3S1_EXTRA_DRIVERS=tests/stress.py python3 .../prescreen.py baseline --workers 1   # alone
  D3S1_RELAX=0 D3S1_FRESH_TREE=1 D3S1_EXTRA_DRIVERS=... D3S1_ONLY=<every driver but stress> \
    python3 .../prescreen.py run --full --mutants dev/audit/rounds/round11/D3/s1/matrix_mutants.json --sub matrix --workers 4
  D3S1_RELAX=0 D3S1_FRESH_TREE=1 D3S1_ONLY=tests/stress.py python3 .../prescreen.py run --full --mutants ... --sub matrix-stress --workers 1
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64, shared box;
box D3R and box D3-m5 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz), each alone.
State: dev/audit/rounds/round11/D3/s1/state/ (resumable); worker trees under $TMPDIR.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import hashlib
import json
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, "tests")
import functools  # noqa: E402
import mutation_table as mt  # noqa: E402
mt.load_closures = functools.lru_cache(maxsize=None)(mt.load_closures)

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"
RESULTS = STATE / "results"
BASE_FILE = STATE / "baselines.json"
REF = "HEAD^1"
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
RELS = [mt.PKG + c + ".py" for c in CELLS]
PRESCREEN_SKIP = {"tests/stress.py", "tests/edge.py", "tests/backtest.py"}
KIND_RANK = {"GUARD_OFF": 0, "RAISE_DEL": 1, "CONST": 2, "CMP_BOUND": 3,
             "BOOLOP": 4, "CLAMP_DROP": 5, "RETURN_DEL": 6}
WT_ROOT = Path(tempfile.gettempdir()) / "d3s1-workers"
LOCK = threading.Lock()


# Box D3-m5 (D3.M5(b), the kill-overlap matrix over EVERY closure script):
# D3S1_EXTRA_DRIVERS adds drivers the pre-screen leaves out -- edge.py,
# backtest.py, stress.py (PRESCREEN_SKIP) and the three DRIVER_EXCLUSIONS:
# golden.py (driven in run.sh's default strict mode, GOLDEN_MODE=strict
# GOLDEN_REF=HEAD^1, which compares the committed fixtures, NOT the
# env_drift step), card.mjs and card_drift.mjs (run under node after their
# producer tests/plan_view.py, closure.py PRODUCERS, on a private
# HPO_PLANDATA). A node driver's reach is its producer's traced reach: the
# node process executes no Python, and the payload is the only way a Python
# line reaches it. D3S1_ONLY restricts a drive to the listed drivers.
NODE = ("tests/card.mjs", "tests/card_drift.mjs")
EXTRA = [x for x in os.environ.get("D3S1_EXTRA_DRIVERS", "").split(",") if x]
ONLY = {x for x in os.environ.get("D3S1_ONLY", "").split(",") if x}


def drivers() -> list[str]:
    clos = mt.load_closures()
    allow = [s for s in mt.DEFAULT_SCRIPTS.split(",") if s not in PRESCREEN_SKIP]
    allow += [s for s in EXTRA if s not in allow]
    return [s for s in allow if any(r in clos.get(s, ()) for r in RELS)]


def run_any(s: str, t: Path, timeout: int, a=None, e=None) -> "mt.ScriptRun":
    """mt.run_script for a Python driver; producer + node for a card driver."""
    if s not in NODE:
        return mt.run_script(s, t, timeout, a, e)
    started = time.monotonic()
    pd = Path(tempfile.mkdtemp(prefix="d3s1-plan-"))
    env = {**os.environ, "PYTHONPATH": "tests/hastub",
           "HPO_PLANDATA": str(pd / "plan.json")}
    env.pop("HPO_REACH_OUT", None)
    env.pop("HPO_REACH_HOOK", None)
    try:
        prod = subprocess.run([sys.executable, "tests/plan_view.py"], cwd=t,
                              env=env, capture_output=True, text=True,
                              timeout=timeout)
        args = [REF] if s == "tests/card_drift.mjs" else []
        try:
            p = subprocess.run(["node", s, *args], cwd=t, env=env,
                               capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return mt.ScriptRun(mt.TIMEOUT_RC, 0, time.monotonic() - started,
                                "", f"{s}: timed out after {timeout}s", True)
    finally:
        shutil.rmtree(pd, ignore_errors=True)
    out = (f"[producer tests/plan_view.py rc={prod.returncode}]\n"
           + prod.stdout[-2000:] + "\n" + p.stdout)
    run = mt.ScriptRun(p.returncode, 0, time.monotonic() - started, out,
                       p.stderr)
    n = mt.failing_count(run)
    if p.returncode != 0 and n == 0:
        # card_drift.mjs prints `card_drift: N problem(s).`; any other red
        # node exit counts one failing check (it named none we can read).
        import re as _re
        m = _re.search(r"card_drift: (\d+) problem", p.stdout)
        n = int(m.group(1)) if m else 1
    return run._replace(failed=n)


def killed_any(s: str, run, base_run) -> bool:
    if s not in NODE:
        return mt.killed(s, run, base_run)
    return run.rc != 0 and run.failed > base_run.failed


def unpinned() -> list[dict]:
    budgets = mt.load_budgets()
    inv = mt.inventory(sorted(mt.PRODUCTION / (c + ".py") for c in CELLS))
    return mt.unpinned_sites(budgets, inv)


def pinned() -> list[dict]:
    budgets = mt.load_budgets()
    inv = mt.inventory(sorted(mt.PRODUCTION / (c + ".py") for c in CELLS))
    loose = {id(s) for s in mt.unpinned_sites(budgets, inv)}
    return [s for s in inv if id(s) not in loose]


def key(m: dict) -> str:
    return hashlib.sha1((m["anchor"] + "|" + m["new"]).encode()).hexdigest()[:16]


def tree(i: int) -> Path:
    d = WT_ROOT / f"w{i}"
    if not (d / ".git").exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet",
                        str(d), "HEAD"], cwd=mt.ROOT, check=True,
                       capture_output=True)
    return d


FRESH = os.environ.get("D3S1_FRESH_TREE", "0") == "1"


def recycle(i: int) -> Path:
    """Box D3R (disk rule): delete a worker's tree after each mutant and
    re-add it, so no mutant leaves files behind for the next one."""
    d = WT_ROOT / f"w{i}"
    subprocess.run(["git", "worktree", "remove", "--force", str(d)],
                   cwd=mt.ROOT, capture_output=True)
    shutil.rmtree(d, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=mt.ROOT, capture_output=True)
    return tree(i)


def spec(script):
    if script == "tests/golden.py":
        return [], {"GOLDEN_MODE": "strict", "GOLDEN_REF": REF}
    return mt.drive_spec(script, REF)


def to_json(run: mt.ScriptRun) -> dict:
    return {"rc": run.rc, "failed": run.failed, "seconds": round(run.seconds, 1),
            "timed_out": run.timed_out,
            "checks": mt.failed_checks(run)[:5],
            "stdout_tail": run.stdout[-1500:], "stderr_tail": run.stderr[-1500:]}


def from_json(d: dict) -> mt.ScriptRun:
    return mt.ScriptRun(d["rc"], d["failed"], d["seconds"],
                        d.get("stdout_tail", ""), d.get("stderr_tail", ""),
                        d.get("timed_out", False))


def timeout_for(script, base) -> int:
    rec = mt.recorded_seconds().get(script, 60.0)
    seen = base.get(script, {}).get("run", {}).get("seconds", rec)
    return mt.driver_timeout(1200, max(rec, seen))


def log(msg: str) -> None:
    line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + msg
    with LOCK:
        print(line, flush=True)
        with open(STATE / "prescreen.log", "a") as f:
            f.write(line + "\n")


def cmd_baseline(args) -> int:
    STATE.mkdir(parents=True, exist_ok=True)
    base = json.loads(BASE_FILE.read_text()) if BASE_FILE.exists() else {}
    todo = [s for s in drivers() if s not in base]
    q: "queue.Queue[str]" = queue.Queue()
    # longest first (recorded seconds)
    rec = mt.recorded_seconds()
    for s in sorted(todo, key=lambda s: -rec.get(s, 60)):
        q.put(s)

    def work(i):
        t = tree(i)
        while True:
            try:
                s = q.get_nowait()
            except queue.Empty:
                return
            a, e = spec(s)
            t0 = time.process_time()
            if s in NODE:
                run = run_any(s, t, mt.driver_timeout(1200, 3 * rec.get(s, 60)))
                pv = json.loads(BASE_FILE.read_text()).get("tests/plan_view.py", {})
                reach = pv.get("reach") if run.rc == 0 else None
                entry = {"run": to_json(run), "reach": reach,
                         "reach_from_producer": "tests/plan_view.py",
                         "reach_problems": mt.reach_problems(reach)}
            else:
                run, reach = mt.traced_baseline(mt.run_script, s, t,
                                                mt.driver_timeout(1200, 3 * rec.get(s, 60)),
                                                a, e)
                entry = {"run": to_json(run), "reach": reach,
                         "reach_problems": mt.reach_problems(reach)}
            with LOCK:
                cur = json.loads(BASE_FILE.read_text()) if BASE_FILE.exists() else {}
                cur[s] = entry
                BASE_FILE.write_text(json.dumps(cur))
            log(f"BASELINE {s} rc={run.rc} failed={run.failed} "
                f"wall={run.seconds:.1f}s reach_ok={not entry['reach_problems']}")
            del t0
    ths = [threading.Thread(target=work, args=(i,)) for i in range(args.workers)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    return 0


def cmd_retrace(args) -> int:
    """Trace a driver whose baseline is red but COMPLETE (its closing
    `N of M ... FAILED` line printed): mutation_table.traced_baseline drops
    the reach of any red run; here the reach is kept, because the run reached
    its summary, and the red count stays the kill threshold (`killed`)."""
    s = args.script
    rec = mt.recorded_seconds()
    t = tree(args.tree_offset or 4)
    with tempfile.TemporaryDirectory(prefix="reach-") as d:
        out = Path(d)
        env = mt.hook_env(out)
        a, e = spec(s)
        traced_env = {**e, **env,
                      "PYTHONPATH": mt.traced_pythonpath(env, "tests/hastub")}
        run = mt.run_script(s, t, mt.driver_timeout(1200, 3 * rec.get(s, 60)),
                            a, traced_env)
        reach = mt.collect(out)
    complete = bool(mt._FAILED.search(run.stdout)) or run.rc == 0
    reach["rc"] = 0 if complete else run.rc
    entry = {"run": to_json(run), "reach": reach if complete else None,
             "reach_problems": (mt.reach_problems(reach) if complete
                                else ["incomplete"]),
             "retraced_red_complete": complete}
    with LOCK:
        cur = json.loads(BASE_FILE.read_text())
        cur[s] = entry
        BASE_FILE.write_text(json.dumps(cur))
    log(f"RETRACE {s} rc={run.rc} failed={run.failed} complete={complete} "
        f"problems={entry['reach_problems']}")
    return 0


def cmd_trace_capture(args) -> int:
    """env_drift.py's only production-executing step is its `--capture` child,
    which it starts with PYTHONPATH reset to tests/hastub, dropping the reach
    hook (so the gate's tracer records no lines for it). Trace that child
    directly, `--all`, and store its reach as env_drift's `capture_reach`."""
    t = tree(args.tree_offset or 7)
    with tempfile.TemporaryDirectory(prefix="reach-cap-") as d:
        out = Path(d)
        env = mt.hook_env(out)
        cap = out / "capture.json"
        e = {**os.environ, **env,
             "PYTHONPATH": mt.traced_pythonpath(env, str(t / "tests" / "hastub"))}
        t0 = time.monotonic()
        p = subprocess.run([sys.executable, "tests/env_drift.py", "--capture",
                            str(t), str(cap), "--all"], cwd=t, env=e,
                           capture_output=True, text=True, timeout=7200)
        reach = mt.collect(out)
    reach["rc"] = p.returncode
    with LOCK:
        cur = json.loads(BASE_FILE.read_text())
        cur["tests/env_drift.py"]["capture_reach"] = reach
        BASE_FILE.write_text(json.dumps(cur))
    log(f"TRACE-CAPTURE rc={p.returncode} wall={time.monotonic() - t0:.1f}s "
        f"problems={mt.reach_problems(reach)} procs={reach['processes']}")
    return 0


def load_base() -> dict:
    return json.loads(BASE_FILE.read_text())


def order(base: dict, ds: list[str]) -> list[str]:
    return sorted(ds, key=lambda s: base[s]["run"]["seconds"])


RELAX = os.environ.get("D3S1_RELAX", "1") == "1"
# D3.M2's pre-screen net is "the FAST scripts of that closure ... plus
# tests/env_drift.py --all": fast = a recorded solo cost (tests/closures.json
# `recorded.seconds`) under FAST_S. The slow ones (optimality, harness_headers,
# boost_drift_replay, features, entities) are deferred to the --full drive
# (D3.M3's full net) and named in each verdict as `deferred_slow`.
FAST_S = float(os.environ.get("D3S1_FAST_S", "120"))


def fast(s: str) -> bool:
    return s == "tests/env_drift.py" or mt.recorded_seconds().get(s, 1e9) < FAST_S


def relaxed_skip(reach, m) -> bool:
    """The gate's reach_skip, plus one relaxation, named in every verdict:
    a run whose ONLY refusal is that it starts `git` (which executes no
    Python line) and whose unrecorded Python processes number at most one is
    read for its executed lines. A survivor relying on this skip is marked
    `relaxed_skipped`, and the re-drive with D3S1_RELAX=0 removes it."""
    if not RELAX or reach is None:
        return False
    if reach["untraced"] or reach.get("rc") not in (0, None):
        return False
    if any(not f.startswith("git ") for f in reach["foreign"]):
        return False
    p = reach["processes"]
    if p["started"] - p["recorded"] > 1:
        return False
    rel = m["file"]
    if rel in reach["reads"]:
        return False
    if rel not in mt._EXECUTABLE:
        mt._EXECUTABLE[rel] = mt.executable_lines(mt.ROOT / rel)
    if m["line"] not in mt._EXECUTABLE[rel]:
        return False
    return m["line"] not in set(reach["hits"].get(rel, ()))


def drive(t: Path, m: dict, base: dict, full: bool, nostop: bool = False) -> dict:
    path = t / m["file"]
    original = path.read_text()
    lines = original.splitlines(True)
    assert lines[m["line"] - 1].rstrip("\n") == m["old"], (m, lines[m["line"] - 1])
    lines[m["line"] - 1] = m["new"] + "\n"
    ds = [s for s in order(base, list(base)) if m["file"] in
          mt.load_closures().get(s, ()) and (not ONLY or s in ONLY)]
    out = {"mutant": m, "runs": {}, "skipped": [], "killed_by": [],
           "started": time.time()}
    try:
        path.write_text("".join(lines))
        for s in ds:
            if not full and not fast(s):
                out.setdefault("deferred_slow", []).append(s)
                continue
            if mt.reach_skip(base[s]["reach"], m):
                out["skipped"].append(s)
                continue
            if relaxed_skip(base[s].get("capture_reach") or base[s]["reach"], m):
                out.setdefault("relaxed_skipped", []).append(s)
                continue
            a, e = spec(s)
            run = run_any(s, t, timeout_for(s, base), a, e)
            k = killed_any(s, run, from_json(base[s]["run"]))
            j = to_json(run)
            j["killed"] = k
            out["runs"][s] = j
            if k:
                out["killed_by"].append(s)
                if not (full or nostop):
                    break
    finally:
        path.write_text(original)
    out["wall"] = round(time.time() - out["started"], 1)
    out["verdict"] = "KILLED" if out["killed_by"] else (
        "TIMEOUT" if any(r["timed_out"] for r in out["runs"].values())
        else "SURVIVED")
    return out


def cmd_run(args) -> int:
    base = load_base()
    RESULTS.mkdir(parents=True, exist_ok=True)
    pool = unpinned()
    if args.anchors:
        want = [ln.strip() for ln in Path(args.anchors).read_text().splitlines()
                if ln.strip()]
        byk = {}
        for m in pool + pinned():
            byk.setdefault(m["anchor"], m)
            byk.setdefault(key(m), m)
        pool = [byk[w] for w in want if w in byk]
    elif args.mutants:
        pool = json.loads(Path(args.mutants).read_text())
    else:
        pool = weighted(pool)
    sub = args.sub or ("full" if args.full else "pre")
    done = {p.stem for p in (RESULTS / sub).glob("*.json")} if (RESULTS / sub).exists() else set()
    (RESULTS / sub).mkdir(parents=True, exist_ok=True)
    pool = [m for m in pool if key(m) not in done]
    if args.limit:
        pool = pool[: args.limit]
    stop = STATE / "STOP"
    q: "queue.Queue[dict]" = queue.Queue()
    for m in pool:
        q.put(m)
    log(f"RUN {sub} queued={len(pool)} workers={args.workers}")

    def work(i):
        t = tree(i + args.tree_offset)
        while not stop.exists():
            try:
                m = q.get_nowait()
            except queue.Empty:
                return
            r = drive(t, m, base, args.full)
            (RESULTS / sub / (key(m) + ".json")).write_text(json.dumps(r))
            if FRESH:
                t = recycle(i + args.tree_offset)
            log(f"{sub.upper()} {r['verdict']} {m['anchor']} L{m['line']} "
                f"by={','.join(r['killed_by']) or '-'} ran={len(r['runs'])} "
                f"skip={len(r['skipped'])} wall={r['wall']}s")
    ths = [threading.Thread(target=work, args=(i,)) for i in range(args.workers)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    return 0


def weighted(pool: list[dict]) -> list[dict]:
    """Consequence weighting (D3.M1): kind rank, round-robin over files."""
    per: dict[str, list[dict]] = {}
    for m in sorted(pool, key=lambda m: (KIND_RANK.get(m["kind"], 9), m["line"])):
        per.setdefault(m["file"], []).append(m)
    out = []
    while any(per.values()):
        for f in sorted(per):
            if per[f]:
                out.append(per[f].pop(0))
    return out


def cmd_complete(args) -> int:
    """D3.M3's full net for pre-screen survivors: re-drive each survivor of
    results/<--from>/ (or the keys in --keys) through every driver the fast
    drive deferred or skipped by the relaxed reach (no relaxation, no early
    stop), and write the merged verdict to results/complete/."""
    global RELAX
    RELAX = False
    base = load_base()
    src = RESULTS / args.src
    want = None
    if args.keys:
        want = [k.strip() for k in Path(args.keys).read_text().split() if k.strip()]
    rs = []
    for p in sorted(src.glob("*.json")):
        r = json.loads(p.read_text())
        if want is not None and p.stem not in want:
            continue
        if want is None and r["verdict"] != "SURVIVED":
            continue
        rs.append((p.stem, r))
    if want:
        rs.sort(key=lambda kr: want.index(kr[0]))
    out_dir = RESULTS / "complete"
    out_dir.mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in out_dir.glob("*.json")}
    q: "queue.Queue" = queue.Queue()
    for k, r in rs:
        if k not in done:
            q.put((k, r))
    log(f"COMPLETE queued={q.qsize()} from={args.src}")

    def work(i):
        t = tree(i + args.tree_offset)
        while not (STATE / "STOP").exists():
            try:
                k, r = q.get_nowait()
            except queue.Empty:
                return
            m = r["mutant"]
            extra = (r.get("deferred_slow", []) + r.get("relaxed_skipped", []))
            path = t / m["file"]
            original = path.read_text()
            lines = original.splitlines(True)
            assert lines[m["line"] - 1].rstrip("\n") == m["old"]
            lines[m["line"] - 1] = m["new"] + "\n"
            t0 = time.time()
            try:
                path.write_text("".join(lines))
                for s in order(base, extra):
                    if mt.reach_skip(base[s]["reach"], m):
                        r["skipped"].append(s)
                        continue
                    a, e = spec(s)
                    run = mt.run_script(s, t, timeout_for(s, base), a, e)
                    j = to_json(run)
                    j["killed"] = mt.killed(s, run, from_json(base[s]["run"]))
                    r["runs"][s] = j
                    if j["killed"]:
                        r["killed_by"].append(s)
            finally:
                path.write_text(original)
            r["complete_wall"] = round(time.time() - t0, 1)
            r["completed"] = True
            r.pop("deferred_slow", None)
            r.pop("relaxed_skipped", None)
            r["verdict"] = "KILLED" if r["killed_by"] else (
                "TIMEOUT" if any(x["timed_out"] for x in r["runs"].values())
                else "SURVIVED")
            (out_dir / (k + ".json")).write_text(json.dumps(r))
            log(f"COMPLETE {r['verdict']} {m['anchor']} L{m['line']} "
                f"by={','.join(r['killed_by']) or '-'} ran={len(r['runs'])} "
                f"wall={r['complete_wall']}s")
    ths = [threading.Thread(target=work, args=(i,)) for i in range(args.workers)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    return 0


def cmd_null(args) -> int:
    base = load_base()
    null = mt.null_for([{"file": r} for r in RELS])
    t = tree(4)
    r = drive(t, null, base, args.full, nostop=True)
    (STATE / ("null-full.json" if args.full else "null.json")).write_text(json.dumps(r))
    print(f"RESULT null_verdict={'LIVES' if not r['killed_by'] else 'KILLED:' + ','.join(r['killed_by'])}")
    print(f"RESULT null_drivers_run={len(r['runs'])}")
    return 0


def classify(base: dict, s: str, m: dict) -> str:
    """exec | noexec | reader | unknown for driver s on mutant m's line."""
    reach = base[s].get("capture_reach") or base[s]["reach"]
    rel, line = m["file"], m["line"]
    if rel not in mt._EXECUTABLE:
        mt._EXECUTABLE[rel] = mt.executable_lines(mt.ROOT / rel)
    if line not in mt._EXECUTABLE[rel]:
        return "unknown"
    if mt.reach_skip(base[s]["reach"], m) or relaxed_skip(reach, m):
        return "noexec"
    if reach is None:
        return "unknown"
    if line in set(reach["hits"].get(rel, ())):
        return "exec"
    if rel in reach["reads"]:
        return "reader"
    return "unknown"


def cmd_reach(args) -> int:
    """Whole-universe reach (D3.M1 weighting): for each unpinned site, which
    drivers of its closure execute its line in their unmutated run. Writes
    state/reach.tsv; prints per-file counts of sites NO driver executes and no
    driver's reach is unknown for (`dead_to_gate`): only a text reader
    (structure/archscore/doc lints) can see such a mutant at all."""
    from collections import Counter
    base = load_base()
    rows = []
    for m in unpinned():
        ds = [s for s in base if m["file"] in mt.load_closures().get(s, ())]
        cls = {s: classify(base, s, m) for s in ds}
        rows.append((m, cls))
    dead, unk = Counter(), Counter()
    with open(STATE / "reach.tsv", "w") as f:
        for m, cls in rows:
            ex = sorted(s for s, c in cls.items() if c == "exec")
            un = sorted(s for s, c in cls.items() if c == "unknown")
            f.write(f"{m['anchor']}\t{m['line']}\t{m['kind']}\t"
                    f"exec={','.join(ex)}\tunknown={','.join(un)}\n")
            fn = m["file"].rsplit("/", 1)[-1]
            if not ex and not un:
                dead[fn] += 1
            elif not ex:
                unk[fn] += 1
    for fn in sorted(set(dead) | set(unk)):
        print(f"  {fn}: dead_to_gate={dead[fn]} only_unknown_reach={unk[fn]}")
    print(f"RESULT unpinned_sites={len(rows)}")
    print(f"RESULT dead_to_gate={sum(dead.values())}")
    print(f"RESULT only_unknown_reach={sum(unk.values())}")
    return 0


def cmd_report(args) -> int:
    from collections import Counter
    for sub in ("pre", "full", "c2", "c3c6", "complete"):
        d = RESULTS / sub
        if not d.exists():
            continue
        rs = [json.loads(p.read_text()) for p in d.glob("*.json")]
        c = Counter(r["verdict"] for r in rs)
        print(f"RESULT {sub}_mutants={len(rs)}")
        for v, n in sorted(c.items()):
            print(f"RESULT {sub}_{v.lower()}={n}")
        kb = Counter(r["killed_by"][0] for r in rs if r["killed_by"])
        for s, n in kb.most_common():
            print(f"  first-kill {s}: {n}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("baseline", "run", "null", "reach", "report", "retrace", "trace-capture", "complete"))
    ap.add_argument("--src", default="pre")
    ap.add_argument("--keys")
    ap.add_argument("--script")
    ap.add_argument("--mutants", help="JSON list of mutant dicts to drive")
    ap.add_argument("--sub", help="results subdirectory name")
    ap.add_argument("--tree-offset", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--anchors")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    STATE.mkdir(parents=True, exist_ok=True)
    rc = {"baseline": cmd_baseline, "run": cmd_run, "null": cmd_null,
          "reach": cmd_reach, "report": cmd_report, "retrace": cmd_retrace, "trace-capture": cmd_trace_capture, "complete": cmd_complete}[args.cmd](args)
    ld = os.getloadavg()[0]
    print(f"RESULT load1={ld:.2f}")
    print("RESULT thread_factor=1.00")
    return rc


if __name__ == "__main__":
    sys.exit(main())
