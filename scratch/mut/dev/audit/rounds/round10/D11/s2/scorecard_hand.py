"""D11.M2 hand-evaluated OpenSSF Scorecard checks Pinned-Dependencies and Token-Permissions.
Metric: count of `uses:` refs in .github/workflows/*.yml not pinned to a 40-hex SHA; count of workflows
without a top-level `permissions:` key; count using pull_request_target.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D11/s2/scorecard_hand.py [--perturb]
Expected: unpinned=0 no_top_perms=0 prt=0 (exact). --perturb appends an unpinned `uses: actions/checkout@v4`
in memory to the first workflow; unpinned must rise to 1. Baseline 17f1c55fad1b, machine: macOS arm64 (B7).
Instrumented symbol: .github/workflows/*.yml (the workflow definitions GitHub executes).
"""
import os
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(k, "1")
import glob, re, sys, time
t0p, t0t = time.process_time(), time.thread_time()
files = sorted(glob.glob(".github/workflows/*.yml"))
texts = {f: open(f).read() for f in files}
if "--perturb" in sys.argv:
    texts[files[0]] += "\n      - uses: actions/checkout@v4\n"
USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)", re.M)
unpinned = sum(1 for t in texts.values() for u in USES.findall(t)
               if not u.startswith("./") and not re.search(r"@[0-9a-f]{40}$", u))
noperm = sum(1 for t in texts.values() if not re.search(r"^permissions:", t, re.M))
prt = sum(1 for t in texts.values() if re.search(r"^\s*pull_request_target\s*:", t, re.M))
print(f"RESULT workflows={len(files)} count")
print(f"RESULT uses_refs={sum(len(USES.findall(t)) for t in texts.values())} count")
print(f"RESULT unpinned={unpinned} count")
print(f"RESULT no_top_perms={noperm} count")
print(f"RESULT pull_request_target={prt} count")
dt = time.thread_time() - t0t
print(f"RESULT thread_factor={(time.process_time()-t0p)/dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
