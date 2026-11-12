"""R10-OUTSIDE-LEARNER-ROBUSTNESS-P3's mutation proof, reproducible.

Each mutant replaces one passage of a production file in place, runs the
check that pins it -- the part's block of tests/features.py through
tools/audit/seat/features_block.py, or tests/card.mjs for the card script --
and restores the file. It prints each mutant's exit status and the names of
the checks that went red. ``M0`` is the null mutant (a comment line) and must
fail nothing; every other mutant must fail at least one check.

    python3 dev/audit/harnesses/learner_freeze_mutants.py

Run from the repository root on a clean checkout, with PYTHONPATH=tests/hastub
and tests/plan_view.py run once (tests/card.mjs reads its plan payload). The
file is restored even when a run raises.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

PKG = pathlib.Path("custom_components/heatpump_optimizer")
BLOCK = ("# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3: the frozen learner phase",)
CARD = "card"
MUTANTS = [
    ("M0-null (a comment line)", PKG / "learner_progress.py",
     "def pauses(", "# null mutant\ndef pauses(", BLOCK),
    ("M1-card-arm-removed (learnerPhase has no frozen arm)", PKG / "www/heatpump-optimizer-card.js",
     '  if (p.phase === "frozen") {', "  if (false) {", CARD),
    ("M2-frozen-below-the-weather-wait", PKG / "learner_progress.py",
     "    if frozen is not None and pauses(frozen[0]):\n"
     "        until = frozen[1].isoformat() if frozen[1] is not None else None\n"
     '        return _status("frozen", progress, frozen[0], None, n, needed, until)\n'
     "    if learner.blocked_by is not None and rate is None:\n"
     '        return _status("waiting", progress, learner.blocked_by, None, n, needed)\n',
     "    if learner.blocked_by is not None and rate is None:\n"
     '        return _status("waiting", progress, learner.blocked_by, None, n, needed)\n'
     "    if frozen is not None and pauses(frozen[0]):\n"
     "        until = frozen[1].isoformat() if frozen[1] is not None else None\n"
     '        return _status("frozen", progress, frozen[0], None, n, needed, until)\n', BLOCK),
    ("M3-end-key-outside-the-frozen-phase", PKG / "learner_progress.py",
     '    if phase == "frozen":\n        status["frozen_until"]', '    if True:\n        status["frozen_until"]', BLOCK),
    ("M4-payload-passes-no-freeze", PKG / "coordinator.py",
     "                boost.learning_freeze(self, self._learner_freeze_reason)),", "                None),", BLOCK),
    ("M5-hot-water-and-buffer-probes-pause", PKG / "learner_progress.py",
     "key not in _OTHER_PROBES", "True", BLOCK),
    ("M6-global-mode-given-an-end", PKG / "boost.py",
     "    if raw != FREEZE_REASON or _mode_live(coord):", "    if raw != FREEZE_REASON:", BLOCK),
    ("M7-skip-reason-formatted-before-the-level-check", PKG / "learner_progress.py",
     '    _LOGGER.debug("No %s sample this cycle: " + why + "%s", what, *args,',
     '    _LOGGER.debug("No %s sample this cycle: " + (why % args) + "%s", what,', BLOCK),
]


def run(target, prelude: str) -> subprocess.CompletedProcess:
    if target == CARD:
        return subprocess.run(["node", "tests/card.mjs"], capture_output=True, text=True, timeout=900)
    return subprocess.run(
        [sys.executable, "tools/audit/seat/features_block.py", "--prelude", prelude, *target],
        capture_output=True, text=True, timeout=900)


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "prelude.py"
        subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", str(out), *BLOCK],
                       check=True, capture_output=True, timeout=900)
        prelude = f"exec({out.read_text()!r})"
    status = 0
    for name, path, a, b, target in MUTANTS:
        orig = path.read_text()
        if orig.count(a) != 1:
            print(f"{name}: SITE NOT FOUND")
            status = 1
            continue
        path.write_text(orig.replace(a, b))
        try:
            r = run(target, prelude)
        finally:
            path.write_text(orig)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL")
                 and "CHECK(S) FAILED" not in ln]
        print(f"{name}: exit {r.returncode}, {len(fails)} check(s) red")
        for f in fails:
            print(f"    {f[:160]}")
        killed = r.returncode != 0 and bool(fails)
        if name.startswith("M0") == killed:
            status = 1
    print("MUTANTS: " + ("as expected" if status == 0 else "UNEXPECTED"))
    return status


if __name__ == "__main__":
    sys.exit(main())
