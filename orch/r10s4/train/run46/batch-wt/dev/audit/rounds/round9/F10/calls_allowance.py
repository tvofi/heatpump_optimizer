"""Round-9 F10.2 evidence: where tests/stress.py's production-call allowance
(SCENARIO_CALLS_GROWTH) sits, measured with the channel's own driver, population
and judge, so a reviewer re-runs the figures rather than trusts them.

  calls_allowance.py history [CACHE_DIR] -- every first-parent solver merge
      1936d5ca..6793659c against its first parent: legitimate unvouched growth
      and what each candidate allowance fires on
  calls_allowance.py pair HERE BASE -- one arm: HERE and BASE are revisions or
      checked-out trees (a defect re-introduced in a worktree, say)

Run from the repository root under PYTHONPATH=tests/hastub. Each capture solves
the population once in a fresh interpreter; history is 22 of them.
"""
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

import json
import os
import subprocess
import sys
import tempfile

ROOT = str(repo_root(__file__))
sys.path[:0] = [os.path.join(ROOT, "tests"), os.path.join(ROOT, "custom_components")]
import stress  # noqa: E402

#: (merge, first parent) for every first-parent merge that touched the solve.
PAIRS = (("5dfa6684", "48786f65"), ("830f84ad", "3d1826b2"), ("3d1826b2", "754d2319"),
         ("3dfebc16", "1f1ec731"), ("3defa2d5", "5395394d"), ("31394964", "cdbca706"),
         ("2eef524d", "fab17619"), ("fab17619", "49fc8bbe"), ("49fc8bbe", "2d71759e"),
         ("9c6b923f", "0c9c4000"), ("0c9c4000", "800d7aab"), ("dbcca5fd", "6ff749d6"),
         ("058e89f1", "48b696c1"))
ALLOWANCES = (0.02, 0.05, 0.10, 0.12)


def capture(rev, cache):
    out = os.path.join(cache, os.path.basename(rev.rstrip("/")) + ".json")
    if os.path.exists(out):
        return json.load(open(out))
    pop = stress.calls_population(stress.sweep_combinations(), stress.load_budget_table())
    specs, tree = os.path.join(cache, "specs.json"), rev
    json.dump(pop, open(specs, "w"))
    if not os.path.isdir(rev):
        tree = tempfile.mkdtemp(prefix="calls_")
        subprocess.run(["git", "worktree", "add", "--detach", tree, rev], cwd=ROOT, check=True, capture_output=True)
    try:
        env = {**os.environ, "PYTHONPATH": os.path.join(tree, "tests", "hastub")}
        subprocess.run([sys.executable, "-c", stress.CALLS_PROBE_DRIVER, tree, out, specs], env=env, check=True)
    finally:
        if tree != rev:
            subprocess.run(["git", "worktree", "remove", "--force", tree], cwd=ROOT, capture_output=True)
    return json.load(open(out))


def unvouched(here, base):
    """(label, calls ratio over the evaluation or simulate ratio) per covered scenario."""
    for label in stress.calls_drift(here, base)["covered"]:
        x, y = here[label], base[label]
        vouched = x["evals"] / y["evals"]
        if y["simulate"]:
            vouched = max(vouched, x["simulate"] / y["simulate"])
        yield label, sum(x["calls"].values()) / sum(y["calls"].values()) / vouched


def main(argv):
    if argv[:1] == ["pair"] and len(argv) == 3:
        cache = tempfile.mkdtemp(prefix="calls_pair_")
        here, base = capture(argv[1], cache), capture(argv[2], cache)
        drift = stress.calls_drift(here, base)
        print("RESULT " + " ".join(f"{k}={len(v)}" for k, v in drift.items()))
        for label, excess in sorted(unvouched(here, base)):
            print(f"  {label:36} unvouched {excess:.4f}x")
        return 0
    if argv[:1] != ["history"]:
        print(__doc__)
        return 2
    cache = argv[1] if len(argv) > 1 else tempfile.mkdtemp(prefix="calls_hist_")
    worst, fires = [], {g: set() for g in ALLOWANCES}
    for merge, parent in PAIRS:
        here, base = capture(merge, cache), capture(parent, cache)
        drift = stress.calls_drift(here, base)
        for label, excess in unvouched(here, base):
            worst.append((round(excess, 4), merge, label))
            for g in ALLOWANCES:
                if excess > 1 + g:
                    fires[g].add((merge, label))
        print(f"{merge} vs {parent}: " + " ".join(f"{k} {len(v)}" for k, v in drift.items()))
    print(f"RESULT pairs={len(PAIRS)} judged_scenario_pairs={len(worst)}")
    for g in ALLOWANCES:
        print(f"RESULT allowance={g} fires={len(fires[g])} merges={sorted({m for m, _ in fires[g]})}")
    print("RESULT largest_unvouched=", sorted(worst, reverse=True)[:6])
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)  # the budget table path is relative to the repository root
    sys.exit(main(sys.argv[1:]))
