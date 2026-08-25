"""The drift gate for the five container-sensitive golden fixtures (G4b).

`valve_storage_smart_write`, `wood_two_tank`, `wood_two_tank_smart_write`,
`wood_coil` and `valve_upper_direct_slab` do not reproduce across
scipy/numpy builds — and not at the last decimal: these are the non-convex
valve/wood solves, and a different BLAS lands them in a different local
optimum (plan-shape flips, different compressor-start counts). On such a
machine `tests/golden.py` reports them as DIFF on a clean checkout of main,
which makes "fails, as expected" worthless as a review signal: a real
regression in exactly these scenarios would hide behind the label.

This script restores the signal. It captures all five scenarios twice in
the SAME environment — once from this working tree, once from a pristine
worktree of a reference commit (default `origin/main`) — and requires the
two computed payload sets to be byte-identical. Solver noise cancels
because both runs share the solver; anything left is this branch's doing.

    PYTHONPATH=tests/hastub python3 tests/env_drift.py [ref]

Exit 0: no drift. Exit 1: this branch moved a fixture main does not move —
either a regression, or a behaviour change the tranche must claim in its
commit message. On machines where the fixtures DO reproduce this check is
redundant (golden.py already proves identity against the stored files) but
still passes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

SCENARIOS = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)


def capture_tree(root: str, out_path: str) -> None:
    """Worker mode: capture the five scenarios from one repo root."""
    os.chdir(root)  # golden.py resolves its fixtures relative to cwd
    sys.path.insert(0, os.path.join(root, "tests"))
    sys.path.insert(0, os.path.join(root, "custom_components"))
    import golden

    payloads = {n: golden.capture(n, golden.SCENARIOS[n]) for n in SCENARIOS}
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


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--capture":
        capture_tree(sys.argv[2], sys.argv[3])
        return 0

    ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            subprocess.run(
                [sys.executable, os.path.abspath(__file__),
                 "--capture", root, out_path],
                check=True, env=env,
            )
            outputs[label] = json.load(open(out_path))
            print(f"  captured {len(outputs[label])} scenarios from {label}")

        failed = 0
        for name in SCENARIOS:
            diffs: list[str] = []
            _diff_leaves(
                outputs["baseline"][name], outputs["branch"][name], name, diffs
            )
            if diffs:
                failed += 1
                print(f"  DRIFT {name}: {len(diffs)} leaves moved vs {ref}")
                for line in diffs[:5]:
                    print(f"         {line}")
            else:
                print(f"  ok    {name} is byte-identical to {ref} here")
        if failed:
            print(f"\n{failed} OF {len(SCENARIOS)} SENSITIVE FIXTURES DRIFTED")
            print("This branch moved scenarios the baseline does not move in")
            print("this environment: a regression, or a change the tranche")
            print("must claim explicitly. Never re-record these five on a")
            print("machine where golden.py already reports them as DIFF.")
            return 1
        print(f"\nNO DRIFT: all {len(SCENARIOS)} sensitive fixtures match {ref}")
        return 0
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree],
            cwd=repo, capture_output=True,
        )


if __name__ == "__main__":
    sys.exit(main())
