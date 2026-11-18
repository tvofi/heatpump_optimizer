#!/usr/bin/env python3
"""R10-HOTFIX-DELTA-REVIEW: one mutant per new arm of the later-round delta scope
(review_packet.py's review_scope, previous_verdict, scope_facts and scope_parts;
bus.sh dispatch's hand-on to the renderer; cloud_dispatch.py's reviewer render),
each run against the mutated file's own self-test.

    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py            # all, one at a time
    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py --list     # enumerate only
    python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py M0 M2      # named

Run from the branch's worktree on a clean tree. Each mutant replaces exactly
one span of one file in place (a span that does not occur exactly once is
STALE, never silently skipped), runs that file's `--self-test`, prints the FAIL
lines and restores the file; mutant_guard restores every file on a kill. M0 is
the unmutated tree and must pass; every other mutant must fail at least one
check, else it SURVIVED. Serial, because the mutants share files.
"""

from __future__ import annotations

import subprocess
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant

PACKET = "tools/audit/seat/review_packet.py"
BUS = "tools/audit/seat/bus.sh"
CLOUD = "tools/audit/seat/cloud_dispatch.py"
RUN = {PACKET: [sys.executable, "-I", PACKET, "--self-test"], BUS: ["bash", BUS, "--self-test"],
       CLOUD: [sys.executable, "-I", CLOUD, "--self-test"]}

# (id, arm, file, the span, its replacement)
MUTANTS = [
    ("M0", "the unmutated head", PACKET, "", ""),
    ("M1", "a later round's diff is `git diff <rh> <head>`", PACKET,
     '"diff": git("diff", rh, head) if delta else git("diff", f"{base}...{head}")}',
     '"diff": git("diff", f"{base}...{head}")}'),
    ("M2", "the packet renders the delta and the previous verdict", PACKET,
     '    if kind == "delta":\n        rh = facts["reviewed_head"]', '    if False:\n        rh = facts["reviewed_head"]'),
    ("M3", "a reviewed head that is not the head's ancestor keeps the full diff", PACKET,
     "    if not is_anc(rh, head):\n", "    if False:\n"),
    ("M4", "the previous verdict is the one naming the reviewed head", PACKET,
     "        if v and v[1] == rh:", "        if v:"),
    ("M5", "bus.sh dispatch hands the renderer --reviewed-head", BUS,
     ' ${rh:+--reviewed-head "$rh"} ', " "),
    ("M7", "the packet's scope line carries the exception's production-code qualifier", PACKET,
     '(custom_components/) puts at risk', 'puts at risk'),
    ("M8", "the packet's scope line states a wider trigger", PACKET,
     'never "\n                "justifies a wider review', 'never "\n                "justifies a wider review, or in full on code that review relied on'),
    ("M6", "the cloud reviewer renders its packet with --reviewed-head", CLOUD,
     '+ (f"--reviewed-head {reviewed_head} " if reviewed_head else "") +', "+"),
]


def one(m: tuple[str, str, str, str, str]) -> tuple[str, str, list[str]]:
    mid, _arm, rel, old, new = m
    src = ROOT / rel
    text = src.read_text()
    if old and text.count(old) != 1:
        return mid, "STALE", [f"span occurs {text.count(old)} times in {rel}"]
    try:
        src.write_text(text.replace(old, new) if old else text)
        cmds = list(RUN.values()) if mid == "M0" else [RUN[rel]]
        rcs, fails = [], []
        for cmd in cmds:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
            rcs.append(r.returncode)
            fails += [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
    finally:
        src.write_text(text)
    if mid == "M0":
        return mid, "PASS" if not any(rcs) and not fails else "BROKEN", fails
    return mid, "KILLED" if fails or any(rcs) else "SURVIVED", fails or [f"rc {rcs}"]


def main(argv: list[str]) -> int:
    mutant_guard.arm([PACKET, BUS, CLOUD])
    if argv[:1] == ["--list"]:
        for mid, arm, rel, _o, _n in MUTANTS:
            print(f"{mid}\t{rel}\t{arm}")
        return 0
    todo = [m for m in MUTANTS if not argv or m[0] in argv]
    bad = 0
    for m in todo:
        mid, state, fails = one(m)
        print(f"{mid} {state}: {m[1]}")
        for f in fails[:4]:
            print(f"    {f[:200]}")
        bad += state not in ("PASS", "KILLED")
    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
