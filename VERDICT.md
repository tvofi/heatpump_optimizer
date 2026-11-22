Fix review: blocked 73797a573acd73668d17d0fc965d33a4b287ad8b mutation-vacuous: coordinator.py diagnostics_state CoordinatorDiagnostics.of(self, self.mode) to of(self) survives debug_collect.py and entities.py

bus-nonce: ee4ae5037aa36ae8d829ca3ba2888617

Round: first (no earlier verdict on this PR).

## Block

- `custom_components/heatpump_optimizer/coordinator.py:4126` (`diagnostics_state`): the mutant `CoordinatorDiagnostics.of(self, self.mode)` -> `CoordinatorDiagnostics.of(self)` (the view's `mode` always `None`, so every diagnostics download reports `"mode": None`) survives `tests/debug_collect.py` (ALL 164 PASSED) and `tests/entities.py` (ALL 2761 ENTITY CHECKS PASSED). No check in `tests/features.py` reads the diagnostics snapshot's `mode` (its `_coordinator_snapshot` checks read learner summaries, `pump_duty` and `cop_learner`); `entities.py:27043` checks only that the key `mode` is present. At the base, the same regression (diagnostics losing the mode) was killed by `debug_collect.py`'s private-plant census, which planted `coord.mode`; this diff moves that plant to `coord.diagnostics_state = lambda: CoordinatorDiagnostics(mode=...)` (`tests/debug_collect.py:1543`), which replaces the coordinator's own `diagnostics_state` and so bypasses the line that hands the mode. The body's claim "this plant reaches `.coordinator` only through `CoordinatorDiagnostics.mode`" holds for the `diagnostics.py` side (M7 below is killed) and pins nothing on the coordinator side. Owed: a check driving a real coordinator's `diagnostics_state()` (or `_coordinator_snapshot` of a real coordinator) that asserts the reported mode equals the coordinator's mode, with a null control (a second mode value) and the M8 mutant shown failing it.

## Evidence

- Head measured: 73797a573acd73668d17d0fc965d33a4b287ad8b (`ev/HEAD.txt`); the PR body's `## Head` names the same SHA.
- Merge with main: `git merge-tree --write-tree origin/main 73797a5` exit 0; origin/main e3cb5c019b is the merge base (head is not behind main) (`ev/merge-tree.txt`).
- Role files current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.
- Mutation proof of the boost half, re-run on the body's block (`ev/mutants.txt`): M1 (drop the restore's `note_mode_change`) 1 of 3 FAILED; M2 (`space_boosted = None` -> `pass`) 2 of 3 FAILED; M3 (drop `and held.space_boosted is not None`) 1 of 3 FAILED; M4 (`seen=True` always) 2 of 3 FAILED. The body's three mutants reproduce with its quoted readings.
- `_mode_live` reverted to `getattr(coord, "mode", None) == MODE_BOOST` (M5) passes the body's block, because its fakes carry `.mode`; the P3 block kills it (1 of 4 FAILED), as does `return False` (M6).
- `diagnostics.py` reverted to `getattr(coord, "mode", None)` (M7): `debug_collect.py` 1 of 164 FAILED, the private-plant census (`unplanted=['.coordinator', '.debug.diagnostics']`).
- M8 (the block above): `debug_collect.py` ALL 164 PASSED; `entities.py` ALL 2761 PASSED (`ev/dc_M8-view-no-mode.tail.txt`, `ev/entities_M8.tail.txt`). The indented `FAIL a3:`/`a16:` lines in those logs are the scripts' own planted negative controls and appear identically at the head (`ev/dc_head.tail.txt`).
- Mode-write enumeration: the operation mode is written at three places in `custom_components/` (`git grep` of `_mode =` assignments): `__init__` (`MODE_AUTO`, consistent with `mode_since None`), `async_set_mode` (calls `note_mode_change(self, self._mode, mode)`), `_async_load_accuracy` (now calls `note_mode_change(self, None, stored_mode)`). Every write reaches boost; `BoostState` is mutated in place by `restore`, never replaced, so the two restore orders both hold (pinned by the restore-order check).
- Pricing equivalence: a restored boost previously had `mode_since None`, so leaving it priced `settle(now, None)` -> `_boosted_with` `None` -> the full tail; now `mode_since=now` with `space_boosted None` gives the same `None` sum and the same full tail.
- Harness: archscore `python3 tools/audit/archscore/score.py --diff e3cb5c019b` at the head printed `Architecture score: dS +1.5850 IMPROVES` with `coordinator_private_reach 2 -> 0`, no other row (`ev/archscore.txt`). Seam grep `git grep -n 'getattr(coord, "mode"' -- custom_components` returns 2 lines at e3cb5c019b (`boost.py:361`, `diagnostics.py:342`) and none at the head.
- Structure: `python3 tests/structure.py` exit 0, `class_excess_loc 17315 <= 17315`, `max_class_loc 7866 <= 7866` (`ev/structure.txt`). The budgets only move down; the payment (three single-use `ctx = getattr(self, "_ctx", self)` locals read through `_ctx_of`, whose body is `getattr(coord, "_ctx", coord)`) is behaviour-identical and a real simplification, not instrument gaming.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/` and both claim files untouched in the three-dot diff. `env_drift.py --all` was not completed here (stopped because it captures from the working tree while a mutant was applied there); CI's run is the authority.
- CI at this head: `merge_train.py classify ... --pr 3873` printed `WAIT 73797a573acd73668d17d0fc965d33a4b287ad8b pending: gate red: none` on every poll from 21:38 to the verdict (`ev/classify.log`); most lanes were queued at 21:56. No red to answer.

## Findings

- The body's `## Unpinned sites` names `tests/features.py` as the old `killed_by` of pins 700af26e (`diagnostics_state`) and 3e0e5f0c (`_floor_widening`); the deleted ledger files say `tests/entities.py` for both. Carry: dismissed: body figure in this PR, corrected in the re-cut this block already requires
