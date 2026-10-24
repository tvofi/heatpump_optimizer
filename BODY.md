ARCH2-s2 P1 (round 10, D7): the four standing configuration notices (grid fee magnitude, grid fee sign, lower-floor modelled, comfort-band contradiction) had four coordinator flags and four hand-copied create/clear blocks. `setpoint_check.ConfigNotices` now owns the rule once: raise once per offending value, clear unconditionally. Touches only the config-notice fields in `coordinator.py`; `issues.set_issue` gains a `persistent` option. No issue closed here; Part of the ARCH2-s2 group.

Alternatives considered: the finder's patch put the create/delete calls (an `ir` import) inside `setpoint_check`; that hunk did not apply to main and the import broke `architecture.md`'s HA-boundary counts, so the owner goes through the existing `issues.set_issue`/`clear_issue` edge instead (one owner per edge, the existing mechanism). `clear_issue` is best-effort (it logs a failed delete), a small change from the bare delete.

## Head

e3be2a045e87e3248ec3b5c4ae5494e866fa6da2, on base 9586fce081411da3e552aab930919c40e2b2b233 (origin/main's tip at 2026-10-24T14:48Z, merged into the handoff branch, never rebased).

## Mutation proof

All five sites this diff adds were driven by `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4` at this head; each mutant took `tests/features.py` from rc=0 to rc=1 (the failure counts are in each pin's `reason`, under `tests/mutation_ledger/killed_by/`). The checks each mutant reds:

- `setpoint_check.py` `if offending is None:` -> `if False:` (the reload-leak defect, a clear gated on instance memory): "ConfigNotices: a fresh instance (entry reload) still clears the notice", plus the four audits' existing "corrected configuration clears" checks.
- `setpoint_check.py` `if self._raised.get(issue_id) == offending:` -> `if False:`: "ConfigNotices: the same offending value is created once, persistent WARNING" (it keys on the issue record's identity, because the stub replaces a re-created issue in place and a count cannot see a repeat).
- `issues.py` `if persistent:` -> `if False:`: the same check's `is_persistent` clause, and the existing "a stored negative rule raises the sign notice" check.
- `coordinator.py` `worst > fee_bound(currency)` -> `>=`: "fee audits: a zero fee and a fee exactly at the bound raise nothing; 1% above raises the magnitude notice".
- `coordinator.py` `lowest < 0.0` -> `<=`: the same check's zero-fee clause (a `<=` would warn every installation with a zero fee).

## Null control

The pin drive's own controls, printed by the run above: the baseline `tests/features.py` at this head rc=0 failed=0, and the comment-only null mutant `coordinator.py:510 NULL_COMMENT` survived `tests/features.py`. The unmutated head passes all three new checks (`PYTHONPATH=tests/hastub python3 tests/features.py`: ALL FEATURE CHECKS PASSED).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4`: "PIN KILLED: 5 pinned, 0 left unpinned".
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head: no unpinned site and no closures or fast red predicted.
- `python3 tools/audit/archscore/score.py --diff 9586fce081411da3e552aab930919c40e2b2b233 HEAD`: IMPROVES, from coord_footprint and coordinator_multiassigned_attrs falling; null control `--diff` of the base against itself: dS +0.0000 NULL.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at this head; the rows this diff lowered were re-recorded in the branch's first commit (`--record`, reason in its message).
- Scoped gate: `python3 tests/closure.py select --diff 9586fce081411da3e552aab930919c40e2b2b233` prints `MODE: SCOPED`; the scripts its `scope.run` names were run with `PYTHONPATH=tests/hastub`, each rc=0 (`tests/entities.py` with `BASH_ENV` unset, see Red checks).
- Finder's harness (`dev/audit/rounds/round10/D7/arch2-s2/`) was not re-executed; the architecture score above is the instrument it reads, re-run here at both ends.

## Architecture score

Architecture score: dS +0.0611 IMPROVES (coord_footprint and coordinator_multiassigned_attrs fall; no gate metric rises).

## Red checks

none on this branch. Locally `tests/entities.py` reds two checks, "gate-sweep.yml: on CI's completion ..." and "graders-head-copy's delivery_status step ...", at this head and identically in a detached worktree of origin/main at 9586fce081411da3e552aab930919c40e2b2b233. Cause: this seat exports `BASH_ENV=/etc/profile.d/hpo-toolchain.sh`, which re-prepends the venv to `PATH` inside every `bash -c`, so the stand-in `python3` those checks put first on `PATH` is shadowed by the real one. With `BASH_ENV` unset, `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head prints ALL ENTITY CHECKS PASSED, and `tools/pr/prepr.sh` was re-run the same way. Cheaper detector: none is owed by this diff, which changes no workflow or test harness.

## Forward-carry

none

## Friction

environment: cost: the seat's BASH_ENV toolchain hook shadows the stand-in python3 that two tests/entities.py workflow-step checks put on PATH, so entities.py and prepr's closures step fail on an untouched tree until BASH_ENV is unset. Carry: R10-POLICY-FIXER-MD (its carry from #2452 names this BASH_ENV shadowing)

## Unpinned sites

Re-derived at this head with `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: none. The five sites the diff adds were pinned by the local `--pin-killed` run above, each killed by `tests/features.py`:

- custom_components/heatpump_optimizer/coordinator.py `_audit_grid_fee` CMP_BOUND (the `grid_fee_magnitude` bound): pinned.
- custom_components/heatpump_optimizer/coordinator.py `_audit_grid_fee` CMP_BOUND (the `grid_fee_sign` bound): pinned.
- custom_components/heatpump_optimizer/issues.py `set_issue` GUARD_OFF (`if persistent:`): pinned.
- custom_components/heatpump_optimizer/setpoint_check.py `ConfigNotices.report` GUARD_OFF (`if offending is None:`): pinned.
- custom_components/heatpump_optimizer/setpoint_check.py `ConfigNotices.report` GUARD_OFF (`if self._raised.get(issue_id) == offending:`): pinned.
