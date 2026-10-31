"""D11-s2 harness: per-file policy caps count LINES, so prose grows unrefused.

Metric: of N capped policy files at zero line headroom, how many accept +600 bytes
  (~150 tokens) of new prose appended to an EXISTING line with zero per-file
  `budgets` errors from policy_lint.mjs:checkBudgets (count; want 0, is N).
Count key: the per-file `budgets` finding checkBudgets itself emits
  ("<file> ... lines exceeds its cap"), read from the production run's output --
  never the harness's own byte count.
Arms per cell (each a full default policy_lint run in a throwaway clone):
  JOINED    +600 bytes on the last non-empty line          -> per-file errors
  NEWLINES  the same 600 bytes as 8 new lines (live control) -> must fire
  PERTURBED JOINED, under a one-line production edit: checkBudgets also refuses
            `r.bytes` above the file's baseline bytes        -> must fire
Aggregate (always/corpus/role) errors are printed separately: 600 bytes stays
inside every band at the baseline, so the aggregates are the null arm.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s2/caps_unit.py
Expected: RESULT joined_unrefused=7 of 7, newline_refused=7, perturbed_refused=7 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B3, 4 CPUs, Linux.
Runs from the repository root; clones HEAD into a temp root; writes nothing in the tree.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import temp_root, clone, node, tail, ROOT  # noqa: E402
import json, random, re, subprocess

CELLS = ["CLAUDE.md", "AGENTS.md", ".claude/skills/steward/SKILL.md",
         ".claude/rules/claim-files.md", ".claude/rules/gate-scoping.md",
         ".claude/rules/comment-readback.md", ".claude/rules/delivery-status-tracking.md"]
LINT = ".claude/workflows/policy_lint.mjs"
ANCHOR = "    if (r.lines > cap) {"


def words(n_bytes, seed):
    rng = random.Random(seed)
    out = []
    while len(" ".join(out)) < n_bytes:
        out.append("".join(rng.choice("bcdfghjklmnpqrstvwxz") for _ in range(rng.randint(4, 9))))
    return " ".join(out)[:n_bytes]


def grow(path, mode, seed):
    raw = open(path, encoding="utf-8").read()
    add = words(600, seed)
    lines = raw.split("\n")
    if mode == "joined":
        i = max(k for k, l in enumerate(lines) if l.strip())
        lines[i] = lines[i] + " " + add
        new = "\n".join(lines)
    else:
        chunk = [add[j:j + 75] for j in range(0, 600, 75)]
        new = raw + ("" if raw.endswith("\n") else "\n") + "\n".join(chunk) + "\n"
    open(path, "w", encoding="utf-8").write(new)


def per_file_errors(out, rel):
    return sum(1 for l in out.splitlines() if rel in l and "lines exceeds its cap" in l
               or (rel in l and "exceeds the file's baseline" in l))


def agg_errors(out):
    return sum(1 for l in out.splitlines() if "tokens exceeds the cap" in l)


def perturb(clone_dir, base_bytes):
    p = os.path.join(clone_dir, LINT)
    src = open(p, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, "perturbation anchor moved"
    edit = (f"    if (r.bytes > ({json.dumps(base_bytes)})[r.file]) out.push({{ severity: 'error', check: 'budgets', where: r.file, message: `${{r.file}} exceeds the file's baseline bytes` }})\n"
            + ANCHOR)
    open(p, "w", encoding="utf-8").write(src.replace(ANCHOR, edit))


def main():
    tmp = temp_root("caps")
    rows = []
    base_bytes = {c: os.path.getsize(os.path.join(ROOT, c)) for c in CELLS}
    # Null: the unmodified clone.
    c0 = os.path.join(tmp, "null")
    head = clone(c0)
    rc, out = node(c0, LINT)
    null_pf = sum(per_file_errors(out, c) for c in CELLS)
    print(f"# head {head}; null run rc={rc}, per-file budgets errors on cells={null_pf}, aggregate={agg_errors(out)}")
    for i, cell in enumerate(CELLS):
        res = {}
        for arm in ("joined", "newlines", "perturbed"):
            d = os.path.join(tmp, f"{i}-{arm}")
            clone(d)
            grow(os.path.join(d, cell), "newlines" if arm == "newlines" else "joined", seed=i)
            if arm == "perturbed":
                perturb(d, base_bytes)
            rc, out = node(d, LINT)
            res[arm] = (per_file_errors(out, cell), agg_errors(out), rc)
        tok = round(600 / 4)
        print(f"CELL {cell:45s} +{tok} tok ({100*600/base_bytes[cell]:.1f}% of file) "
              f"joined pf={res['joined'][0]} agg={res['joined'][1]} | newlines pf={res['newlines'][0]} | perturbed pf={res['perturbed'][0]}")
        rows.append(res)
    n = len(CELLS)
    print(f"RESULT cells={n} count")
    print(f"RESULT null_per_file_errors={null_pf} count")
    print(f"RESULT joined_unrefused={sum(1 for r in rows if r['joined'][0] == 0 and r['joined'][1] == 0)} count")
    print(f"RESULT newline_refused={sum(1 for r in rows if r['newlines'][0] > 0)} count")
    print(f"RESULT perturbed_refused={sum(1 for r in rows if r['perturbed'][0] > 0)} count")
    tail()


if __name__ == "__main__":
    main()
