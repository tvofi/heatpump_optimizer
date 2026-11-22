R11-ARCH-cycle-surface, a refactor group with no finding: ADR-005 parts 1 and 2 (plan/r11 at 819aa2e354b4). `boost.py` answers whether the global boost mode is live from `BoostState.mode_since`, the state `note_mode_change` is already told, and `diagnostics.py` reads the mode from the #1739 view (`CoordinatorDiagnostics.mode`, which the coordinator hands to `CoordinatorDiagnostics.of`). Neither reads `getattr(coord, "mode", ...)` any more. ADR-005 part 3 was withdrawn, so `async_shutdown` and its `self._background_tasks.clear()` are not in this diff.

A restart restored the mode in `_async_load_accuracy` without telling boost. Boost now reads only its own state, so a restart that restores the boost mode must tell it. The coordinator calls `boost.note_mode_change(self, None, stored_mode)`, where `old` `None` means a restored mode. `BoostState.note_mode(..., seen=False)` sets `mode_since` and makes `space_boosted` unknown. This keeps today's pricing: a start nobody saw owes the full tail (`settle_tail(None)`). `_restore_settle` keeps an unknown sum unknown. The boost-store and accuracy-store restores are separate spawned tasks, and without this a persisted tail restored after the mode would replace the unknown sum with the stored hours.

Alternatives not taken:
- A separate `note_mode_restored(coord, mode)` entry point. Tried at commit 2c8953a425. It is a parallel mechanism beside `note_mode_change`, and it is a coord-handed function, so it read `coord_footprint 2525 -> 2527` (inadmissible).
- Persisting `mode_since` in the boost store. The mode lives in the accuracy store. A crash between the two saves could leave boost live while the restored mode is not boost.
- Filling `CoordinatorDiagnostics.mode` from `getattr(coord, "_mode")`. With that, `name_kept_members` rose 38 -> 39: the coordinator's `mode` property was then reached only by untyped `.mode` loads, and the view's new field shares the name. Typing `of`'s receiver as the coordinator instead read `coordinator_private_reach` (structure.py) 0 -> 6. The coordinator hands the view `self.mode`, which is a bare delegation.

Scenario S25 (SCENARIOS.md at 819aa2e354b4): `boost.py` and `diagnostics.py` are no longer handed the coordinator to read its mode.

## Head

1e677d26cd48aef3e3694ca43d7cc7b2be0743f8, branched from origin/main 1207ee13b0e439a4acefccabace691785af2ebad, which was still main's tip when this body was written.

## Mutation proof

Block: `python3 tools/audit/seat/features_block.py --prelude "exec(open('<emitted prelude>').read())" "# The coordinator's mode change reaches \`\`note_mode_change\`\`" "# A hot-water charge inside a counter span"`. Each production line below was deleted on its own, then restored:
- `boost.note_mode_change(self, None, stored_mode)` in `_async_load_accuracy` removed. FAIL `a restart restoring the boost mode reads it live, and leaving it owes the unseen start's tail`, reading `{'boost': (False, None, False), ...}`. This is the failing test first: boost reads its own state, and a restart in boost read not-live.
- `self.space_boosted = None` under `if not seen:` in `BoostState.note_mode` replaced by `pass`. FAIL on both new checks (`'boost': (True, timedelta(microseconds=209), False)`, and `(NOW, timedelta(seconds=1800))`).
- `and held.space_boosted is not None` in `_restore_settle` removed. FAIL `a persisted tail restored after the boost mode keeps its boosted sum unknown` (`'boost': (NOW, timedelta(seconds=1800))`).

## Null control

- Restart test: a restart restoring auto reads not-live, with `space_boosted` `timedelta(0)` and no tail (`'auto': (False, timedelta(0), True)`). Restore-order test: with no mode restored, the stored hours restore (`'auto': (None, timedelta(seconds=1800))`).
- Score: `python3 tools/audit/archscore/score.py --diff HEAD` on an unchanged checkout of the merge base read `dS +0.0000 NULL`.
- Seam grep: `git grep -n 'getattr(coord, "mode"' -- custom_components` printed 2 lines at the merge base (`boost._mode_live`, `diagnostics._coordinator_snapshot`) and none at the head (exit 1).

## Figures

- Harness, before: the plan's `reach` arm. `$EXPORT` is a checkout of the merge base 1207ee13b0 with `$EXPORT/dev/audit/rounds/round11/PLAN/prototypes.py` (sha1 1f8fb7050661ceb0ff18abff3d27084ac7c4e19b) written into it from `git show 819aa2e354b4:dev/audit/rounds/round11/PLAN/prototypes.py`. Run from `$EXPORT`, `python3 $EXPORT/dev/audit/rounds/round11/PLAN/prototypes.py --only reach` printed `dS +1.5850 IMPROVES coordinator_private_reach 2 -> 0`.
- Harness, after: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` at the head printed `dS +1.5850 IMPROVES` and `coordinator_private_reach 2 -> 0`, with no other row moving. ADR-005's fitness functions hold: `coord_footprint`, `computed_attr_access` and `reflective_writes` are flat, and `shared_inplace_writes` is not moved.
- Class enumeration: the enumerating rule is archscore's `coordinator_private_reach` counter. It reads 0 at the head, so no seam is left. The plan's two sites are both closed in this diff.
- Structure: `python3 tests/structure.py` at the head exits 0. `class_excess_loc` 17317 -> 17315 and `max_class_loc` 7868 -> 7866 are recorded (commit 643ee512ce). The restored mode's one coordinator-class line, the view's field and its keyword are paid by three single-use `ctx = getattr(self, "_ctx", self)` locals: `_async_load_accuracy`, `_floor_widening` and `_effective_cycling_cost` now read through the typed `_ctx_of`. `_pv_export_price` was tried and not taken, because its read is an alias that the footprint does not count, and inlining it read `coord_footprint 2525 -> 2526`.
- Typing: `/opt/hpo/venv-ha/bin/python tests/typing_ruler.py --mypy` printed `ALL 9 typing-ruler checks PASSED` (errors did not grow). The `typing` job is the authority.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran those at the head: at 643ee512ce, `features.py` failed 1 of 6030: the `P3 one source` check, whose fake set a `mode` attribute that boost no longer reads. It now tells boost through `note_mode_change` (commit 489003ed75). The run hit the session's 30-minute background limit after `config_flow_steps.py`. Every script it had finished, other than `features.py`, printed `ok`. The scripts it had not reached were then run one by one, each under `PYTHONPATH=tests/hastub` (for example `python3 tests/guard_pins.py`). At 489003ed75, `features.py` passed all 6030 checks, and `deployment_shape`, `finite_boundary`, `guard_pins`, `harness_headers`, `manual_plan`, `solar_alignment`, `structure`, `typing_ruler` and `layout` exited 0. `debug_collect.py` failed 1 of 164: the private-plant census read `unplanted=['.coordinator', '.debug.diagnostics']`, because its fixture planted the mode on the coordinator's attribute. It now plants it in the published view, and at ff05d7a84e it printed `ALL 164 DEBUG COLLECT CHECKS PASSED`. That this plant reaches `.coordinator` only through `CoordinatorDiagnostics.mode` shows that diagnostics reads the view. `golden.py` is skipped under `GOLDEN_MODE=drift`, and `env_drift.py --all origin/main` printed `ok`.

## Unpinned sites

The added sites `prepr.sh` step 6d lists, with each survivor of `MUTANT_CMD` (the block named under `## Mutation proof`). All are under `custom_components/` and are pinned by `mutation-autofix`. Where this diff edited a line that main had pinned, that pin's file is deleted in commit 1e677d26cd and the old `killed_by` is named, so the lane pins the edited line afresh.
- `custom_components/heatpump_optimizer/boost.py:212 GUARD_OFF` (`BoostState.note_mode`, `if not seen:`). Killed by this block: the `self.space_boosted = None` mutant above fails both new checks. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/boost.py:369 RETURN_DEL` (`_mode_live`). Killed by this block: a `None` return reads a restart in boost as not live. Main's pin c34d5103 was killed by `tests/features.py`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/boost.py:627 CMP_BOUND*2` (`_restore_settle`, `0.0 <= hours < math.inf`), survived the block as `0.0 < hours`. The condition is unchanged and only reflowed onto its own line. Main's pin 81c29603 was killed by `tests/features.py`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:4126 RETURN_DEL` (`diagnostics_state`), survived the block. Main's pin 700af26e was killed by `tests/features.py`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:6238 BOOLOP` (`_floor_widening`; its STMT_DEL too), survived the block. Main's pin 3e0e5f0c was killed by `tests/features.py`. Pinned by mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10434 GUARD_OFF` (`_effective_cycling_cost`, `if False:`), survived the block. Main's pin 9ee6aedb was killed by `tests/features.py`. Pinned by mutation-autofix.
- `coordinator.py` STMT_DEL of the `CoordinatorDiagnostics.mode` field and of the `return cls(` in `CoordinatorDiagnostics.of`; `coordinator.py` STMT_DEL of `self._comfort_learner = ComfortLearner.from_dict(` in `_async_load_accuracy` (its argument now reads `_ctx_of(self)`); `diagnostics.py` STMT_DEL of the `snap` literal. Each survived the block, which runs no diagnostics or comfort reader. The field and `snap` are read by `tests/debug_collect.py`'s private-plant census, which failed with the plant moved off the view. Pinned by mutation-autofix.

## Red checks

- `tests / mutation` (predicted by `prepr.sh` step 6d; not yet run, because no pull request exists). The mutation lane goes red on the added sites listed under `## Unpinned sites` until `mutation-autofix` pushes their pins, and the five deleted stale pins are re-pinned the same way. The cheaper detector already exists and ran: `prepr.sh` step 6d predicted this red locally before the handoff, and it adds no standing cost beyond the `prepr.sh` run every seat makes. No further countermeasure is owed: the red is the lane's repair mechanism for a diff that edits pinned lines (`ci-autofix.md`), not a defect.

## Forward-carry

none

## Friction

none
