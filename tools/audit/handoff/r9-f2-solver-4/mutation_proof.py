"""R9-F2.4 mutation proof: five mutants, each one seam of the fix restored to base.

fixer.md step 2 asks for the fix's production lines deleted, the closure run,
and the failing check names pasted. Each mutant below is one seam put back the
way it was at the merge base -- not a random operator -- and the runner is
`run_block.py`, which execs tests/features.py's own prologue plus the block
between its markers, so the checks that fail are the suite's own bytes. M4's
checks live in tests/entities.py, so its runner is that script in full.

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
]


def sh(argv: list[str]) -> tuple[int, str]:
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def fails_of(out: str) -> set[str]:
    """The failing check names in a runner's output, without their details."""
    names = set()
    for ln in out.splitlines():
        at = ln.find("FAIL ")
        if at < 0:
            continue
        names.add(ln[at + 5:].split("  [")[0].strip())
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

    # The healthy arm first, per runner: a mutant is judged on the checks it
    # ADDS to this set, so a red this box already has is not read as a kill.
    selected = [m for m in MUTANTS if not a.only or m["id"] == a.only]
    healthy: dict[tuple[str, ...], set[str]] = {}
    for runner in {tuple(m["runner"]) for m in selected}:
        rc, out = sh(list(runner))
        healthy[runner] = fails_of(out)
        print(f"=== M0 healthy arm: {' '.join(runner)} rc={rc} "
              f"fails={len(healthy[runner])}")
        for ln in sorted(healthy[runner]):
            print(f"    pre-existing FAIL {ln}")

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
        added = sorted(fails_of(out) - healthy[runner])
        print(f"\n=== {m['id']}: {m['what']}")
        print(f"    file {path}  runner {' '.join(runner)}  rc={rc}")
        for ln in added:
            print(f"    FAIL {ln}")
        print(f"RESULT mutant[{m['id']}]_added_fails={len(added)} count")
        print(f"RESULT mutant[{m['id']}]_runner_rc={rc}")
        if not added:
            print(f"REFUSED {m['id']}: the mutant added no failing check")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
