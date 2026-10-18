#!/usr/bin/env python3
"""R10-TRAIN-RAISE-HOLD (#2401): replay the train's raise reading on live pull requests.

    python3 dev/audit/harnesses/r10_train_raise_hold_replay.py PR[:BASE] [PR[:BASE] ...]

For each pull request, at its live head and three-dot from origin/main (or
from BASE, for one main already holds: #2401 merged at 07a09406a, its base
was 176851e950), prints two readings of "is this a budget raise":

  path     the defect's rule, as merge_train.py's approve and
           queue_pre_flight.py applied it before the fix: any changed path
           ending `_budgets.json` is a raise;
  gate     `Train.raise_hold`, the fix: budget_raise_gate's own
           `raises_between` from the merge base, then -- on a raise only --
           the owner's approval at the head with the body's justification and
           the mandate judged now, exactly as approve and pre-flight read it.

Read-only: it fetches the head and calls `gh` read APIs; it never pushes,
approves, comments or merges. A read that fails prints the train's own Stop.
"""
import sys
import tempfile
from pathlib import Path



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


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import merge_train as mt  # noqa: E402


def main(argv: "list[str]") -> int:
    if not argv or not all(a.split(":")[0].isdigit() for a in argv):
        print(__doc__)
        return 2
    with tempfile.TemporaryDirectory() as d:
        t = mt.Train("tvofi/heatpump_optimizer", Path(d), None, "", (), 1)
        for arg in argv:
            pr, _, at = arg.partition(":")
            pr = int(pr)
            h = t.head(pr)
            t.run = t._run  # a BASE answers its own entry only
            t.run(["git", "fetch", "-q", "origin", "main", h])
            base = t.out("git", "merge-base", at or "origin/main", h)
            files = t.out("git", "diff", "--no-renames", "--name-only", base, h).split()
            path = [f for f in files if f.endswith("_budgets.json")]
            print(f"#{pr} head {h[:12]} base {base[:12]}")
            print(f"  path : {'RAISE' if path else 'none'} ({', '.join(path) or 'no budget path'})")
            if at:  # raise_hold reads the merge base with origin/main; answer it with BASE's
                real = t.run

                def run(argv, cwd=mt.ROOT, stdin=None, real=real, base=base):
                    if argv[:3] == ["git", "merge-base", "origin/main"]:
                        return 0, base + "\n"
                    return real(argv, cwd=cwd, stdin=stdin)
                t.run = run
            try:
                raises, held, why = t.raise_hold(pr, h, files)
                print(f"  gate : {len(raises)} raise(s), {'HOLDS' if held else 'STOPS'}: {why}")
            except mt.Stop as s:
                print(f"  gate : STOP {s.step}: {s.why}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
