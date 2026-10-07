Fix review: blocked 4e3f09b6a7230b9fdbaad3ea6b144a82466ccc87 mutation-unpinned: quiet_windows.py:507 GUARD_OFF, added by the c3d7f89f resolution, is ADDED UNPINNED; mutation-autofix printed skip-no-measurement, so no bot pin is coming

bus-nonce: 84c76c03dd30884caa54d28882efc376

Round 7. This round judges the resolution delta since the merge verdict at `95ad5034d4e41b5440b3c08350a2964c57867a84`. Measured detached at `4e3f09b6a7230b9fdbaad3ea6b144a82466ccc87`, which the body names. Its parents are `95ad5034` and `5b1ea517a43740d0236caa35b76df21f645e8e40`. Merge base with origin/main `f060cb4c` is `59b5ac6e` (#2006). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/ tools/audit/briefs/` is empty. `VERSION` and the manifest are untouched, and both read 6.7.16 on main and on this head.

## Resolution: nothing reverted

The branch's own non-merge commits since `95ad5034` are `c3d7f89f`, `1919f631` and `347721aa`. The branch merges are `a8d2e78e`, `e36aedf6`, `e23f8712`, `5b1ea517` and `4e3f09b6`. `git merge-tree` on each merge's parents:
- `e36aedf6`, `e23f8712` and `4e3f09b6` exit 0, with a tree equal to the commit's.
- `a8d2e78e` (main `421c77f9`) conflicts in `coordinator.py` and `tests/features.py`.
- `5b1ea517` (main `59b5ac6e`, SW-6) conflicts in `tests/features.py`.

The PR's patch at `95ad5034` is `618d014f..95ad5034`. At this head it is `59b5ac6e..HEAD`. Both touch the same 91 files. In 88 of them the sorted +/- lines are identical. So neither features.py resolution dropped a line from either side, and no main change outside these three files was undone. The three that differ:
- `coordinator.py`: the PR now removes main's #1913 inline body, with predicate `silent_unenforceable(cfg, hass.states.get)`. It calls `quiet_windows.configured_specs(config, hass.states.get)` instead. Before, it removed the pre-#1913 body.
- `quiet_windows.py`: `configured_specs` takes `get_state` and calls `silent_unenforceable(config, get_state)`, main's predicate. `git diff origin/main HEAD -- quiet_windows.py` is only the branch's two added functions. Main's `silent_unenforceable` is untouched. Main's change survives where the body now lives.
- `tests/closures.json`: `debug_collect.py` gains `quiet_windows.py` and `modbus_prefill.py`. An import trace of the harness at this head loads both modules. Otherwise only `features.py`'s recorded seconds differ, which is main's own value.

The dropped `CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY` import is used neither on main nor on this head (grep counts 0 for both).

`git merge-tree --write-tree origin/main HEAD` exits 0.

## Harness at both ends

No finder harness is committed for #1939. The instrument is the fixer's `tests/debug_collect.py`, as in round 1.

RESULT debug_collect_head=30 count  (ALL 30 DEBUG COLLECT CHECKS PASSED)
RESULT debug_collect_base=import-error  (at 59b5ac6e, `debugger.py` is absent)

## Mutation proof (mine)

RESULT mutant_domain_guard=fail  (debugger.py:109 replaced with `if False:`, debug_collect 1 of 30 FAILED; restored)
RESULT mutant_guard_off_507=fail  (quiet_windows.py:507 replaced with `if False:`, manual_plan `FAIL configured_specs returns the stored rows and the not-enforced marker`; restored)
RESULT null_manual_plan=pass  (ALL 129)

`python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `env_drift.py --claims-only 59b5ac6e` printed `claims hygiene: ... ok`.

## The block

The resolution `c3d7f89f` adds the guard `if silent_unenforceable(config, get_state):` at `quiet_windows.py:507`. The mutation table records no disposition for it.

RESULT added_unpinned=1  (local `python3 tests/mutation_table.py --scope changed --base origin/main`: `MUTATION TABLE REFUSED -- 4695 unpinned site(s) against 4694 at the ratchet base 59b5ac6e..., 1 of them added by this diff`)
RESULT ci_mutation=failure  (job 112770100732, the same REFUSED line. The drive then printed `NOT RUN ...quiet_windows.py:507 GUARD_OFF -- not started: it would have overrun --budget-minutes`.)
RESULT ci_mutation_autofix=skip-no-measurement  (job 112772526098: `THE REPAIR DID NOT HAPPEN. No commit will be pushed ... Pin the new sites yourself`)

The body's `## Mutation proof` states that pinning the site is `mutation-autofix`'s job. The autofix ran on this head and reported that it did not repair the site. Under `ci-autofix.md`, a red autofix means no bot commit is coming. The site is killed: `tests/manual_plan.py` kills it, as shown above and in the body's Mutant C. So the repair is the fixer's: run `python3 tests/mutation_table.py --pin-killed --base origin/main` and commit `tests/mutation_ledger/`. The body's `## Red checks` names `mutation` for this head, but its answer is that wait, and the autofix has refuted it.

## Other checks on this head (API check-runs, 0 failed calls)

- `delivery-status` and `nightly-status`: failure. The body answers both, and they belong to main.
- `budget-raise-gate`: one run was cancelled (112770101126) and its twin succeeded (112770109433). The cancelled run needs a rerun before the merge.
- `closures`, `coverage` and `fast (3.14)`: in progress at measurement. The gate was not re-run here, because load was 255.

## Not blocking

The bare claim list on this head is `config_flow` only. Main's five R9-DIAG-2S `coord_*` claims are not in it. The patch is unchanged from `95ad5034`, which round 6 passed. Under `claim-files.md`, lines main carries from earlier merges are inert until the stamp.
