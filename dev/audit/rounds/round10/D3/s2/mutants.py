#!/usr/bin/env python3
"""D3-s2 mutation pre-screen (round 10, D3.M1-M3).

Metric: per mutant, the first gate script (of the mutated file's measured
closure in tests/closures.json, fast scripts first) that exits non-zero; a
mutant no script kills is a survivor.  Count key: the exit code each real
gate script returns with the mutated production file on disk.

Command (from the worktree root, an ISOLATED worktree -- it edits production
on disk and restores it with `git checkout -- <file>` after each mutant):
    PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python \
        dev/audit/rounds/round10/D3/s2/mutants.py list            # M1: sample
    ... mutants.py run [ID ...] [--scripts a,b,c]                   # M2: screen
Expected: `list` is deterministic for SEED=10 (exact); `run` results exact
(exit codes) modulo timeouts.  Baseline 17f1c55fad1b, machine: tvofi macOS
arm64 (8 cores, shared box B2).

Perturbation: re-run a survivor with the script that *should* kill it after
adding the assertion named in REPORT.md; the survivor count drops by one.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, json, random, re, subprocess, sys, time

ROOT = os.getcwd()
PKG = "custom_components/heatpump_optimizer/"
MODULES = ["sensor", "binary_sensor", "climate", "switch", "button", "entity",
           "store", "ledger", "snapshots", "payload", "inputs", "topology",
           "entry_config", "diagnostics", "accuracy", "services", "const",
           "__init__"]
SEED = 10
N = 36
PER_MODULE = 4
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MUT_OUT") or os.path.join(HERE, "results.json")
# Consequence weights (M1): user-facing published values, persistence and
# services weigh most; constants/entity plumbing least.
WEIGHTS = {"sensor": 3, "binary_sensor": 2, "climate": 3, "switch": 2,
           "button": 1, "entity": 1, "store": 3, "ledger": 3, "snapshots": 2,
           "payload": 3, "inputs": 3, "topology": 2, "entry_config": 3,
           "diagnostics": 1, "accuracy": 2, "services": 3, "const": 1,
           "__init__": 2}
# fast-first; stress/edge/backtest skipped by the brief; arch/doc/structure
# scripts measure shape, not behaviour, and are skipped as well.
ORDER = ["guard_pins.py", "block_duty.py", "debug_collect.py",
         "wood_advisor.py", "solar_alignment.py", "manual_plan.py",
         "config_flow_steps.py", "plan_view.py", "validate.py",
         "entities.py", "finite_boundary.py", "optimality.py",
         "features.py"]
SKIP = {"stress.py", "edge.py", "backtest.py", "boost_drift_replay.py",
        "arch_score_head.py", "harness_headers.py", "structure.py",
        "doc_claims.py", "typing_ruler.py", "deployment_shape.py",
        "env_drift.py", "card.mjs", "card_drift.mjs"}


def candidates(mod):
    path = PKG + mod + ".py"
    src = open(path).read().splitlines()
    tree = ast.parse("\n".join(src))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            ln = node.lineno
            line = src[ln - 1]
            if re.match(r"\s*(el)?if .*:\s*(#.*)?$", line) and node.test.end_lineno == ln:
                cond = ast.get_source_segment("\n".join(src), node.test)
                kw = "elif" if line.lstrip().startswith("elif") else "if"
                ind = line[: len(line) - len(line.lstrip())]
                out.append((path, ln, "negate-guard", line,
                            f"{ind}{kw} not ({cond}):"))
        elif isinstance(node, ast.Compare) and node.lineno == node.end_lineno:
            line = src[node.lineno - 1]
            for a, b in ((">=", ">"), ("<=", "<"), (" > ", " >= "), (" < ", " <= ")):
                if line.count(a) == 1:
                    out.append((path, node.lineno, f"boundary {a.strip()}->{b.strip()}",
                                line, line.replace(a, b)))
                    break
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in ("min", "max") and node.lineno == node.end_lineno:
            line = src[node.lineno - 1]
            f = node.func.id
            g = "max" if f == "min" else "min"
            if line.count(f + "(") == 1:
                out.append((path, node.lineno, f"{f}->{g}", line,
                            line.replace(f + "(", g + "(")))
    # dedupe by line
    seen, res = set(), []
    for c in sorted(out, key=lambda c: (c[1], c[2])):
        if c[1] in seen:
            continue
        seen.add(c[1])
        res.append(c)
    return res


def sample():
    rng = random.Random(SEED)
    pool = {m: candidates(m) for m in MODULES}
    chosen, count = [], {m: 0 for m in MODULES}
    mods = [m for m in MODULES if pool[m]]
    w = [WEIGHTS[m] for m in mods]
    tries = 0
    while len(chosen) < N and tries < 10000:
        tries += 1
        m = rng.choices(mods, weights=w)[0]
        if count[m] >= PER_MODULE or not pool[m]:
            continue
        c = pool[m].pop(rng.randrange(len(pool[m])))
        # syntax check of the mutated module
        p, ln, op, old, new = c
        src = open(p).read().splitlines()
        src[ln - 1] = new
        try:
            compile("\n".join(src), p, "exec")
        except SyntaxError:
            continue
        count[m] += 1
        chosen.append({"id": f"M{len(chosen)+1:02d}", "file": p, "line": ln,
                       "op": op, "old": old.strip(), "new": new.strip()})
    return chosen, {m: len(candidates(m)) for m in MODULES}


def closure_of(path):
    c = json.load(open("tests/closures.json"))["closures"]
    hit = [os.path.basename(s) for s in c if path in c[s]]
    return [s for s in ORDER if s in hit], hit


def apply(m):
    src = open(m["file"]).read().split("\n")
    assert src[m["line"] - 1].strip() == m["old"], m
    ind = src[m["line"] - 1][: len(src[m["line"] - 1]) - len(src[m["line"] - 1].lstrip())]
    src[m["line"] - 1] = ind + m["new"]
    open(m["file"], "w").write("\n".join(src))


def restore(m):
    subprocess.run(["git", "checkout", "--", m["file"]], check=True)


def run(ids, scripts=None, timeout=1500):
    muts, _ = sample()
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    py = sys.executable
    for m in muts:
        if ids and m["id"] not in ids:
            continue
        order, hit = closure_of(m["file"])
        if scripts:
            order = [s for s in scripts if s in hit]
        rec = res.get(m["id"], {"mutant": m, "ran": {}})
        rec["mutant"] = m
        rec["closure"] = hit
        apply(m)
        try:
            for s in order:
                prev = rec["ran"].get(s)
                if prev and isinstance(prev["rc"], int) and prev["rc"] > 0:
                    break
                if prev and prev["rc"] == 0:
                    continue
                t = time.time()
                try:
                    p = subprocess.run([py, "tests/" + s], capture_output=True,
                                       text=True, timeout=timeout,
                                       env=dict(os.environ, GOLDEN_MODE="strict"))
                    rc = p.returncode
                    fails = [l.strip() for l in p.stdout.splitlines()
                             if l.strip().startswith("FAIL ") or " FAILED" in l]
                    tail = "\n".join(fails[:12]) or (p.stdout + p.stderr)[-600:]
                except subprocess.TimeoutExpired:
                    rc, tail = "timeout", ""
                rec["ran"][s] = {"rc": rc, "wall": round(time.time() - t, 1),
                                 "tail": tail if rc != 0 else ""}
                print(m["id"], s, rc, flush=True)
                res[m["id"]] = rec
                json.dump(res, open(OUT, "w"), indent=1)
                if isinstance(rc, int) and rc > 0:
                    break
        finally:
            restore(m)
        killed = [s for s, v in rec["ran"].items() if isinstance(v["rc"], int) and v["rc"] > 0]
        rec["killed_by"] = killed[0] if killed else None
        res[m["id"]] = rec
        json.dump(res, open(OUT, "w"), indent=1)
    surv = [k for k, v in res.items() if not v.get("killed_by")]
    print(f"RESULT screened={len(res)} count")
    print(f"RESULT survivors={len(surv)} count  {' '.join(sorted(surv))}")
    print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    if sys.argv[1] == "list":
        ch, pools = sample()
        print("pool sizes:", json.dumps(pools))
        for m in ch:
            print(f'{m["id"]} {m["file"].split("/")[-1]}:{m["line"]} [{m["op"]}] {m["old"]}  =>  {m["new"]}')
        print(f"RESULT sampled={len(ch)} count")
    elif sys.argv[1] == "run":
        a = sys.argv[2:]
        sc = None
        if "--scripts" in a:
            i = a.index("--scripts"); sc = a[i + 1].split(","); a = a[:i] + a[i + 2:]
        run(a, sc)
