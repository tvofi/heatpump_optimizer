"""One shard of `mutant_run.py --diff`: the same mutants, the same command, every Nth.

    python3 dev/audit/harnesses/mutant_run_diff_shards.py BASE...HEAD I N ['<argv>']
    for i in 0 1 2 3; do python3 dev/audit/harnesses/mutant_run_diff_shards.py \\
        "$(git merge-base origin/main HEAD)...HEAD" $i 4 > shard-$i.log & done; wait

`tools/audit/seat/mutant_run.py --diff` runs its mutants one after another; over
a self-test that takes a minute that is hours (R10-HOTFIX-MUTANT-RUN-DARWIN: 123
mutants). This calls the driver's own `added_lines`, `diff_mutants`,
`Workspace` and `run_cmd` and runs the mutants whose index in `diff_mutants`'
list is I modulo N, in a `git archive` copy of HEAD, so N of these side by side
cover the list the serial pass covers. '<argv>' defaults to the driver's own
self-test.

Prints `shard I/N: <mine> of <all>`, then one line per mutant, KILLED included
(the serial pass prints none for a kill): `KILLED|SURVIVED|FORKCAP file:line
OPERATOR  <mutated line>  [#index rc=N]`, then `DONE`. `BASELINE FAILS`, exit 3,
when the command fails on the unedited copy. Timing-bound checks can fail under
N-fold load: a KILLED here whose `rc` is the command's and not a timeout is
still that command failing, so re-run one shard alone before reading a kill
that matters.
"""
from __future__ import annotations

import shlex
import sys
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
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
import mutant_run as m  # noqa: E402 -- the driver under measurement


def main(argv: list[str]) -> int:
    rng, i, n = argv[0], int(argv[1]), int(argv[2])
    cmd = shlex.split(argv[3] if len(argv) > 3 else "python3 -I tools/audit/seat/mutant_run.py --self-test")
    ws = m.Workspace(ROOT, sorted(m.added_lines(ROOT, rng)), False, rev="HEAD")
    try:
        mutants = m.diff_mutants(ROOT, rng, ws.dir)
        mine = [(k, x) for k, x in enumerate(mutants) if k % n == i]
        print(f"shard {i}/{n}: {len(mine)} of {len(mutants)}", flush=True)
        if m.run_cmd(cmd, ws.dir, 600) != 0:
            print("BASELINE FAILS", flush=True)
            return 3
        for k, (rel, line, op, text, new) in mine:
            rc = ws.apply(rel, text, cmd, 600)
            tag = "FORKCAP" if rc == m.FORKCAP_RC else ("SURVIVED" if rc == 0 else "KILLED")
            print(f"{tag} {rel}:{line} {op}  {new}  [#{k} rc={rc}]", flush=True)
    finally:
        ws.close()
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
