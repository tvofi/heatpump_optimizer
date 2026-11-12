#!/usr/bin/env python3
"""R10-TRAIN-REJOIN-NO-RECARRY: one mutant per new arm of merge_train.py (card 1, the
rejoin; card 5, no recarry) and remerge_main.sh's conflict diagnosis is pinned by
pr_args.sh's own `mut:remergeconflict` arm, against merge_train.py's own self-test.

    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py            # all, 4 at a time
    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py --list     # enumerate only
    python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py M0 M2      # named

Run from the branch's worktree. Each mutant replaces exactly one source span of
tools/audit/seat/merge_train.py (the span must occur exactly once, or the
mutant is reported STALE, never silently skipped), writes the result beside the
original as `_mutant_<id>.py` (so ROOT, gh_read and the tool table resolve as
for the real file), runs its `--self-test`, and prints the FAIL lines. M0 is
the unmutated file and must pass; every other mutant must fail at least one
check, else it SURVIVED. The copies are removed whatever happens.
"""

from __future__ import annotations

import concurrent.futures
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
SRC = ROOT / "tools/audit/seat/merge_train.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant

# (id, arm, the span, its replacement)
MUTANTS = [
    ("M0", "the unmutated head", "", ""),
    # Card 1: the rejoin.
    ("M1", "a rejoin fires on GREEN only, never on RED",
     "                if state == \"green\":\n                    self.log(f\"REJOIN #{pr}: GREEN",
     "                if state in (\"green\", \"red\"):\n                    self.log(f\"REJOIN #{pr}: GREEN"),
    ("M2", "the batch runs the rejoin", "                self.rejoin(rejoin, head_req)\n", "                pass\n"),
    ("M3", "only a red holding GATE is a rejoin candidate",
     "        if isinstance(s, HeadRed) and GATE in s.red:", "        if isinstance(s, HeadRed):"),
    ("M4", "the rejoin waits, bounded by the train's cap (cap 0)",
     "        cap = self.wait_cap_s()\n        while waiting:", "        cap = 0\n        while waiting:"),
    ("M5", "the rejoin's bound is the train's cap (cap x100)",
     "        cap = self.wait_cap_s()\n        while waiting:", "        cap = 100 * self.wait_cap_s()\n        while waiting:"),
    ("M6", "a head the branch moved off does not rejoin",
     "                if self.head(pr) != h:\n                    self.log(f\"REJOIN #{pr}: the head moved off",
     "                if False:\n                    self.log(f\"REJOIN #{pr}: the head moved off"),
    ("M7", "a serial rejoin candidate is queued too", "                        self.rejoin_candidate(a, s, rejoin)\n", ""),
    # Card 5: no recarry.
    ("M8", "a clean merge tree merges with no recarry (a recarry on every main move)",
     "        if not self.contains_main(h) and not self.merges_as_is(item, h):", "        if not self.contains_main(h):"),
    ("M9", "a strict or unreadable policy recarries",
     "        if item.get(\"grade_held\") or self.strict_update() is not False:", "        if item.get(\"grade_held\"):"),
    ("M10", "a merge-tree conflict recarries", "        if got is None or got[1] or self.bot_tip(h):",
     "        if got is None or self.bot_tip(h):"),
    ("M11", "a bot head recarries", "        if got is None or got[1] or self.bot_tip(h):", "        if got is None or got[1]:"),
    ("M12", "a held grade recarries",
     "        if item.get(\"grade_held\") or self.strict_update() is not False:",
     "        if self.strict_update() is not False:"),
    ("M13", "the non-recarried head is graded against its merge base (serial)",
     "        self.serial(item, h, item.get(\"nr_base\"))", "        self.serial(item, h, None)"),
    ("M14", "the non-recarried head is graded against its merge base (--overlap)",
     "                        a[\"rc_base\"] = a.get(\"nr_base\") or rb", "                        a[\"rc_base\"] = rb"),
    ("M15", "strict_update reads the policy", "        return {\"true\": True, \"false\": False}.get(o.strip()) if ok else None",
     "        return False"),
    # prepr.sh step 6d's diff-mutant survivors at 5358f7b1, killed by tests added after them.
    ("M16", "a REMERGE FAILED recarry stops as a git failure", "            if failed:  # carry f7d2bf7c",
     "            if False:  # carry f7d2bf7c"),
    ("M17", "a rejoin refused again is skipped again",
     "                        self.skip(pr, \"post-merge\" if self.is_merged(pr) else s.step, f\"#{pr} {s.why}\", s.cls)\n",
     "                        pass\n"),
    ("M18", "the rejoin sleeps between reads", "            if waiting:\n                self.hold_refresh()  # the rejoin",
     "            if False:\n                self.hold_refresh()  # the rejoin"),
    ("M19", "the rejoin's sleep is the train's poll grain",
     "                self.sleep(min(POLL_SECONDS, HEARTBEAT_SECONDS))\n\n    def skip_report", "                pass\n\n    def skip_report"),
]

def one(m: tuple[str, str, str, str]) -> tuple[str, str, list[str]]:
    mid, _arm, old, new = m
    text = SRC.read_text()
    if old and text.count(old) != 1:
        return mid, "STALE", [f"span occurs {text.count(old)} times"]
    dst = SRC.parent / f"_mutant_{mid}.py"
    try:
        dst.write_text(text.replace(old, new) if old else text)
        r = subprocess.run([sys.executable, str(dst), "--self-test"], cwd=ROOT, capture_output=True, text=True,
                           timeout=1800)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
        if mid == "M0":
            return mid, "PASS" if r.returncode == 0 and not fails else "BROKEN", fails
        return mid, "KILLED" if fails or r.returncode else "SURVIVED", fails or [f"rc {r.returncode}"]
    finally:
        dst.unlink(missing_ok=True)


def main(argv: list[str]) -> int:
    mutant_guard.arm([], scratch=[SRC.parent / f"_mutant_{m[0]}.py" for m in MUTANTS])
    if argv[:1] == ["--list"]:
        for mid, arm, _o, _n in MUTANTS:
            print(f"{mid}\t{arm}")
        return 0
    todo = [m for m in MUTANTS if not argv or m[0] in argv]
    bad = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for mid, state, fails in ex.map(one, todo):
            arm = next(a for i, a, _o, _n in MUTANTS if i == mid)
            print(f"{mid} {state}: {arm}")
            for f in fails[:4]:
                print(f"    {f[:200]}")
            bad += state not in ("PASS", "KILLED")
    print(f"MUTANTS: {len(todo)} run, {bad} not as required")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
