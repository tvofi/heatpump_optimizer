R10-ARBITER-OFF-RESTORE: turning the optimizer off, and every unload, restores the pump arbiter's space set-point to the person's baseline, under the owner's ruling (tvofi, #201 comment 6708225978, 2026-11-07, "Arbiter too"), which retracts the 2026-09-26 "off writes nothing" ruling for that slot. Stacked on R10-GENERIC-HEAT-CURVE-PERSISTENT's handoff (owner ruling 2026-11-10, "Yes on 1 and 2"); see `## Head`. No finding, no issue to close, no finder harness: the build is the owner's ruling.

**What changed** (only `pump_arbiter.py` in production; the off_restore hook is consumed as built, unedited).
- The space set-point is an off_restore consumer, key `pump_arbiter_space`: `Restorer(space_setpoint_entity, write_setpoint_c, baseline_of=read_setpoint, restored=_space_restored)`, the writer registered for rule R. Baseline and restore are both degC through the one read/write pair `inputs.py` owns, so a restored value reads back as itself. Off and unload restore it through the hook's existing `async_mode_change` and `async_unload_entry` call sites: no second owner of either path.
- `_write` arms before every space write (`_held_back`, which also takes `_write`'s retry and read-only-mode guards, unchanged). `_arm_space` refuses a first capture whose reading equals the arbiter's own last write (`ArbiterState.written`, the existing persisted ownership record; no second record), latched once per entity, and holds the write until the controller reads anything else.
- A person's edit between writes becomes the baseline (`_adopt` / `_edited`, read before `hold` rewrites it). It is adopted only when the reading differs from the arbiter's write after `ECHO_GRACE_S`, on the first miss, and differs from the reading when that write was sent (`ArbiterState.space_before`: a refused write falls back to that). `space_before` is unknown after a restart and is reset while the power switch reads off, so the pump's own reset on power-up is never adopted. The hold itself is unchanged: while active, the edit is still written over.
- A person's value set while the optimizer is off is captured at the next arm, because a successful restore disarms the key (hook behaviour).
- `release` (unload) writes the fallback row without the space set-point, since the restore has written its baseline first, and saves the record. `_space_restored` drops the slot from the arbiter's record. The Off pass saves that drop (`_forget` now also clears `space_before`).
- Docs: `docs/configuration.md` (Pump duty control: rails, hold, the new restore bullet) and the module docstring.

**The brief's carries, each answered.**
- Carry 1 (73eb63bd): the space set-point is a consumer registered with `register_consumer` that arms before every space write. Nothing here owns the unload, MODE_OFF or remove path; `off_restore.py` and `__init__.py` are unedited.
- Carry 2 (a94cb8b6), entity keying of the armed record: the consumer's baseline entry records its entity, so rule R restores a changed entity to its own value. `_space_restored` drops the arbiter's own record on any restore of its key.
- Carry 3 (0a8663d2): the `restored` callback is `_space_restored`. It keeps the arbiter's write record honest after a restore: the slot is dropped, then saved by the Off pass or the release (M09 to M11).
- Carry 4 (8755bcb3): consumed as built, through `register_consumer`, `Restorer(..., baseline_of=, restored=)`, `async_arm`, `async_armed_entry` and `async_rebaseline`. The baseline consumer keeps no class attribute named `state`.
- Carry 5 (76ae476a) and Carry 6 (2bcac34a): the reserve rule binds a consumer that budgets writes, and the arbiter budgets none (`## Forward-carry`).
- Carry 7 (the 2026-11-10 stacking ruling): built on `handoff/r10-generic-heat-curve-persistent` (`## Head`). WSF has not landed, so `ArbiterState.written` is the one write record, and the own-write refusal reads it.

**Departure from the brief, for the reviewer.** The brief restores "on unload while Home Assistant is not stopping"; the hook as built restores on every unload, a stop included (`off_restore.py` module docstring, "Home Assistant stopping changes nothing"; `__init__.py`'s unload comment). A per-consumer stop rule would need an edit of the hook, which carry 73eb63bd forbids ("never a second owner of the unload"), so this consumer follows the hook. The docs say so. The cost on a stop is one restore write, then one capture and one rewrite at the next start.

## Head

`0d5c11241db30df60ee4fed97c6135f757f7b0f0`. It is stacked on R10-GENERIC-HEAT-CURVE-PERSISTENT's handoff: built on `f483180ffa75b0eb464666f359ed2c9bad22532b`, then merged with that handoff's newer tip `9e4ad065c7ca248008de7d65d943f0b3c02d32b3` (`handoff/r10-generic-heat-curve-persistent`, its own merge of main `1cabb845d` and its two pin commits). That merge was forced because `git merge-tree --write-tree origin/main HEAD` reported conflicts in `translations/de.json` and the card. Both conflicts are on the predecessor's lines, which the new tip resolves; its `off_restore.py`, `pump_arbiter.py` and `__init__.py` are byte-identical to `f483180ff` (`git diff --stat f483180ff 9e4ad065c -- <those files>` prints nothing). Until that group's pull request lands, this pull request shows its diff too; then origin/main is merged in so it carries only this group's diff. R10-WATER-SETPOINT-FEEDBACK has not landed (`handoff-wip` only), so there is no WSF write record to reuse; `ArbiterState.written` is the record (Carry 7). `git merge-tree --write-tree origin/main HEAD` exits 0 at origin/main `2cf0f129bc8cfac6cf38005dfda4c2930353f7cd`. Every figure below is this group's own diff, measured against `9e4ad065c` at `0d5c11241db30df60ee4fed97c6135f757f7b0f0` unless named; the failing-first run and the first build's ratchet and score readings were taken against `f483180ff`, whose arbiter and hook files are the same.

## Mutation proof

Failing test first: the new checks, run with `pump_arbiter.py` at `f483180ff` and the tests at the head, fail `5 of 47 FEATURES BLOCK FAILED` (every R10-ARBITER-OFF-RESTORE check at that commit), first "R10-ARBITER-OFF-RESTORE: switching the optimizer off writes the space set-point's baseline back ...", with `_pa_ro_sent=0`. At the fix they pass.

Sixteen named mutants of the lines this diff adds, each applied alone to a `git archive` copy and driven by the pump-duty arbiter block of `tests/features.py` (`dev/audit/harnesses/r10_arbiter_off_restore_mutants.py`, which holds the spec; NULL survives, every mutant is KILLED). For each mutant: what it changes, then the number of failed checks, then the first one:
- M01 `register_consumer` deleted: 16; "a hot-water-only step writes DHW only, the configured hot-water set-point and the space gate" (no consumer, no arm, no space write).
- M02 `_held_back` never arms: 8; "... switching the optimizer off writes the space set-point's baseline back ...".
- M03 the own-write refusal off: 1; "... a reading equal to the arbiter's own last write is never captured ...".
- M04 the before-write comparison dropped: 1; "... a space set-point a person sets between writes becomes the baseline ...".
- M05 the first-miss condition dropped: 1; "... a second differing reading is a write the pump does not take ...".
- M06 power-off does not forget `space_before`: 1; "... between writes ..." (its power-off null control).
- M07 no `async_rebaseline`: 2; "... between writes ...".
- M08 release writes the space set-point: 1; "... unloading restores the space baseline and the release writes the fallback row without the space set-point over it".
- M09 `_space_restored` keeps the record: 1; "... after an off or an unload restored a baseline equal to the plan's value, a restart captures it again ...".
- M10 release does not save: 1; same check (unload arm).
- M11 the Off pass does not save on `space_before`: 1; same check (off arm).
- M12 no echo grace: 1; "... a reading inside the echo grace, and one that holds the write, are no edit ...".
- M13 `_forget` keeps `space_before`: 1; "... switching the optimizer off ..." (its record is saved on every later Off pass).
- M14 the factory answers None: 16; as M01.
- M15 `_adopt` skipped: 2; "... between writes ...".
- M16 the written-value comparison dropped: 2; "... between writes ..." and "... echo grace ... holds the write ...".

## Null control

- With the arbiter not controlling (`pump_duty_mode` observe), off writes nothing and the hook sends 0: the first new check's second arm (`_pa_ro_null_sent == 0`, `writes() == []`). With no space entity, `_restorer` answers None, and M14 shows that path writes no space value.
- Every pre-existing arbiter check passes unchanged, the "off writes nothing" ones included (`tests/features.py` "switching the optimizer off writes nothing, not even the baseline", "unloading with the optimizer off writes nothing"). Those set `_mode` directly, so they never call the hook. The new checks drive the hook's own `async_mode_change` / `async_restore`, as the coordinator does.
- The adoption arms each carry their non-edit twin: the value before the write; a power cycle; a second miss; within the grace; a held write.

## Figures

At `9c37f926082963d4d1a93fe0830ddfaae6fd3bab` unless named.
- Failing first: `5 of 47 FEATURES BLOCK FAILED` with `pump_arbiter.py` from `f483180ff` (that file checked out over a `git archive` copy of the head), and `ALL 50 FEATURES BLOCK PASSED` at the head: `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "R.section(\"pump-duty arbiter — mode and set-points per plan step" "_pa_subs = _PaCoord("` (the base run was taken before the two later checks existed: 47 then, 50 now).
- Mutants: `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py`: `SURVIVED NULL`, then `KILLED` for M01 to M16, exit 0. Each mutant's failed-check count above comes from the same block, mutant by mutant.
- Scoped gate: `python3 tests/closure.py select --diff 9e4ad065c7ca248008de7d65d943f0b3c02d32b3 --workdir $D` prints `MODE: SCOPED`; every script `scope.run` names was run with `PYTHONPATH=tests/hastub` and `GOLDEN_MODE=drift` (`tests/features.py`: `ALL ... FEATURE CHECKS PASSED`; the rest exit 0). Against origin/main the scope is the stacked predecessor's too: `MODE: SCOPED`.
- Ratchet: `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. The first build put `_write` at CC 16 and `functions_cc_over_15` one over; paid by moving `_write`'s retry and read-only-mode guards with the new arm into `_held_back`. No budget is re-recorded.
- Score: `python3 tools/audit/archscore/score.py --diff 9e4ad065c7ca248008de7d65d943f0b3c02d32b3`: `IMPROVES`. The first build read `coord_footprint` up (`WORSENS`); the new logic now sits in functions handed the entry, the inputs and the arbiter record, not the coordinator (`_held_back`, `_arm_space`, `_adopt`, `_edited`). The remaining delta is `_write`'s guards moving out.
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted against 1cabb845d617`, and `16 unpinned site(s)`, all this group's (below). Seven ledger pins whose lines this diff rewrote are deleted (`_arbitrate` cac4451e, deac2794; `_pump_off` dfd29811; `_write` 2f54ce51 and 92b8766d, BOOLOP and GUARD_OFF); `--apply-inert` classified the new harness.
- Class seams (fixer.md step 8). The rule is every call that writes a degC set-point: `git grep -n "write_setpoint_c(" custom_components/heatpump_optimizer/`. It returns two call sites. `pump_arbiter._write`, the space slot's one writer, is armed in this diff, and `release`, its only other route, excludes the space slot. `coordinator._valve_write_problem` writes the valve, another entity, which is not this ruling's. The restore's own write is the function registered with the hook, not a call site. The heat curve's `write_setpoint` writes its own entity and is already the hook's consumer.

## Unpinned sites

Each site below is owed to `mutation-autofix`, whose lane mutates `custom_components/`; none is pinned in-tree here (`unmeasured` until that job runs, `ci-autofix.md`). The named mutants under `## Mutation proof` kill the behaviour each carries.
- custom_components/heatpump_optimizer/pump_arbiter.py:1102 CMP_BOUND: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1150 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1172 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1182 BOOLOP: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1182 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1184 BOOLOP: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1184 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1186 BOOLOP: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1186 RETURN_DEL: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1209 RETURN_DEL: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1323 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1336 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1506 RETURN_DEL: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1522 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1620 GUARD_OFF: mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1634 GUARD_OFF: mutation-autofix

## Red checks

No CI check has run on this branch. Its commits went only to `handoff-wip/r10-arbiter-off-restore`, which runs no job, and the orchestrator opens the pull request.
- `tests / mutation`: predicted red, ADDED UNPINNED on the 16 sites under `## Unpinned sites`, which `mutation-autofix` pins once the pull request exists (`ci-autofix.md`: wait for its commit). Cheaper detector: `python3 tools/pr/ci_predict.py`, run here before the handoff, which lists the same sites; no cheaper one exists. Pinning in-tree costs `tests/features.py` a full run per mutant.
- `ledger`: STALE PIN on the seven pins this diff's lines moved (`_arbitrate` cac4451e and deac2794; `_pump_off` dfd29811; `_write` 2f54ce51 and 92b8766d), predicted at the first build. Repaired here by deleting the pin files, as `ci_predict.py` prescribes. It now predicts no closures, fast, governance or instrument red against `1cabb845d`.
- Local reds this seat met and repaired, each on the script itself in the scoped gate: `tests/structure.py` `functions_cc_over_15` (`_write` CC 16; paid, see `## Figures`); `tests/features.py` and `tests/guard_pins.py`, a `TypeError` from off_restore's weak entry key on `SimpleNamespace` fixtures (`## Friction`); `tests/guard_pins.py`, a bare `_write` driver with no entry. None reached CI.
- `tests / coverage-ratchet`: red in this branch's ancestry on a #3299 commit (`off_restore.py` under 95 % there), not on a commit of this group. It was covered there and answered in #3299's body and R10-GENERIC-HEAT-CURVE-PERSISTENT's body. That cheaper detector, a `coverage run` of the module's driver, is not in prepr. This diff adds no module. Other earlier reds in the predecessor's commits are answered in those two bodies, and none is on a commit of this group.

## Forward-carry

- R10-WATER-SETPOINT-FEEDBACK goes before this group on `pump_arbiter.py`. The arbiter's space write record is now `ArbiterState.written["space_setpoint"]` plus `ArbiterState.space_before`, read by `_arm_space` (the own-write refusal) and `_edited` (edit adoption). Precondition for WSF: a record WSF adds for the space write extends these two fields rather than adding a second; if it adds one, this group's two readers move onto it. Control: M03 and M04/M16 here go red if the record they read stops being written. Carry: R10-WATER-SETPOINT-FEEDBACK
- The reserve-rule carries (76ae476a, 2bcac34a) bind a consumer that budgets writes. The arbiter has no per-day write cap (`_write` has no counter; `hold` retries every `RETRY_MINUTES`), so nothing here owes the restore a reserved write. Carry: dismissed: the arbiter budgets no writes
- Entity keying (a94cb8b6, 0a8663d2) is met by the hook's rule R plus `_space_restored`, which drops the arbiter's own record on any restore of its key. Carry: dismissed: built here

## Friction

- brief-stop-restore: contradiction: the brief restores "on unload while Home Assistant is not stopping", while the hook it must reuse (carry 73eb63bd, never a second owner of the unload) restores on every unload, a stop included (`off_restore.py` docstring). Built to the hook. Carry: dismissed: the departure is raised in the body for the reviewer; a stop-exempt restore would be a change to the hook, R10-GENERIC-HEAT-CURVE's seam
- fixture-weakref: cost: off_restore keys its record weakly on the config entry, so three arbiter test fixtures that used a `SimpleNamespace` entry (`tests/features.py` `_PaCoord`, `_df_write`, `_CpArb`; `tests/guard_pins.py`) raised `TypeError` on the first space write. They now use the harness `FakeEntry`; a real `ConfigEntry` is weak-referenceable. Carry: dismissed: repaired here
