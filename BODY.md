<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #1743 (R9-EG-B5a). `_optimize_space_only` and `_optimize_with_dhw` each built their own `_space_traj`, `objective` and `objective_batch` closures plus the four cost terms they close over (`comfort_band`, `_terminal_cost`, `_grid_terms`, `_energy_cost_fn`). `HeatPumpOptimizer._solve_objectives` now builds them once, at the same point in each path, so call order is unchanged. The DHW path passes its fixed plan as `dhw_plan_power`; with `None` the arithmetic is the space-only path's operand for operand (`combined is space_power`). A pure refactor: no plan, fixture or claim moves.

The builder keeps its own unpacking statements distinct from the two paths', and stays at or under 150 LOC, so it joins no clone class and `methods_over_150` does not move.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

dafa803ca025876621db0fb2d1f8c0ab794af3dd, the merge of origin/main 2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d (#1838) into 5a69e8744ab52dd257884fd2c036689d7ed59bb5. Measured 2026-10-02T12:00Z (`date -u`).

The merge left the production delta unchanged: `diff <(git diff 46a708150 5a69e8744 -- custom_components) <(git diff $(git merge-base origin/main HEAD)...HEAD -- custom_components) && echo CODE-DELTA-IDENTICAL` printed `CODE-DELTA-IDENTICAL`. Main changed no line of `optimizer.py` between the old base 46a70815 and 2b6c5b87. The numeric evidence below was measured at 5a69e874 against 46a70815. It was not re-run at this head, because this seat has no numpy (see Figures).

## Mutation proof

Measured at 5a69e874 by the previous seat. Two mutants of the builder, each run against `tests/features.py` (Python 3.13.14, CI's requirements):

- M1: the scalar objective's `combined` drops the DHW plan (`combined = space_power`). rc=1, 4 of 3649 failed: `every row equals the scalar objective bit for bit` and its Neumaier-grid twin, for `single-zone with-DHW, PV, capacity tariff, off-boundary start` and `two-zone with-DHW, valve, masked windows`.
- M2: the batch twin's `grid_power` drops the DHW plan (`grid_power = space_matrix`). rc=1, the same 4 checks.

At this head, main's merge touched `tests/features.py` only in the `_T6_PROPERTY_PAIRS` coordinator-property rows and `_G8DtCoord`. Neither touches the objective-parity checks that M1 and M2 fail. CI's required `features` and `mutation` checks re-run both at this head.

`mutation_table.py --scope changed --base 46a70815` reported one added unpinned site at 5a69e874, the builder's `return` (RETURN_DEL). Pinning is `mutation-autofix`'s job (`ci-autofix.md`). The four DHW-path conditional expressions that moved are not candidate sites, so no survivor sits on a touched site. It was not re-run here: its drivers import numpy.

## Null control

- Unmutated 5a69e874: `tests/features.py` passed all 3649 checks, including the six `every row equals the scalar objective bit for bit` rows that M1 and M2 fail.
- At 5a69e874: `PYTHONPATH=tests/hastub:custom_components python3 tests/env_drift.py --all 46a708150f35534344039ef0ada7f12c81c77af6` reported 37 scenarios `byte-identical` and 19 may-drift scenarios `did not move here`, printed `NO UNCLAIMED DRIFT: 56 scenario(s)`, and exited rc=0. A perturbation of the objective's DHW term would move with-DHW plans, and M1 and M2 show `features.py` sees that kind of perturbation.
- At this head: `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` is empty, so nothing is claimed.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` at dafa803c: rc=0. `git diff origin/main HEAD -- tests/structure_budgets.json` shows only the branch's three downward rows over main's re-recorded budgets: `duplication_copies`, `max_method_loc` and `methods_over_200`. The reasons are in 5a69e874's message. The merge commit's message corrects one of them: `methods_over_200` fell because `_optimize_space_only` drops under 200 LOC; `_optimize_with_dhw` stays over 200 (structure.py's monster-method listing at this head).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 23 script(s) run, 5 scoped out.`
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at dafa803c on Python 3.14.7, without numpy. These passed: `structure.py`, `typing_ruler.py` (source-only; the mypy census was not checked because `HPO_TYPING_PYTHON` was unset), `closure.py selftest`, `env_drift.py --claims-only` and `layout.py`. The other 20 failed for reasons outside the diff:
  - 17 Python scripts stopped at `ModuleNotFoundError: No module named 'numpy'`: `features`, `entities`, `doc_claims`, `wood_advisor`, `config_flow_steps`, `manual_plan`, `solar_alignment`, `guard_pins`, `finite_boundary`, `harness_headers`, `deployment_shape`, `env_drift --all`, `validate`, `edge`, `backtest`, `optimality` and `plan_view`.
  - `card.mjs` and `card_drift.mjs` failed on the missing plan payload that `plan_view.py` writes.
  - `stress.py` was not run: the run's lease label held no lease. It is left to CI's required check, which is allowed by `gate-scoping.md`.
  - CI runs all 23.

## Red checks

none

## Forward-carry

none. R9-EG-B5's brief already assumes this PR's builder: the closures stay on the optimizer, and its `_optimize_with_dhw` is the shorter one.

## Friction

- `resume.note_file`: contradiction: the roster's resume.note_file puts the seat note on the code branch (handoff/round9/fix/resume/EG-B5a.md on handoff/r9-eg-dhw-closure-dedupe), and prepr.sh's transport step refuses any handoff/ path in the code head's ancestry. The note moved to a handoff-body ref's RESUME.md, and the code head moved to handoff/r9-eg-dhw-closure-dedupe-v2, because the never-force-push rule rules out re-cutting the first branch in place.
- `fixer.step6`: cost: the Mac seat has no numpy and the hpo-ci container was deleted 2026-10-01, so after a merge that leaves the code delta byte-identical, `fixer.md` steps 2-3's numeric re-runs fall to CI.
