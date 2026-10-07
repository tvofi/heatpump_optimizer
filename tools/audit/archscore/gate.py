"""The architecture score as a required check (R9-EG-A4, #1774; tvofi's decision R3-6, 2026-09-29).

A pull request passes when the score, with the counters, reads delta-S >= 0 and no gate metric rises
between the merge base and the head. A rise passes only when the body explains it the way a budget
raise is explained: a ``## Architecture score`` section with one line per risen metric, naming it
and saying why. A negative delta-S needs a rise (every term of an admissible change is >= 0), so
explaining the rises is explaining the delta. The check reads the body; the fix reviewer judges the
reason, and a reason that only restates the number is the reviewer's to refuse.

It is never a target: the score is a review trigger, and a gain that appears only without the
counters did not happen (ABOUT.md). The weights stay at the hash ``tests/arch_score.py`` pins.

    python3 -I tools/audit/archscore/gate.py --base SHA --head SHA --body FILE
    python3 tools/audit/archscore/gate.py --self-test

``.github/workflows/arch-score.yml`` restores this directory and ``tests/structure.py`` (the
definitions the vector reads) from the base before it runs, so a pull request cannot edit the check
that grades it; a change to the instrument is graded by the base's copy and lands for the next one.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from archscore import score  # noqa: E402

HEADING = "## Architecture score"
#: An explanation line names the metric and carries at least this many characters besides.
MIN_REASON = 30


def section(body: str) -> list[str]:
    """The lines under ``## Architecture score``, up to the next level-2 heading."""
    out, inside = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            inside = line.strip() == HEADING
            continue
        if inside and line.strip():
            out.append(line.strip())
    return out


def unexplained(d: dict, body: str) -> list[str]:
    """The risen metrics no line of the section explains."""
    lines = section(body)
    missing = []
    for rise in d["rises"]:
        metric = rise.split()[0]
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(metric)}(?![A-Za-z0-9_])")
        if not any(pat.search(ln) and len(pat.sub("", ln).strip(" -*`:")) >= MIN_REASON for ln in lines):
            missing.append(rise)
    return missing


def decide(d: dict, body: str) -> tuple[bool, str]:
    if d["admissible"] and d["dS"] >= 0:
        return True, f"dS {d['dS']:+.4f} {d['verdict']}, no gate metric rose"
    missing = unexplained(d, body)
    if missing:
        return False, (f"dS {d['dS']:+.4f} {d['verdict']}; unexplained: {'; '.join(missing)}. Add a "
                       f"'{HEADING}' section with one line per metric: its name and why it rises")
    return True, f"dS {d['dS']:+.4f} {d['verdict']}; every rise explained in the body: {'; '.join(d['rises'])}"


def self_test() -> list[tuple[str, bool]]:
    """(case, passed) for the decision rule; tests/arch_score.py runs it."""
    flat = {"admissible": True, "dS": 0.0, "verdict": "NULL", "rises": []}
    up = {"admissible": False, "dS": -0.5, "verdict": "WORSENS", "rises": ["coord_footprint 10->12"]}
    why = "the extracted planner keeps its own entry point, which the footprint charges"
    sec = f"{HEADING}\n\n- `coord_footprint` 10 -> 12: {why}\n"
    cases = [
        ("an admissible change passes without a section", decide(flat, "")[0]),
        ("a rise with no section fails", not decide(up, "")[0]),
        ("a rise explained on its own line passes", decide(up, sec)[0]),
        ("a section naming another metric fails", not decide(up, sec.replace("coord_footprint", "dead_members"))[0]),
        ("a line naming the metric with no reason fails", not decide(up, f"{HEADING}\n- `coord_footprint` 10 -> 12\n")[0]),
        ("an explanation under another heading fails", not decide(up, sec.replace(HEADING, "## Figures"))[0]),
        ("a metric whose name prefixes another is not explained by it",
         not decide({**up, "rises": ["dead_members 1->2"]}, sec.replace("coord_footprint", "dead_members_v2"))[0]),
        ("two rises need two explanations",
         not decide({**up, "rises": ["coord_footprint 10->12", "dead_members 1->2"]}, sec)[0]),
    ]
    return cases


def vector_at(ref: str) -> dict:
    from archscore import vector
    with tempfile.TemporaryDirectory(prefix="archscore-gate-") as tmp:
        return vector.measure(score.tree_of(ref, Path(tmp)))


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = [name for name, ok in self_test() if not ok]
        print("\n".join(f"FAIL {n}" for n in bad) or "gate self-test: all cases pass")
        return 1 if bad else 0
    arg = {k: argv[argv.index(k) + 1] for k in ("--base", "--head", "--body") if k in argv}
    if set(arg) != {"--base", "--head", "--body"}:
        print(__doc__)
        return 2
    base = subprocess.run(["git", "-C", str(score.REPO), "merge-base", arg["--base"], arg["--head"]],
                          capture_output=True, text=True, check=True).stdout.strip()
    b, h = vector_at(base), vector_at(arg["--head"])
    d = score.delta(b, h)
    print(f"merge base {base[:12]}, head {arg['--head'][:12]}")
    print(score.report(b, h))
    if d["missing"]:
        print(f"FAIL: not measured on one side: {', '.join(d['missing'])}")
        return 1
    ok, why = decide(d, Path(arg["--body"]).read_text())
    print(("PASS: " if ok else "FAIL: ") + why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
