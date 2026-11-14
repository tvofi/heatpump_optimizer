"""R10-OUTSIDE-LEARNER-ROBUSTNESS-P2's mutation proof, reproducible.

Each mutant replaces one line of custom_components/heatpump_optimizer/boost.py
in place, runs the part's block of tests/features.py through
tools/audit/seat/features_block.py, and restores the file. It prints each
mutant's exit status and the names of the checks that went red. ``M0`` is the
null mutant (a comment edit) and must fail nothing; every other mutant must
fail at least one check or raise: either exits non-zero, and a raise
prints its last line.

    python3 dev/audit/harnesses/boost_tail_mutants.py

Run from the repository root on a clean checkout; the file is restored even
when a run raises.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

BOOST = pathlib.Path("custom_components/heatpump_optimizer/boost.py")
START = "# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)"
END = "# A hot-water charge inside a counter span (the dwell saw it)"
MUTANTS = {
    "M0-null (comment edit)": (
        "        # Unreadable boosted time reads as a start nobody saw: unknown.\n",
        "        # Unreadable boosted time reads as a start nobody saw: unknown (null mutant).\n"),
    "M1-full-tail (every sum owes the full tail, the scaling dropped; P3)": (
        "        until = utc_shift(end, settle_tail(self.space_boosted))\n",
        "        until = utc_shift(end, SPACE_SETTLE_TAIL)\n"),
    "M2-sum-dropped (each boost counted alone)": (
        "        return self.space_boosted + timedelta(seconds=max(0.0, utc_elapsed_seconds(end, since)))\n",
        "        return timedelta(seconds=max(0.0, utc_elapsed_seconds(end, since)))\n"),
    "M3-persisted-tail-dropped": (
        "    if held.space_settle_until is not None:\n        boosted = held.space_boosted\n",
        "    if False:\n        boosted = held.space_boosted\n"),
    "M4-restore-dropped": (
        "    _restore_settle(held, raw, now)\n",
        "    pass\n"),
    "M5-sum-never-clears": (
        "            self.space_settle_until, self.space_boosted = None, timedelta(0)\n",
        "            self.space_settle_until = None\n"),
    # The fix review's survivors at 594238bf, by its numbering.
    "X1-sum-cleared-under-live-overlay": (
        "                and CHANNEL_SPACE not in self.until and self.mode_since is None):\n",
        "                and self.mode_since is None):\n"),
    "X2-sum-cleared-under-live-mode": (
        "                and CHANNEL_SPACE not in self.until and self.mode_since is None):\n",
        "                and CHANNEL_SPACE not in self.until):\n"),
    "X3-start-restamped-on-extension": (
        "            if channel == CHANNEL_SPACE and not self.active(channel, now):\n",
        "            if channel == CHANNEL_SPACE:\n"),
    "X4-mode-exit-not-saved": (
        "        if old == MODE_BOOST:\n            _schedule_persist(coord)\n",
        "        if False:\n            _schedule_persist(coord)\n"),
    "X5-cycle-saves-only-on-release": (
        "    if released or held.space_settle_until != tail:\n",
        "    if released:\n"),
    "X7-tail-shortened": (
        "        if held is None or utc_elapsed_seconds(until, held) > 0:\n",
        "        if True:\n"),
    "X11-negative-sum-restored": (
        "not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)",
        "not isinstance(hours, bool) and hours < math.inf else None)"),
    "X13-mode-entry-keeps-spent-sum": (
        "        if live:\n            self._clear_spent(now)\n",
        "        if live:\n            pass\n"),
    # The ledger inventory's BOOLOP sites (``and`` to ``or``), which
    # tools/audit/seat/mutant_run.py does not draw.
    "B240-press-start-boolop": (
        "            if channel == CHANNEL_SPACE and not self.active(channel, now):\n",
        "            if channel == CHANNEL_SPACE or not self.active(channel, now):\n"),
    "B502-payload-start-boolop": (
        "    if held.space_since is not None and CHANNEL_SPACE in held.until:\n",
        "    if held.space_since is not None or CHANNEL_SPACE in held.until:\n"),
    "B549-restore-tail-boolop": (
        "    if until is not None and dt_util.as_utc(until) > dt_util.as_utc(now):\n",
        "    if until is not None or dt_util.as_utc(until) > dt_util.as_utc(now):\n"),
    "B557-restore-start-boolop": (
        "    if since is not None and CHANNEL_SPACE in held.until:\n",
        "    if since is not None or CHANNEL_SPACE in held.until:\n"),
    "B560-restore-ended-boolop": (
        "    if end is not None and CHANNEL_SPACE not in held.until:\n",
        "    if end is not None or CHANNEL_SPACE not in held.until:\n"),
}


def block(prelude: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/audit/seat/features_block.py", START, END, "--prelude", prelude],
        capture_output=True, text=True, timeout=600,
        # Two mutants of one size written inside one second would otherwise
        # share a cached .pyc: the second run would measure the first mutant.
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "prelude.py"
        subprocess.run([sys.executable, "tools/audit/seat/features_block.py", START, END,
                        "--emit-prelude", str(out)], check=True, capture_output=True, timeout=600)
        prelude = out.read_text()
    orig = BOOST.read_text()
    status = 0
    for name, (a, b) in MUTANTS.items():
        if orig.count(a) != 1:
            print(f"{name}: SITE NOT FOUND")
            status = 1
            continue
        BOOST.write_text(orig.replace(a, b))
        try:
            r = block(prelude)
        finally:
            BOOST.write_text(orig)
        fails = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL")]
        print(f"{name}: exit {r.returncode}, {len(fails)} check(s) red")
        for f in fails:
            print(f"    {f[:160]}")
        if r.returncode != 0 and not fails:
            print(f"    raised: {(r.stderr.strip().splitlines() or ['-'])[-1][:160]}")
        killed = r.returncode != 0
        if name.startswith("M0") == killed:
            status = 1
    print("MUTANTS: " + ("as expected" if status == 0 else "UNEXPECTED"))
    return status


if __name__ == "__main__":
    sys.exit(main())
