#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s2-01.

METRIC (one line): over EVERY capped policy file at zero line headroom (lines == cap
  per `policy_lint.mjs --budgets`, derived at run time, not carried), how many accept
  +400 bytes of new prose appended to their last non-empty line with NO new error of
  ANY check class in a default `policy_lint.mjs` run (errors naming tools/audit/round9/
  evidence files are the null run's own and are diffed out); plus the bound: the
  smallest appended size, on CLAUDE.md and on one non-always-loaded rule, at which
  any error appears (the aggregate band is the only thing left to stop it).
KEY: the set of ERROR lines policy_lint itself prints, diffed against the null run.
CONTROL: the same 400 bytes as 6 new lines on each file -> must add an error.
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_caps_bytes.py
EXPECTED (baseline 1936d5ca): printed; exact counts.
Works in a `git archive HEAD` copy under tempfile.mkdtemp(); never edits the tree.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import random, re, shutil, subprocess, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
NODE = shutil.which("node") or "/opt/node22/bin/node"
LINT = ".claude/workflows/policy_lint.mjs"


def run(d):
    env = dict(os.environ, HPO_PLANDATA=os.path.join(d, ".plandata"))
    p = subprocess.run([NODE, LINT], cwd=d, capture_output=True, text=True, env=env)
    return {l.strip() for l in (p.stdout + p.stderr).splitlines()
            if "ERROR" in l and "tools/audit/round9/" not in l}


def prose(n, seed):
    rng = random.Random(seed)
    w = []
    while len(" ".join(w)) < n:
        w.append("".join(rng.choice("bcdfghjklmnprstvw") for _ in range(rng.randint(4, 9))))
    return " ".join(w)[:n]


def grow(path, n, mode, seed):
    raw = open(path, encoding="utf-8").read()
    add = prose(n, seed)
    if mode == "joined":
        lines = raw.split("\n")
        i = max(k for k, l in enumerate(lines) if l.strip())
        lines[i] += " " + add
        new = "\n".join(lines)
    else:
        step = -(-n // 6)
        new = raw + ("" if raw.endswith("\n") else "\n") + "\n".join(add[j:j + step] for j in range(0, n, step)) + "\n"
    open(path, "w", encoding="utf-8").write(new)
    return raw


def main():
    d = tempfile.mkdtemp(prefix="d11v2-caps-")
    subprocess.run(f"git archive HEAD | tar -x -C {d}", shell=True, check=True)
    subprocess.run(["git", "init", "-q"], cwd=d)
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)  # policy_lint enumerates tracked files
    env = dict(os.environ, HPO_PLANDATA=os.path.join(d, ".plandata"))
    bud = subprocess.run([NODE, LINT, "--budgets"], cwd=d, capture_output=True, text=True, env=env).stdout
    zero = []
    for l in bud.splitlines():
        m = re.match(r"^(\S+)\s+(\d+)\s+(\d+)\s+\d+", l)
        if m and m.group(2) == m.group(3):
            zero.append(m.group(1))
    null = run(d)
    print(f"# zero-line-headroom files: {len(zero)}; null-run errors outside round9 evidence: {len(null)}")
    joined_ok = newline_refused = 0
    for i, f in enumerate(zero):
        p = os.path.join(d, f)
        raw = grow(p, 400, "joined", i); e1 = run(d) - null; open(p, "w", encoding="utf-8").write(raw)
        grow(p, 400, "newlines", i); e2 = run(d) - null; open(p, "w", encoding="utf-8").write(raw)
        joined_ok += not e1
        newline_refused += bool(e2)
        print(f"CELL {f:45s} joined+400B new_errors={len(e1)} | newlines+400B new_errors={len(e2)}")
    for f in ("CLAUDE.md", ".claude/rules/gate-scoping.md"):
        p = os.path.join(d, f)
        first = None
        for n in (400, 700, 900, 1000, 1100, 1300, 1600, 2000):
            raw = grow(p, n, "joined", 99); e = run(d) - null; open(p, "w", encoding="utf-8").write(raw)
            if e and first is None:
                first = n
                print(f"# bound {f}: first refused at +{n} B joined: {sorted(e)[0][:150]}")
                break
        print(f"RESULT bound_bytes_{re.sub(r'[^a-z]', '_', f.lower())}={first} B")
    print(f"RESULT zero_headroom_files={len(zero)} count")
    print(f"RESULT joined_400B_accepted={joined_ok} count")
    print(f"RESULT newline_400B_refused={newline_refused} count")
    shutil.rmtree(d, ignore_errors=True)
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
