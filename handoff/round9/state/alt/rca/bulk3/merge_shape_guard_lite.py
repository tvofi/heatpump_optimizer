"""Re-implementation (this seat) of the #1041 RCA's merge_shape_guard, which was never pushed.
For each merge-subject enumerator: locate its pattern IN ITS SOURCE at <sha> by literal (V1),
derive the first-parent window <since>..<sha> checking git's exit (V2), and REFUSE an enumerator
that matches 0 of a non-empty window (the alarm condition is the empty set). Empty window -> UNCHECKED (V3).
usage: merge_shape_guard_lite.py REPO SHA SINCE [--widen]"""
import re, subprocess, sys, time
t0 = time.perf_counter()
repo, sha, since = sys.argv[1:4]; widen = "--widen" in sys.argv
def git(*a):
    p = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True); return p.returncode, p.stdout
ENUMS = [  # (name, file, literal locating the pattern, python regex extractor)
    ("policy_lint.MERGE_SUBJECT_RE", ".claude/workflows/policy_lint.mjs", r"const MERGE_SUBJECT_RE = /(.+)/\n"),
    ("stamp.PR_RE", "tools/release/stamp.py", r'PR_RE = re\.compile\(r"(.+)"\)\n'),
]
rc, log = git("log", "--first-parent", "--format=%s", f"{since}..{sha}")
if rc: print(f"REFUSE window: git log exited {rc}"); sys.exit(2)
subs = [s for s in log.splitlines() if s and not re.match(r"^v\d+\.\d+\.\d+", s)]
if not subs: print("UNCHECKED this run, not confirmed alive: empty window"); sys.exit(0)
dead = 0
for name, path, loc in ENUMS:
    rc, src = git("show", f"{sha}:{path}")
    m = re.search(loc, src) if rc == 0 else None
    if not m: print(f"REFUSE {name}: its pattern is no longer at {path}"); dead += 1; continue
    pats = [m.group(1)]
    if name.startswith("stamp") and "MERGE_SUBJECT_RE = re.compile" in src:  # stamp reads both shapes since #1057
        pats.append(re.search(r'MERGE_SUBJECT_RE = re\.compile\(r"(.+)"\)', src).group(1))
    if widen: pats.append(r"^Merge pull request #(\d+)\b")
    n = sum(1 for s in subs if any(re.search(p, s) for p in pats))
    v = "REFUSE" if n == 0 else "ok"; dead += n == 0
    print(f"{v:6} {name}: matches {n} of {len(subs)} merge subject(s) in {since}..{sha[:8]}")
print(f"MERGE-SHAPE: {dead} dead enumerator(s) of {len(ENUMS)}  ({time.perf_counter()-t0:.3f}s)"); sys.exit(1 if dead else 0)
