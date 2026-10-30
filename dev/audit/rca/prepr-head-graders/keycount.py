"""How many first-parent merges into main each restoring job's key reaches: a
merge is keyed for a job when its first-parent diff changes a path that job's
restore pathspecs cover and its first parent holds (`ci_predict.restored_hit`,
the graders arm's own rule, over the first parent's own governance.yml). Each
set of jobs keyed together is counted too: they run side by side. A
pathspec no path matches is the null control: it keys nothing.

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


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def main(tip: str, since: str) -> int:
    merges = git("rev-list", "--first-parent", "--merges", f"--since={since}", tip).split()
    print(f"merges {len(merges)} (git rev-list --first-parent --merges --since={since} {tip})")
    keyed: dict[str, int] = {}
    sets: dict[tuple[str, ...], int] = {}
    anyjob = null = 0
    for m in merges:
        text = git("show", f"{m}^1:{agreement_py.WORKFLOW}")
        names = git("diff", "--no-renames", "--name-only", f"{m}^1", m).split()
        at_tip = set(git("ls-tree", "-r", "--name-only", f"{m}^1").splitlines())
        hit = [j for j in ci_predict.restore_jobs(text)
               if ci_predict.restored_hit(names, agreement_py.restore_specs(text, j), at_tip, agreement_py.covers)]
        for j in hit:
            keyed[j] = keyed.get(j, 0) + 1
        anyjob += bool(hit)
        if hit:
            sets[tuple(sorted(hit))] = sets.get(tuple(sorted(hit)), 0) + 1
        null += bool(ci_predict.restored_hit(names, ["no/such/path"], at_tip, agreement_py.covers))
    for j, n in sorted(keyed.items()):
        print(f"{j}: {n} keyed")
    for jobs, n in sorted(sets.items()):
        print(f"exactly {' + '.join(jobs)}: {n}")
    print(f"any job keyed: {anyjob}")
    print(f"null control (pathspec no/such/path): {null} keyed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
