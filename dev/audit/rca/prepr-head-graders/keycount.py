"""How many first-parent merges into main each `ci_predict.GRADERS` row's key
reaches: a merge is keyed when its first-parent diff changes a file in the
row's `mjs_closure` that the row's job restores (`grader_hit`'s rule). Both
keys are counted, `named` off (the round-2 key) and on (the round-3 key).

    python3 -I dev/audit/rca/prepr-head-graders/keycount.py <tip> <since>

Run from the root of the tree whose predictor is measured.
"""
import subprocess
import sys
from pathlib import Path

root = Path.cwd()
sys.path[:0] = [str(root / "tools/pr"), str(root / "tools/policy"), str(root / "tests")]
import agreement_py  # noqa: E402
import ci_predict  # noqa: E402


def main(tip: str, since: str) -> int:
    text = (root / agreement_py.WORKFLOW).read_text()
    merges = subprocess.run(["git", "rev-list", "--first-parent", "--merges", f"--since={since}", tip],
                            capture_output=True, text=True, check=True).stdout.split()
    diffs = [set(subprocess.run(["git", "diff", "--no-renames", "--name-only", f"{m}^1", m],
                                capture_output=True, text=True, check=True).stdout.split()) for m in merges]
    print(f"merges {len(merges)} (git rev-list --first-parent --merges --since={since} {tip})")
    keyed = {False: set(), True: set()}
    for job, _, mark, homes, whole, _ in ci_predict.GRADERS:
        entry = next(p for p in homes if (root / p).is_file())
        specs = agreement_py.restore_specs(text, job)
        row = {}
        for named in (False, True):
            key = {f for f in ci_predict.mjs_closure(root, entry, imports=whole, named=named)
                   if any(agreement_py.covers(s, f) for s in specs)}
            if not named and not whole:
                key = {entry}  # the round-2 key: the grader alone
            hit = {i for i, d in enumerate(diffs) if d & key}
            keyed[named] |= hit
            row[named] = (len(key), len(hit))
        print(f"{mark}: round-2 key {row[False][0]} files, {row[False][1]} keyed; "
              f"round-3 key {row[True][0]} files, {row[True][1]} keyed")
    print(f"any row keyed: round-2 {len(keyed[False])}, round-3 {len(keyed[True])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
