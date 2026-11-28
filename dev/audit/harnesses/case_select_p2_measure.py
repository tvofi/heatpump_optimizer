#!/usr/bin/env python3
"""R11-CI-CASE-SELECT P2: what tests/case_select.py's plan would run for past pull requests.

    python3 dev/audit/harnesses/case_select_p2_measure.py prs <merge sha>...   one row per PR and case script
    python3 dev/audit/harnesses/case_select_p2_measure.py files               one row per production file

Reads `tests/case_closures.json` at this checkout and plans each case script at
this checkout's text. `prs`: the changed set is the PR's own three-dot diff
(`<merge>^1...<merge>^2`); a span the PR's diff edited (its hash moved between
those two texts) is planned as edited (rule ii), and a PR that edited a
script's header is FULL, as `plan` would print it on that PR. `files`: each
`custom_components/` file alone as the diff. Seconds are the table's per-span
`seconds`; the null for each row is the sum over every span of the same
recording, printed beside it. Rows at fraction 0 and at `case_sample.FRACTION`,
seeded by the merge's second parent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
import case_sample  # noqa: E402
import case_select as C  # noqa: E402


def git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout


def plan_row(script: str, changed: list[str], edited: set[str], seed: str, frac: float, table: dict):
    t = json.loads(json.dumps(table))
    spans = t["scripts"][script]["spans"]
    for sid in edited & set(spans):
        spans[sid]["hash"] = "edited-by-the-pr"
    source = (ROOT / script).read_text()
    blob = t["scripts"][script]["blob"]
    ids, line, _ = C.plan(script, source, changed, t, base_blob=blob, head_blob=blob,
                          event="pull_request", seed=seed, fraction=frac)
    e = C.entry(table, script)
    total = sum(v["seconds"] for v in e["spans"].values())
    if ids is None:
        return line, total, total
    return line, sum(e["spans"][i]["seconds"] for i in ids if i in e["spans"]), total


def edited_spans(script: str, a: str, b: str) -> tuple[set[str], bool]:
    """(span ids whose text moved between commits a and b, whether the header moved)."""
    ta, tb = git("show", f"{a}:{script}"), git("show", f"{b}:{script}")
    if not tb or ta == tb:
        return set(), False
    ha, hha, sa, _ = C.split(ta) if ta else ([], "", [], [])
    hb, hhb, sb, _ = C.split(tb)
    old = {s.id: s.hash for s in sa}
    return {s.id for s in sb if old.get(s.id) != s.hash}, hha != hhb


def prs(merges: list[str], table: dict) -> None:
    for m in merges:
        p1, p2 = git("rev-parse", f"{m}^1").strip(), git("rev-parse", f"{m}^2").strip()
        base = git("merge-base", p1, p2).strip()
        changed = sorted(x for x in git("diff", "--no-renames", "--name-only", f"{base}...{p2}").split("\n") if x)
        for script in C.SCRIPTS:
            edited, header = edited_spans(script, base, p2)
            for frac in (0.0, case_sample.FRACTION):
                if header:
                    line, sel, total = f"CASES: FULL {script} -- the PR edited its header", None, None
                    e = C.entry(table, script)
                    total = sel = sum(v["seconds"] for v in e["spans"].values())
                else:
                    line, sel, total = plan_row(script, changed, edited, p2, frac, table)
                print(f"PR {m[:10]} files={len(changed)} edited_spans={len(edited)} frac={frac} "
                      f"seconds {sel:.0f} of {total:.0f} :: {line}")


def files(table: dict) -> None:
    prod = sorted(x for x in git("ls-files", "custom_components/").split("\n") if x.endswith(".py"))
    for script in C.SCRIPTS:
        for f in prod:
            line, sel, total = plan_row(script, [f], set(), "seed", 0.0, table)
            print(f"FILE {f} seconds {sel:.0f} of {total:.0f} :: {line}")


if __name__ == "__main__":
    tab = C.load()
    if tab is None:
        sys.exit("case_select_p2_measure: no table")
    if sys.argv[1:2] == ["prs"]:
        prs(sys.argv[2:], tab)
    elif sys.argv[1:2] == ["files"]:
        files(tab)
    else:
        sys.exit(__doc__)
