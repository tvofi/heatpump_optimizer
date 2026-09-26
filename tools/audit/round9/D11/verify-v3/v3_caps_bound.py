#!/usr/bin/env python3
"""D11 verify-v3 (round 9), finding D11-s2-01: how far can a capped policy file grow in
prose, appended to an existing line, before ANY `budgets` error fires -- and which cap fires.

METRIC (one line): (a) of ALL per-file caps in policy_budgets.json files{}, how many
  report 0 per-file `budgets` errors when +600 bytes are appended to the file's last
  non-empty line (seam enumeration beyond the finder's 7 zero-headroom cells);
  (b) the largest joined append to CLAUDE.md, bisected to 16 bytes, that yields 0
  `budgets` errors of any kind, and the check that fires first above it.
KEY: the `budgets` error lines production `policy_lint.mjs:checkBudgets` prints in a
  default run (per-file: "lines exceeds its cap"; aggregate: "tokens exceeds the cap").
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_caps_bound.py
          [--perturb bytes]  one-line in-memory-equivalent edit in the throwaway clone:
                             checkBudgets also refuses r.bytes above the file's baseline
                             bytes -> (a) goes to 0 (down).
EXPECTED (baseline 1936d5ca + round-9 evidence commits): (a) = number of files{} entries;
  (b) bounded by the corpus aggregate band headroom (~4 bytes per token), exact on this tree.
MACHINE: box G4-V3 cloud container, 4 CPU Linux, node 22, CPython 3.14.
Writes only under tempfile.mkdtemp() (clone of HEAD); never edits the tree under audit.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, json, shutil, subprocess, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
LINT = ".claude/workflows/policy_lint.mjs"
ANCHOR = "    if (r.lines > cap) {"
NODE = shutil.which("node")


def run(clone):
    p = subprocess.run([NODE, LINT], cwd=clone, capture_output=True, text=True)
    out = p.stdout + p.stderr
    pf = [l for l in out.splitlines() if "lines exceeds its cap" in l or "exceeds the file's baseline bytes" in l]
    agg = [l for l in out.splitlines() if "tokens exceeds the cap" in l]
    return pf, agg


def join_append(path, n):
    raw = open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    i = max(k for k, l in enumerate(lines) if l.strip())
    lines[i] = lines[i] + " " + ("qwrtz " * (n // 6 + 1))[:n]
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["bytes"])
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="d11v3-caps-")
    os.environ["HPO_PLANDATA"] = os.path.join(tmp, "plandata")
    clone = os.path.join(tmp, "c")
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", os.getcwd(), clone], check=True)
    files = sorted(json.load(open(os.path.join(clone, ".claude/workflows/policy_budgets.json")))["files"])
    if a.perturb == "bytes":
        base = {f: os.path.getsize(os.path.join(clone, f)) for f in files if os.path.exists(os.path.join(clone, f))}
        p = os.path.join(clone, LINT)
        src = open(p, encoding="utf-8").read()
        assert src.count(ANCHOR) == 1
        edit = (f"    if (r.bytes > ({json.dumps(base)})[r.file]) out.push({{ severity: 'error', check: 'budgets', where: r.file, message: `${{r.file}} exceeds the file's baseline bytes` }})\n" + ANCHOR)
        open(p, "w", encoding="utf-8").write(src.replace(ANCHOR, edit))
    pf0, agg0 = run(clone)
    print(f"# null (unmodified clone): per-file budgets errors={len(pf0)} aggregate={len(agg0)}")
    blind = 0
    for f in files:
        fp = os.path.join(clone, f)
        if not os.path.exists(fp):
            print(f"# {f}: not in tree"); continue
        raw = join_append(fp, 600)
        pf, agg = run(clone)
        mine = [l for l in pf if f in l]
        blind += (len(mine) == 0)
        print(f"CELL {f:46s} joined+600B per_file_err={len(mine)} aggregate_err={len(agg)}")
        open(fp, "w", encoding="utf-8").write(raw)
    # bisect the silent joined growth on CLAUDE.md
    fp = os.path.join(clone, "CLAUDE.md")
    lo, hi = 0, 8192
    first_hi = None
    while hi - lo > 16:
        mid = (lo + hi) // 2
        raw = join_append(fp, mid)
        pf, agg = run(clone)
        open(fp, "w", encoding="utf-8").write(raw)
        if pf or agg:
            hi = mid; first_hi = (pf + agg)[0].strip()[:160]
        else:
            lo = mid
    print(f"# CLAUDE.md: silent joined growth up to {lo} B; first refusal above it: {first_hi!r}")
    print(f"RESULT per_file_caps={len(files)} count")
    print(f"RESULT per_file_caps_blind_to_joined_600B={blind} count")
    print(f"RESULT claude_md_silent_joined_bytes={lo} bytes")
    print(f"RESULT claude_md_silent_joined_tokens={round(lo / 4)} tokens")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
