"""The drift gate for golden fixtures whose floats do not travel.

`valve_storage_smart_write`, `wood_two_tank`, `wood_two_tank_smart_write`,
`wood_coil` and `valve_upper_direct_slab` do not reproduce across
scipy/numpy builds — and not at the last decimal: these are the non-convex
valve/wood solves, and a different BLAS lands them in a different local
optimum (plan-shape flips, different compressor-start counts). On such a
machine `tests/golden.py` reports them as DIFF on a clean checkout of main,
which makes "fails, as expected" worthless as a review signal: a real
regression in exactly these scenarios would hide behind the label.

This script restores the signal. It captures scenarios twice in the SAME
environment — once from this working tree, once from a pristine worktree
of a reference commit (default `origin/main`) — and requires the two
computed payload sets to be byte-identical. Solver noise cancels because
both runs share the solver; anything left is this branch's doing.

    PYTHONPATH=tests/hastub python3 tests/env_drift.py [ref]          # 5 sensitive fixtures
    PYTHONPATH=tests/hastub python3 tests/env_drift.py --all [ref]    # every fixture (CI)

`--all` is what CI runs: committed fixtures were recorded on one machine
and CI runs on another, so exact comparison against the files would cry
wolf; comparing two captures made by the same runner is environment-proof
by construction.

A branch is allowed to move fixtures — behaviour changes are sometimes
the point — but it must say so: `tests/golden/claimed_drift.txt` lists
one scenario name per line (with a reason after `#`). Listed scenarios
still print their diffs, but do not fail the gate. The file is meant to
be populated by the PR that moves the fixtures and emptied by the next
one, so a non-empty file is always visible in review.

Scenarios that exist only on this branch (a PR adding coverage) have no
baseline to compare against; they are reported and pass — the golden
invariant layer inside `golden.py` still vets them. Scenarios that exist
only on the baseline (a PR deleting coverage) fail unless claimed.

Exit 0: no unclaimed drift. Exit 1: this branch moved a fixture the
reference does not move in this environment — either a regression, or a
behaviour change the PR must claim. Never re-record the five sensitive
fixtures on a machine where golden.py already reports them as DIFF.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

SENSITIVE = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)

CLAIM_FILE = os.path.join("tests", "golden", "claimed_drift.txt")


def capture_tree(root: str, out_path: str, everything: bool) -> None:
    """Worker mode: capture scenarios from one repo root."""
    os.chdir(root)  # golden.py resolves its fixtures relative to cwd
    sys.path.insert(0, os.path.join(root, "tests"))
    sys.path.insert(0, os.path.join(root, "custom_components"))
    import golden

    if everything:
        payloads = {n: golden.capture(n, s) for n, s in golden.SCENARIOS.items()}
        for name, config in golden.coordinator_scenarios().items():
            payloads[name] = golden.capture_coordinator(config)
        payloads["config_flow"] = golden.capture_config_flow()
    else:
        payloads = {n: golden.capture(n, golden.SCENARIOS[n]) for n in SENSITIVE}
    with open(out_path, "w") as f:
        json.dump(payloads, f, indent=1, sort_keys=True)


def _diff_leaves(a, b, path, out) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: present on one side only")
            else:
                _diff_leaves(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _diff_leaves(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def _claimed(repo: str) -> dict[str, str]:
    """Scenario names a PR has declared as deliberately moved."""
    path = os.path.join(repo, CLAIM_FILE)
    claims: dict[str, str] = {}
    if not os.path.exists(path):
        return claims
    for line in open(path):
        body, _, comment = line.partition("#")
        name = body.strip()
        if name:
            claims[name] = comment.strip() or "no reason given"
    return claims


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--capture":
        everything = "--all" in sys.argv[4:]
        capture_tree(sys.argv[2], sys.argv[3], everything)
        return 0

    args = [a for a in sys.argv[1:] if a != "--all"]
    everything = "--all" in sys.argv[1:]
    ref = args[0] if args and args[0] else "origin/main"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    claims = _claimed(repo)
    tmp = tempfile.mkdtemp(prefix="env_drift_")
    worktree = os.path.join(tmp, "baseline")
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree, ref],
        cwd=repo, check=True, capture_output=True,
    )
    try:
        outputs = {}
        for label, root in (("branch", repo), ("baseline", worktree)):
            out_path = os.path.join(tmp, f"{label}.json")
            env = dict(os.environ)
            env["PYTHONPATH"] = os.path.join(root, "tests", "hastub")
            cmd = [sys.executable, os.path.abspath(__file__),
                   "--capture", root, out_path]
            if everything:
                cmd.append("--all")
            subprocess.run(cmd, check=True, env=env)
            outputs[label] = json.load(open(out_path))
            print(f"  captured {len(outputs[label])} scenarios from {label}")

        branch, baseline = outputs["branch"], outputs["baseline"]
        failed = 0
        claimed_hits = []
        for name in sorted(set(branch) | set(baseline)):
            if name not in baseline:
                print(f"  new   {name}: no baseline on {ref} (added by this branch)")
                continue
            if name not in branch:
                if name in claims:
                    claimed_hits.append(name)
                    print(f"  CLAIMED {name}: removed ({claims[name]})")
                else:
                    failed += 1
                    print(f"  DRIFT {name}: scenario removed by this branch")
                continue
            diffs: list[str] = []
            _diff_leaves(baseline[name], branch[name], name, diffs)
            if not diffs:
                print(f"  ok    {name} is byte-identical to {ref} here")
            elif name in claims:
                claimed_hits.append(name)
                print(f"  CLAIMED {name}: {len(diffs)} leaves moved ({claims[name]})")
                for line in diffs[:3]:
                    print(f"         {line}")
            else:
                failed += 1
                print(f"  DRIFT {name}: {len(diffs)} leaves moved vs {ref}")
                for line in diffs[:5]:
                    print(f"         {line}")

        stale = sorted(set(claims) - set(claimed_hits))
        if stale:
            # A claim nothing uses is a stale entry from an earlier PR; it
            # would silently excuse the next accidental drift, so it fails.
            failed += len(stale)
            for name in stale:
                print(f"  STALE claim for {name}: nothing drifted, remove it")

        if failed:
            print(f"\n{failed} UNCLAIMED DRIFT(S) vs {ref}")
            print("This branch moved scenarios the baseline does not move in")
            print("this environment: a regression, or a change that must be")
            print("claimed in tests/golden/claimed_drift.txt and justified in")
            print("the PR. Never re-record the five sensitive fixtures on a")
            print("machine where golden.py already reports them as DIFF.")
            return 1
        n = len(set(branch) | set(baseline))
        print(f"\nNO UNCLAIMED DRIFT: {n} scenario(s) checked against {ref}")
        return 0
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree],
            cwd=repo, capture_output=True,
        )


if __name__ == "__main__":
    sys.exit(main())
