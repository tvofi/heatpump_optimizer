<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVHrr7pT5nAFauRCXWPCTRX3)_

Part of #1743 (R9-EG-B5a). `_optimize_space_only` and `_optimize_with_dhw` each built their own `_space_traj`, `objective` and `objective_batch` closures plus the four cost terms they close over (`comfort_band`, `_terminal_cost`, `_grid_terms`, `_energy_cost_fn`). `HeatPumpOptimizer._solve_objectives` now builds them once, at the same point in each path, so call order is unchanged. The DHW path passes its fixed plan as `dhw_plan_power`; with `None` the arithmetic is the space-only path's operand for operand (`combined is space_power`). A pure refactor: no plan, fixture or claim moves.

The builder keeps its own unpacking statements distinct from the two paths', and stays at or under 150 LOC, so it joins no clone class and `methods_over_150` does not move.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_014mDh6skwPhwdk5zLQAQP4K

## Head

DRAFT: re-measured after #1838 merges and origin/main is merged in. Figures below are at 5a69e8744ab52dd257884fd2c036689d7ed59bb5 against its parent 46a708150f35534344039ef0ada7f12c81c77af6 (#1838's head).

## Mutation proof

Two mutants of the builder, each run against `tests/features.py` (Python 3.13.14, the CI requirements):

- M1: the scalar objective's `combined` drops the DHW plan (`combined = space_power`). rc=1, 4 of 3649 failed: `every row equals the scalar objective bit for bit` and its Neumaier-grid twin, for `single-zone with-DHW, PV, capacity tariff, off-boundary start` and `two-zone with-DHW, valve, masked windows`.
- M2: the batch twin's `grid_power` drops the DHW plan (`grid_power = space_matrix`). rc=1, the same 4 checks.

`mutation_table.py --scope changed --base 46a70815` reports one added unpinned site, the builder's `return` (RETURN_DEL). Pinning is `mutation-autofix`'s (`ci-autofix.md`). The four DHW-path conditional expressions that moved are not candidate sites, so no survivor sits on a touched site.

## Null control

- Unmutated head: `tests/features.py` passes all 3649 checks, including the six `every row equals the scalar objective bit for bit` rows that M1 and M2 fail.
- `PYTHONPATH=tests/hastub:custom_components python3 tests/env_drift.py --all 46a708150f35534344039ef0ada7f12c81c77af6`: 37 scenarios `byte-identical`, 19 may-drift scenarios `did not move here`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, rc=0. A perturbation of the objective's DHW term would move with-DHW plans. M1 and M2 show that kind of perturbation is visible to `features.py`.
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` is empty, so nothing is claimed.

## Figures

- `python3 tests/structure.py` at the head against `--record` at the parent. Three rows moved down and were re-recorded with the reason in commit 5a69e874's message:
  - `duplication_copies`: the two `objective` closures were one clone class, and it is gone.
  - `max_method_loc`: `_optimize_with_dhw` falls below `sysid.identify`.
  - `methods_over_200`: `_optimize_space_only` drops under 200. Correction to 5a69e874's message, which named `_optimize_with_dhw`; that method stays over 200.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` printed `MODE: SCOPED -- 24 script(s) run, 4 scoped out`. On Python 3.11, 21 passed. `tests/entities.py`, `tests/harness_headers.py` and `tests/stress.py` failed on 3.11 at the base's own 3.12-only syntax (PEP 701 f-strings) and `sys.monitoring`. Re-run on 3.13.14, all three passed at rc=0.

## Red checks

none

## Forward-carry

none. R9-EG-B5's brief already assumes this PR's builder: the closures stay on the optimizer, and its `_optimize_with_dhw` is the shorter one.

## Friction

- `resume.note_file`: contradiction: the roster's resume.note_file puts the seat note on the code branch (handoff/round9/fix/resume/EG-B5a.md on handoff/r9-eg-dhw-closure-dedupe), and prepr.sh's transport step refuses any handoff/ path in the code head's ancestry. The note moved to handoff-body/<topic>'s RESUME.md, and the code head moved to handoff/r9-eg-dhw-closure-dedupe-v2, because the never-force-push rule rules out re-cutting the first branch in place.
