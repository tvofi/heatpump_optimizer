#!/usr/bin/env python3
"""r10_triage_gate_replay.py -- replay roster_edit.py's triage gate over a roster's carries.

    python3 dev/audit/harnesses/r10_triage_gate_replay.py <roster.json> [--cite BATCH]

R10-FLOW-ARCH-PLANNER (decision 0015). For every carry entry of the roster,
judges it as if it were being appended now, with roster_edit's own
`triage_refusal` (imported, never copied) and the ruling reader at this
checkout's tree. Prints `GATE <group>[<i>] refused|passes <why>` for each entry
the gate's detector names, then `replay: N carries, D proposal-sourced, R
refused`. With `--cite dev/programme/triage/<file>.md`, each proposal-sourced
carry is judged again with `triage: <file>#P<n>` appended, P<n> read from the
carry's own `triage P<n>` -- the control that a cited ACCEPT passes and a
proposal the batch does not hold is still refused.
"""
import argparse
import json
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
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import roster_edit  # noqa: E402


def read(rel):
    f = ROOT / rel
    return f.read_text(encoding="utf-8") if f.is_file() else None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roster", type=Path)
    ap.add_argument("--cite")
    a = ap.parse_args(argv)
    groups = json.loads(a.roster.read_text(encoding="utf-8"))["groups"]
    n = d = r = 0
    for g in groups:
        for i, c in enumerate(g.get("carry") or []):
            n += 1
            m = roster_edit.PROPOSAL_RE.search(c)
            if not m and not roster_edit.RULING_CITE_RE.search(c):
                continue
            d += 1
            text = c
            if a.cite and m:
                text = f"{c} triage: {a.cite}#P{m.group(0).split('P')[-1]}"
            why = roster_edit.triage_refusal([text], read)
            r += why is not None
            print(f"GATE {g['group']}[{i}] {'refused' if why else 'passes'} {why or ''}".rstrip())
    print(f"replay: {n} carries, {d} proposal-sourced, {r} refused")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
