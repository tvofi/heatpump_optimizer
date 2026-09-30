"""R9-F2.4 mutation proof: eight mutants, each one seam of the fix restored to base.

fixer.md step 2 asks for the fix's production lines deleted, the closure run,
and the failing check names pasted. Each mutant below is one seam put back the
way it was at the merge base -- not a random operator -- and the runner is
`run_block.py`, which execs tests/features.py's own prologue plus the block
between its markers, so the checks that fail are the suite's own bytes. M4's
checks live in tests/entities.py, so its runner is that script in full.

A mutant is judged on the runner's OWN verdict -- `harness.Results.close`'s
summary line, which is the one count the suite stands behind -- and not on a
grep for failure-shaped lines: `tests/entities.py` prints other runs' `FAIL`
lines as its own evidence, 37 of them in a run whose summary is ALL 1990
PASSED. The names printed beside each verdict are this PR's own checks.

    python3 tools/audit/handoff/r9-f2-solver-4/mutation_proof.py [--only M1] \
        [--features-runner 'python3 tests/features.py']

Runs from the repository root of a COMMITTED tree: every mutant is applied
in place and restored with `git checkout --`, and the script refuses to start
on a dirty production file rather than risk restoring over uncommitted work.
Prints, per mutant, the FAIL lines and the restored tree's own verdict, then one
RESULT line per mutant with the count of checks that failed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PKG = Path("custom_components/heatpump_optimizer")
BLOCK_RUNNER = [sys.executable, "tools/audit/handoff/r9-f2-solver-4/run_block.py"]
ENTITIES_RUNNER = [sys.executable, "tests/entities.py"]

MUTANTS = [
    dict(
        id="M1",
        what="the plan's on schedule decides at half the modulation floor again",
        file=PKG / "optimizer.py",
        old="        return planned_draws_run(space_power_schedule, dhw_power_schedule)\n",
        new=(
            "        p = self.model.params\n"
            "        on_threshold = max(0.1, p.min_electrical_power * 0.5)\n"
            "        space = np.asarray(space_power_schedule, dtype=float)\n"
            "        dhw = (\n"
            "            np.zeros_like(space)\n"
            "            if dhw_power_schedule is None\n"
            "            else np.asarray(dhw_power_schedule, dtype=float)\n"
            "        )\n"
            "        return (np.maximum(space, dhw) >= on_threshold).tolist()\n"
        ),
        runner=BLOCK_RUNNER,
    ),
    dict(
        id="M2",
        what="the published action's fallback and its mode band read the meter's "
             "threshold again",
        file=PKG / "optimizer.py",
        old="            else planned_draw_runs(power, dhw_power_at_i)\n",
        new=(
            "            else power > max(\n"
            "                0.1, self.model.params.min_electrical_power * 0.5)\n"
        ),
        runner=BLOCK_RUNNER,
    ),
    dict(
        id="M2b",
        what="the action's space band reads the meter's threshold again "
             "(0.2 kW on the block's 0.4 kW plant)",
        file=PKG / "optimizer.py",
        old="        space_on = planned_draw_runs(power)\n",
        new="        space_on = power >= 0.2\n",
        runner=BLOCK_RUNNER,
    ),
    dict(
        id="M3",
        what="the arbiter's space duty reads the meter's threshold again "
             "(0.2 kW on a 0.4 kW plant, the base's caller-supplied value)",
        file=PKG / "pump_arbiter.py",
        old="    s_on = i < len(space) and planned_draw_runs(space[i])\n",
        new="    s_on = i < len(space) and space[i] >= 0.2\n",
        runner=BLOCK_RUNNER,
    ),
    dict(
        id="M4",
        what="the published power stops reading the action's own declaration",
        file=PKG / "entity.py",
        old=(
            "    if action.get(\"heat_pump_on\") is False:\n"
            "        return 0.0\n"
        ),
        new="",
        runner=ENTITIES_RUNNER,
    ),
    dict(
        id="M5",
        what="the meter's threshold loses its half-floor (the retired "
             "_on_kw CLAMP_DROP pin, on the owner now)",
        file=PKG / "thermal_model.py",
        old="    return max(MIN_RUNNING_DRAW_KW, float(params.min_electrical_power) * 0.5)\n",
        new="    return MIN_RUNNING_DRAW_KW\n",
        runner=BLOCK_RUNNER,
    ),
    dict(
        # The site the allocation-free rewrite re-anchored, and the one the
        # ledger leaves unpinned: the ratchet reads 3581 against 3583 at the
        # base, so it does not refuse, and --pin-killed's fixed cost is a
        # baseline for all 19 drivers for a single site. This is the
        # measurement that the site is killable, and by what.
        id="M6",
        what="the owner's scalar form returns nothing (the re-anchored "
             "RETURN_DEL site the ledger leaves unpinned)",
        file=PKG / "thermal_model.py",
        old="    return (float(space_kw) + float(dhw_kw)) > MIN_RUNNING_DRAW_KW\n",
        new="",
        runner=BLOCK_RUNNER,
    ),
    dict(
        # The batch form's return, re-anchored by the annotated local the typing
        # ruler's no-any-return ratchet asks for. The second of the two sites
        # this diff leaves unpinned, measured killable for the same reason.
        id="M7",
        what="the owner's batch form returns nothing (the RETURN_DEL site the "
             "annotated local re-anchored)",
        file=PKG / "thermal_model.py",
        old="    return on_steps\n",
        new="",
        runner=BLOCK_RUNNER,
    ),
]


def sh(argv: list[str]) -> tuple[int, str]:
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def summary(out: str) -> tuple[int, str]:
    """The runner's own verdict: (failed checks, the summary line).

    Read from `harness.Results.close` -- the last `ALL n <label> PASSED` or
    `k of n <label> FAILED` line -- and not by counting lines that look like
    failures. Both counts are wrong to grep for: `tests/entities.py` prints
    other runs' `FAIL` lines as its own evidence (37 of them in a run whose
    summary is ALL 1990 PASSED), and a check NAME can contain the word. The
    reporter's summary is the one number the suite itself stands behind.
    """
    line = ""
    failed = 0
    for ln in out.splitlines():
        s = ln.strip()
        if s.startswith("ALL ") and s.endswith("PASSED"):
            failed, line = 0, s
        elif " FAILED" in s and " of " in s:
            try:
                failed, line = int(s.split(" of ")[0]), s
            except ValueError:
                continue
    return failed, line


def block_fails(out: str, prefix: str = "R9-F2.4") -> set[str]:
    """The names of this PR's own checks that the runner reports as failing."""
    names = set()
    for ln in out.splitlines():
        s = ln.lstrip()
        if s.startswith("FAIL ") and s[5:].startswith(prefix):
            names.add(s[5:].split("  [")[0].strip())
    return names


def clean(path: Path) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "--", str(path)]).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    a = ap.parse_args()

    dirty = [str(m["file"]) for m in MUTANTS if not clean(m["file"])]
    if dirty:
        print(f"REFUSED: uncommitted changes in {sorted(set(dirty))}; a mutant "
              "restores with git checkout and would erase them")
        return 2

    # The healthy arm first, per runner: a mutant is judged on what it ADDS to
    # this arm's own verdict, so a red this box already has is not read as a
    # kill and a green box is not asked to be.
    selected = [m for m in MUTANTS if not a.only or m["id"] == a.only]
    healthy: dict[tuple[str, ...], tuple[int, set[str], str]] = {}
    for runner in {tuple(m["runner"]) for m in selected}:
        rc, out = sh(list(runner))
        failed, line = summary(out)
        healthy[runner] = (failed, block_fails(out), line)
        print(f"=== M0 healthy arm: {' '.join(runner)} rc={rc} failed={failed}")
        print(f"    summary: {line}")
        for ln in sorted(healthy[runner][1]):
            print(f"    pre-existing block FAIL {ln}")

    for m in MUTANTS:
        if a.only and m["id"] != a.only:
            continue
        path: Path = m["file"]
        runner = tuple(m["runner"])
        src = path.read_text()
        if m["old"] not in src:
            print(f"REFUSED {m['id']}: the line to mutate is not in {path}")
            return 2
        path.write_text(src.replace(m["old"], m["new"], 1))
        try:
            rc, out = sh(list(runner))
        finally:
            subprocess.run(["git", "checkout", "--", str(path)], check=True)
            if not clean(path):
                print(f"REFUSED {m['id']}: {path} did not restore")
                return 2
        was, was_block, _ = healthy[runner]
        failed, line = summary(out)
        added = sorted(block_fails(out) - was_block)
        print(f"\n=== {m['id']}: {m['what']}")
        print(f"    file {path}  runner {' '.join(runner)}  rc={rc}")
        print(f"    summary: {line}")
        print(f"    failed {was} -> {failed} (+{failed - was})")
        for ln in added:
            print(f"    FAIL {ln}")
        print(f"RESULT mutant[{m['id']}]_added_fails={failed - was} count")
        print(f"RESULT mutant[{m['id']}]_added_block_checks={len(added)} count")
        print(f"RESULT mutant[{m['id']}]_runner_rc={rc}")
        if failed <= was or not added:
            print(f"REFUSED {m['id']}: the suite's own verdict did not move, or "
                  "no check of this PR's went red -- the mutant survived")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
