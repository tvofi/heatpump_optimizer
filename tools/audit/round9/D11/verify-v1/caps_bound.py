"""D11 V1 (verify-v1) harness for D11-s2-01: how far can a capped policy file grow
by appending prose to an existing line before ANY `[budgets]` error fires?

Metric: largest joined append (bytes, 200-byte steps, up to 4000) to one file's last
  non-empty line for which a default policy_lint run emits zero `[budgets]` lines
  beyond the unmodified tree's; and, beside it, the same for a NEWLINES arm (same
  bytes as 75-char new lines). Per-file line cap bound vs aggregate-band bound.
Count key: `[budgets]` lines printed by .claude/workflows/policy_lint.mjs (production).
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D11/verify-v1/caps_bound.py
Baseline: 1936d5ca + round-9 evidence (handoff/audit-r9-evidence). Machine: G4 box, 4 CPUs.
Writes only in a private `git worktree` under $TMPDIR, removed at the end.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import subprocess, tempfile, time, random

T0P, T0T = time.process_time(), time.thread_time()
ROOT = os.getcwd()
LINT = ".claude/workflows/policy_lint.mjs"
CELLS = ["CLAUDE.md", ".claude/rules/delivery-status-tracking.md", ".claude/rules/gate-scoping.md"]


def words(n, seed):
    rng = random.Random(seed); out = []
    while len(" ".join(out)) < n:
        out.append("".join(rng.choice("bcdfghjklmnpqrstvwxz") for _ in range(rng.randint(4, 9))))
    return " ".join(out)[:n]


def budgets(wt):
    p = subprocess.run(["node", LINT], cwd=wt, capture_output=True, text=True)
    return [l.strip() for l in (p.stdout + p.stderr).splitlines() if "[budgets]" in l]


def main():
    tmp = tempfile.mkdtemp(prefix="d11v1-caps-")
    os.environ["HPO_PLANDATA"] = os.path.join(tmp, "plandata")
    wt = os.path.join(tmp, "wt")
    subprocess.run(["git", "-C", ROOT, "worktree", "add", "-q", "--detach", wt, "HEAD"], check=True)
    try:
        base = set(budgets(wt))
        print(f"# baseline [budgets] lines: {len(base)}")
        for i, cell in enumerate(CELLS):
            path = os.path.join(wt, cell)
            orig = open(path, encoding="utf-8").read()
            res = {}
            for arm in ("joined", "newlines"):
                first_fire, first_msg = None, ""
                for n in range(200, 4001, 200):
                    add = words(n, i)
                    if arm == "joined":
                        lines = orig.split("\n")
                        k = max(j for j, l in enumerate(lines) if l.strip())
                        lines[k] += " " + add
                        new = "\n".join(lines)
                    else:
                        new = orig + "\n".join(add[j:j + 75] for j in range(0, n, 75)) + "\n"
                    open(path, "w", encoding="utf-8").write(new)
                    extra = [l for l in budgets(wt) if l not in base]
                    if extra:
                        first_fire, first_msg = n, extra[0][:140]
                        break
                open(path, "w", encoding="utf-8").write(orig)
                res[arm] = (first_fire, first_msg)
                print(f"CELL {cell} arm={arm}: first refusal at +{first_fire} bytes :: {first_msg}")
            acc_j = (res["joined"][0] or 4200) - 200
            acc_n = (res["newlines"][0] or 4200) - 200
            print(f"RESULT {os.path.basename(cell)}_joined_max_accepted={acc_j} bytes")
            print(f"RESULT {os.path.basename(cell)}_newlines_max_accepted={acc_n} bytes")
    finally:
        subprocess.run(["git", "-C", ROOT, "worktree", "remove", "--force", wt])
    pt, tt = time.process_time() - T0P, time.thread_time() - T0T
    print(f"RESULT thread_factor={pt / tt if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
