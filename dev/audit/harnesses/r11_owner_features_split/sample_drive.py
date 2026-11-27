"""C2 sample-and-report: drive a seeded sample of rule-1 and rule-2 ledger rows per part.

    cd <base tree>; PYTHONPATH=tests/hastub:tests python3 sample_drive.py LINES.json OUT.jsonl [--n 200] [--seed 11] [--workers 4]

Reach and plans are linereach.py's (the spike, at the design note's commit): a row's
reaching spans are the spans whose recorded LINE events hold a line equal to the row's
`old` (module-level line: every span whose recorded `files` hold the module); a part's
drive plan is its reaching spans plus their in-part `needs` closure. A part is driven by
`case_select run tests/features.py --plan <plan>` on a per-worker copy of the tree with the
mutant written in place; the drive stops at the first `FAIL` line (fail-fast). A drive that
printed a FAIL is a kill only if the same plan's unmutated run prints fewer FAILs
(mutation_table.killed's rule); that baseline is run only for plans that printed a FAIL,
cached by plan. Rule 1: drive the one part. Rule 2: drive reaching parts cheapest first by
recorded cost, stop at the first kill. CPU-s is the child's ru_utime+ru_stime by wait4.
"""
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import threading
import queue
from pathlib import Path

ROOT = Path.cwd()
SPIKE = Path(os.environ["SPIKE"])
sys.path[:0] = [str(ROOT / "tests"), str(SPIKE)]
import case_select as cs  # noqa: E402
import mutation_table as mt  # noqa: E402
import swap_run  # noqa: E402
import linereach  # noqa: E402


def rows_with_reach(lines_path):
    parts = swap_run.partition()
    rec = json.load(open(lines_path))
    lines = {sid: {tuple(x) for x in v} for sid, v in rec["lines"].items()}
    by_line = {}
    for sid, v in lines.items():
        for x in v:
            by_line.setdefault(x, set()).add(sid)
    e = cs.entry(cs.load(), "tests/features.py")
    spans = e["spans"]
    sec = {sid: spans.get(sid, {}).get("seconds", 0.0) for sid in parts}
    needs = {sid: set(spans.get(sid, {}).get("needs", [])) for sid in parts}
    files_of = {sid: {os.path.basename(f) for f in spans.get(sid, {}).get("files", [])} for sid in parts}
    out = []
    srcc, flc = {}, {}
    for p in sorted(Path("tests/mutation_ledger/killed_by").rglob("*.json")):
        row = json.load(open(p))
        if row.get("killed_by") != "tests/features.py":
            continue
        f = row["anchor"].split(":")[0]
        base = os.path.basename(f)
        if f not in srcc:
            srcc[f] = open(f, encoding="utf-8").read().split("\n")
            flc[f] = linereach._func_lines(f)
        cand = [i + 1 for i, t in enumerate(srcc[f]) if t.rstrip("\n") == row["old"]]
        reach = set()
        for ln in cand:
            if ln in flc[f]:
                reach |= by_line.get((base, ln), set())
            else:
                reach |= {sid for sid in parts if base in files_of[sid]}

        def plan_of(x):
            # X's reaching spans plus their whole needs closure: a needed span of another
            # part stands for the binding or seed the split copies into X's header.
            plan, todo = set(), [s for s in reach if parts.get(s) == x]
            while todo:
                s = todo.pop()
                if s in plan:
                    continue
                plan.add(s)
                todo += list(needs.get(s, ()))
            return sorted(plan), sum(sec.get(s, 0.0) for s in plan)

        rparts = sorted({parts[s] for s in reach if s in parts})
        drives = sorted((plan_of(x)[1], x, plan_of(x)[0]) for x in rparts)
        out.append({"row": str(p), "anchor": row["anchor"], "rule": min(len(rparts), 2), "drives": drives})
    global PARTS
    PARTS = parts
    return out


_mut_cache = {}


def mutant_text(anchor):
    f = anchor.split(":")[0]
    if f not in _mut_cache:
        src = (ROOT / f).read_text()
        muts = mt.anchor_sites(src, list(mt.candidates(ROOT / f, mt.RATCHETED, src)))
        _mut_cache[f] = (src, {m["anchor"]: m for m in muts})
    src, by = _mut_cache[f]
    m = by.get(anchor)
    if m is None:
        return f, None
    lines = src.splitlines(True)
    lines[m["line"] - 1] = m["new"] + "\n"
    return f, "".join(lines)


PARTS = {}
RUNNER = str(Path(__file__).resolve().with_name("span_runner.py"))


def run_plan(tree, plan, part, failfast=True):
    """Fails inside part `part`'s spans, attributed by @@SPAN; stops at the first one."""
    pf = tree / ".plan"
    pf.write_text("\n".join(plan) + "\n")
    env = dict(os.environ, PYTHONPATH="tests/hastub:tests", PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen([sys.executable, RUNNER, str(pf)],
                         cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    fails, other, first, cur, scoped = 0, 0, None, "header", False
    for ln in p.stdout:
        if ln.startswith("@@SPAN "):
            cur = ln[7:].rstrip("\n")
            continue
        if ln.startswith("CASES: SCOPED"):
            scoped = True
        if not ln.lstrip().startswith("FAIL "):
            continue
        if PARTS.get(cur) == part or cur == "header":
            fails += 1
            first = first or f"{cur} :: {ln.strip()}"
            if failfast:
                p.kill()
                break
        else:
            other += 1
    p.stdout.close()
    _, status, ru = os.wait4(p.pid, 0)
    if not first and not scoped and os.waitstatus_to_exitcode(status) not in (0, -9):
        # an uncaught exception ended the run inside span `cur`: one failing check (failing_count)
        if PARTS.get(cur) == part or cur == "header":
            fails += 1
            first = f"{cur} :: uncaught exception"
        else:
            other += 1
    return fails, other, first, ru.ru_utime + ru.ru_stime, scoped
def main():
    a = sys.argv[1:]
    lines_path, out_path = a[0], a[1]
    n = int(a[a.index("--n") + 1]) if "--n" in a else 200
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 11
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 4
    rows = rows_with_reach(lines_path)
    pool = [r for r in rows if r["rule"] in (1, 2)]
    from collections import Counter
    print("rows", len(rows), "by rule", dict(Counter(r["rule"] for r in rows)), flush=True)
    sample = random.Random(seed).sample(pool, n)
    print("sample", n, "by rule", dict(Counter(r["rule"] for r in sample)), flush=True)
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["anchor"] for l in open(out_path)}
    trees = []
    for w in range(workers):
        t = Path(os.environ.get("TREES", "/root/trees")) / f"w{w}"
        if not t.exists():
            shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git"), symlinks=True)
        # an aborted run leaves its in-flight mutant behind: rewrite every production file
        # from the base, then refuse unless each tree's production source equals the base's
        for src in (ROOT / "custom_components").rglob("*.py"):
            (t / src.relative_to(ROOT)).write_bytes(src.read_bytes())
        bad = [str(q.relative_to(t)) for q in (t / "custom_components").rglob("*.py")
               if not (ROOT / q.relative_to(t)).exists() or q.read_bytes() != (ROOT / q.relative_to(t)).read_bytes()]
        if bad:
            sys.exit(f"REFUSE tree {t}: production source differs from the base: {bad[:5]}")
        trees.append(t)
    base_cache, lock = {}, threading.Lock()
    q = queue.Queue()
    for r in sample:
        if r["anchor"] not in done:
            q.put(r)
    outf = open(out_path, "a")

    def baseline(tree, plan, part):
        k = hashlib.sha1((part + "\n" + "\n".join(plan)).encode()).hexdigest()
        with lock:
            if k in base_cache:
                return base_cache[k]
        fails, other, first, cpu, _ = run_plan(tree, plan, part, failfast=False)
        with lock:
            base_cache[k] = (fails, other, cpu)
        return fails, other, cpu

    def worker(w):
        tree = trees[w]
        while True:
            try:
                r = q.get_nowait()
            except queue.Empty:
                return
            f, text = mutant_text(r["anchor"])
            res = {"anchor": r["anchor"], "rule": r["rule"], "drives": []}
            if text is None:
                res["error"] = "no mutant regenerated at this tree"
            else:
                path = tree / f
                orig = path.read_text()
                try:
                    for est, part, plan in r["drives"]:
                        path.write_text(text)
                        fails, other, first, cpu, scoped = run_plan(tree, plan, part)
                        path.write_text(orig)
                        killed = False
                        bcpu, bf, bo = 0.0, None, None
                        if fails and os.environ.get("NO_BASELINE"):
                            killed = True  # baseline false-kill rate measured separately (baselines.py)
                        elif fails:
                            bf, bo, bcpu = baseline(tree, plan, part)
                            if bf:
                                path.write_text(text)
                                fails, other, first, cpu2, scoped = run_plan(tree, plan, part, failfast=False)
                                path.write_text(orig)
                                cpu += cpu2
                                killed = fails > bf
                            else:
                                killed = True
                        res["drives"].append({"part": part, "spans": len(plan), "est_s": round(est, 1),
                                              "cpu_s": round(cpu, 1), "baseline_cpu_s": round(bcpu, 1),
                                              "killed": killed, "first": first, "other_part_events": other,
                                              "completed": scoped, "baseline_fails": bf})
                        if killed:
                            break
                finally:
                    path.write_text(orig)
            res["killed"] = any(d["killed"] for d in res["drives"])
            with lock:
                outf.write(json.dumps(res) + "\n")
                outf.flush()
                print(f"{r['rule']} killed={res['killed']} cpu={sum(d['cpu_s'] for d in res['drives']):.0f} {r['anchor']}", flush=True)

    ths = [threading.Thread(target=worker, args=(w,)) for w in range(workers)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    print("@@DONE", flush=True)


if __name__ == "__main__":
    main()
