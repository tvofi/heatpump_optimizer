#!/usr/bin/env python3
"""R10-FLY-RELAY-REVIEW-FF: the field verdict items carry_audit.py flags, at any revision.

    python3 dev/audit/harnesses/r10_carry_field_figures.py <rev> [<rev> ...]

Loads tools/audit/carry_audit.py as <rev> holds it (git show) and runs its
items() over dev/audit/harnesses/r10_carry_field_verdicts.json, as the working
tree holds it: each field item alone under its own verdict word and heading,
and #2645's round-1 blocked VERDICT.md whole. Prints one line per revision:

  RESULT rev=<sha9> field_flagged=<n>/<total> v2645_flagged=<n>

Each field item is no finding (P308, P314, P329, CARRY 3, CARRY 5), so a sound
parser prints field_flagged=0; #2645's verdict holds one genuine NONBLOCK item.
Null control: the merge base 7539d1675 prints 17/17 and 8.
"""
from __future__ import annotations

import json
import subprocess
import sys
import types


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
sys.path.insert(0, str(ROOT / "tools/audit/seat"))  # roster_lib, which carry_audit imports


def flagged(rev: str) -> str:
    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:tools/audit/carry_audit.py"],
                         capture_output=True, text=True, check=True).stdout
    m = types.ModuleType("carry_audit_at_rev")
    m.__file__ = str(ROOT / "tools/audit/carry_audit.py")
    exec(compile(src, f"{rev}:tools/audit/carry_audit.py", "exec"), m.__dict__)
    fx = json.loads((ROOT / "dev/audit/harnesses/r10_carry_field_verdicts.json").read_text())
    n = sum(any(x["id"] == i and x["flagged"] for x in m.items(
        f"Fix review: {v['verdict']} {'d' * 40}\n\n## {v['section']}\n\n{v['text']}\n", True))
        for i, v in fx["items"].items())
    w = sum(x["flagged"] for x in m.items(fx["verdict_2645"]["whole"], True))
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=9", rev],
                         capture_output=True, text=True, check=True).stdout.strip()
    return f"RESULT rev={sha} field_flagged={n}/{len(fx['items'])} v2645_flagged={w}"


if __name__ == "__main__":
    for r in sys.argv[1:] or ["HEAD"]:
        print(flagged(r))
