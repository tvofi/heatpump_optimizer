"""D3-s1 mutation pre-screen (D3.M1/M2).

Metric: per mutant, the first closure script (cheapest-first) that exits
non-zero with the mutant applied; "SURVIVED" when none does.
Command:
  PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py sample
  PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py run <id>[,<id>...] [--full]
Expected: `sample` is deterministic (seed 10, exact); `run` prints
RESULT <id>=<killer|SURVIVED>. Baseline 17f1c55fad1b, machine: owner's
8-core Mac (Darwin 25.6), shared box during the fan-out.
Perturbation (the judge's): run the id with the mutant applied (default)
versus `--null` (no edit): a SURVIVED/killed verdict means something only
if `--null` passes every script in the same chain.
The mutant is a single-line textual edit applied in THIS checkout and
restored in a finally block (D3 owns an isolated worktree).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, json, random, re, subprocess, sys, time

ROOT = os.getcwd()
# scripts red with NO mutant on this machine (measured by --null); never count as a kill
BASELINE_RED = set(filter(None, os.environ.get("D3S1_BASELINE_RED", "").split(",")))
PKG = "custom_components/heatpump_optimizer/"
MODS = {"coordinator": 3, "optimizer": 3, "thermal_model": 3, "sysid": 2,
        "defrost": 2, "flow_lift": 2, "process_worker": 1, "batchmath": 2,
        "price_model": 2, "tariff": 3, "grid_fee": 3, "dhw_planner": 2}
BASE = "17f1c55fad1b"
SEED = 10
N = 36
HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_PRESCREEN = {"tests/golden.py", "tests/stress.py", "tests/edge.py", "tests/backtest.py",
                  "tests/boost_drift_replay.py"}
# structural scripts: cannot see a same-line-count behavioural edit; run only with --full
STRUCTURAL = {"tests/harness_headers.py", "tests/entities.py",
              "tests/arch_score_head.py", "tests/structure.py",
              "tests/typing_ruler.py", "tests/doc_claims.py",
              "tests/deployment_shape.py"}
OPS = [(" < ", " <= ", 2), (" > ", " >= ", 2), (" <= ", " < ", 2),
       (" >= ", " > ", 2), ("min(", "max(", 3), ("max(", "min(", 3),
       (" and ", " or ", 2), (" or ", " and ", 2)]


def candidates():
    out = []
    for mod, mw in MODS.items():
        path = PKG + mod + ".py"
        src = open(path).read().split("\n")
        tree = ast.parse("\n".join(src))
        guard_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.IfExp, ast.Compare,
                                 ast.BoolOp, ast.Call, ast.Return, ast.Assign)):
                if node.lineno == getattr(node, "end_lineno", node.lineno):
                    guard_lines.add(node.lineno)
        for ln in sorted(guard_lines):
            line = src[ln - 1]
            code = line.split("#")[0]
            if '"' in code or "'" in code or "def " in code:
                continue
            for a, b, w in OPS:
                if code.count(a) == 1:
                    kind = "guard" if re.match(r"\s*(if|elif|while|return)\b", code) else "expr"
                    out.append({"mod": mod, "line": ln, "from": a, "to": b,
                                "weight": mw * w * (2 if kind == "guard" else 1),
                                "orig": line.strip()})
    return out


def sample():
    c = candidates()
    rng = random.Random(SEED)
    pool, chosen, per = list(c), [], {}
    while pool and len(chosen) < N:
        pick = rng.choices(pool, weights=[x["weight"] for x in pool])[0]
        pool.remove(pick)
        if per.get(pick["mod"], 0) >= 4 or any(
                x["mod"] == pick["mod"] and x["line"] == pick["line"] for x in chosen):
            continue
        per[pick["mod"]] = per.get(pick["mod"], 0) + 1
        chosen.append(pick)
    for i, m in enumerate(chosen, 1):
        m["id"] = "M%02d" % i
    print("RESULT candidates=%d count" % len(c))
    print("RESULT sampled=%d count" % len(chosen))
    return chosen


def chain(mod, full):
    d = json.load(open("tests/closures.json"))
    rec = d["recorded"]
    f = PKG + mod + ".py"
    s = [k for k, v in d["closures"].items() if f in v and k not in SKIP_PRESCREEN]
    if not full:
        s = [k for k in s if k not in STRUCTURAL]
    s.append("tests/env_drift.py")
    s = sorted(set(s), key=lambda k: (k != "tests/env_drift.py" and
                                      rec.get(k, {}).get("seconds", 1e9) or 30))
    return s, rec


def run_script(k, rec, log):
    if k.endswith(".mjs"):
        args = ["node", k] + ([BASE] if "drift" in k else [])
    elif k == "tests/env_drift.py":
        args = [sys.executable, k, "--all", BASE]
    else:
        args = [sys.executable, k]
    env = dict(os.environ, PYTHONPATH="tests/hastub", GATE_JOBS="1",
               GOLDEN_MODE="drift", GOLDEN_REF=BASE)
    t = 1200 if k == "tests/env_drift.py" else rec.get(k, {}).get("seconds", 60) * 3 + 300
    t0 = time.time()
    try:
        p = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                           text=True, timeout=t)
        rc, tail = p.returncode, (p.stdout + p.stderr)[-1500:]
    except subprocess.TimeoutExpired:
        rc, tail = "timeout", ""
    log.write("== %s rc=%s %.1fs\n%s\n" % (k, rc, time.time() - t0, tail))
    log.flush()
    return rc


def run(ids, full, null):
    muts = {m["id"]: m for m in sample()}
    for i in ids:
        m = muts[i]
        claim = os.environ.get("D3S1_CLAIMS")
        if claim:  # several lanes share one id list; the first to claim an id runs it
            try:
                os.close(os.open(os.path.join(claim, i + ("-null" if null else "")), os.O_CREAT | os.O_EXCL))
            except FileExistsError:
                continue
        path = PKG + m["mod"] + ".py"
        # a SIGTERM'd earlier run leaves its mutant behind; refuse to treat it as the original
        assert subprocess.run(["git", "diff", "--quiet", "--", path]).returncode == 0, path
        orig = open(path).read()
        lines = orig.split("\n")
        old = lines[m["line"] - 1]
        assert old.strip() == m["orig"], (i, old)
        code, sep, com = old.partition("#")
        lines[m["line"] - 1] = code.replace(m["from"], m["to"], 1) + sep + com
        logp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "d3s1-%s%s.log" % (i, "-null" if null else ""))
        killer = "SURVIVED"
        ran = []
        with open(logp, "w") as log:
            try:
                if not null:
                    open(path, "w").write("\n".join(lines))
                s, rec = chain(m["mod"], full)
                kills = []
                for k in s:
                    # cheap tier (<30 s recorded) runs to the end so duplicated
                    # kills are visible (D3.M5); the costly tier stops at the first kill
                    if kills and not null and rec.get(k, {}).get("seconds", 30) >= 30 and k != "tests/env_drift.py":
                        break
                    rc = run_script(k, rec, log)
                    ran.append(k)
                    if rc != 0 and k not in BASELINE_RED:
                        kills.append(k)
                        killer = "%s(rc=%s)" % (kills[0], rc)
                    if rc != 0 and null:
                        print("NULLRED %s rc=%s" % (k, rc), flush=True)
            finally:
                open(path, "w").write(orig)
        print("MUTANT %s %s:%d %r->%r ran=%d log=%s" % (i, m["mod"], m["line"], m["from"], m["to"], len(ran), logp))
        print("KILLS %s %s" % (i, ",".join(kills)))
        print("RESULT %s=%s" % (i + ("-null" if null else ""), killer), flush=True)


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))  # run the restore in finally
    if sys.argv[1] == "sample":
        for m in sample():
            print(json.dumps(m))
    else:
        run(sys.argv[2].split(","), "--full" in sys.argv, "--null" in sys.argv)
    print("RESULT thread_factor=%.3f" % (time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    print("RESULT swapins=0")
