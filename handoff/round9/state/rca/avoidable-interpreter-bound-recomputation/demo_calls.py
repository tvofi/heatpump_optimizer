"""RCA demo: the production-call channel prototyped in tests/stress.py on
handoff/r9-rca-avoidable-interpreter-bound-recomputation, driven arm by arm.

Metric: tests/stress.py:calls_drift's `over` list (the prototype's own verdict
code) and, beside it, the shipped gate's count verdicts (work_over_verdict on
evaluations and simulate steps) for the same pair of captures.
Arms (here-tree vs baseline-tree, both captured by CALLS_PROBE_DRIVER in fresh
interpreters, side by side):
  null      origin/main vs origin/main       -> over must be empty, ratio 1.000 exact
  defect    1936d5ca vs 45492d88             -> #985's per-row comfort twin against its
                                                 row-vectorised fix: over must be non-empty
  fixed     45492d88 vs 1936d5ca             -> the fix against the defect: over empty
  tariff2x  939ea6f9 vs 1936d5ca             -> peak_cost_batch run twice (D9-s2-03 shape):
                                                 over non-empty; shipped count verdicts silent
Command (from the prototype worktree root):
  PYTHONPATH=tests/hastub python3 <this> ARM [LABEL ...]
Commits 45492d88 and 939ea6f9 are local RCA demo commits (not pushed): recreate them with
`git am evidence/demo-commit-*.patch` on a branch at 1936d5ca (same one-hunk diffs).
"""
import json, os, subprocess, sys, tempfile, time
sys.path[:0] = ["tests", "custom_components"]
import stress

ARMS = {"null": ("origin/main", "origin/main"), "defect": ("1936d5ca", "45492d88"),
        "fixed": ("45492d88", "1936d5ca"), "tariff2x": ("939ea6f9", "1936d5ca")}
arm = sys.argv[1]
labels = sys.argv[2:] or None
here_ref, base_ref = ARMS[arm]
repo = stress.repository_root()
tmp = tempfile.mkdtemp(prefix="rca_calls_")
trees = []
for i, ref in enumerate((here_ref, base_ref)):
    wt = os.path.join(tmp, f"t{i}")
    subprocess.run(["git", "worktree", "add", "--detach", wt, ref], cwd=repo, check=True, capture_output=True)
    trees.append(wt)
t0 = time.perf_counter()
procs = [stress.capture_calls(wt, os.path.join(tmp, f"t{i}.json"), labels) for i, wt in enumerate(trees)]
rows = []
for i, p in enumerate(procs):
    out, err = p.communicate()
    assert p.returncode == 0, err[-500:]
    rows.append(json.load(open(os.path.join(tmp, f"t{i}.json"))))
wall = time.perf_counter() - t0
for wt in trees:
    subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=repo, capture_output=True)
here, base = rows
covered, replanned, over, unmetered = stress.calls_drift(here, base)
shipped = []
for label in covered:
    h, b = here[label], base[label]
    ratio = sum(h["calls"].values()) / sum(b["calls"].values())
    ev = stress.work_over_verdict(h["evals"], b["evals"])
    sim = stress.work_over_verdict(h["simulate"], b["simulate"])
    print(f"  {label:30s} calls {ratio:.4f}x  evals {h['evals']}/{b['evals']}  "
          f"simulate {h['simulate'] / b['simulate']:.4f}x  shipped_evals_over={ev} shipped_sim_over={sim}  "
          f"identical_calls={h['calls'] == b['calls']}  top_file_growth="
          f"{max(((h['calls'].get(f, 0) - b['calls'].get(f, 0)), f) for f in set(h['calls']) | set(b['calls']))}")
    shipped += [label] if (ev or sim) else []
for o in over:
    print("  OVER", o)
print(f"RESULT arm={arm} here={here_ref} base={base_ref} scenarios={len(here)} covered={len(covered)} "
      f"replanned={len(replanned)} unmetered={len(unmetered)} calls_over={len(over)} "
      f"shipped_count_over={len(shipped)} capture_wall_s={wall:.1f}")
