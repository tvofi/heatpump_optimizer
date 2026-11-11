R10-ARBITER-OFF-RESTORE: turning the optimizer off, and every unload, restores the pump arbiter's space set-point to the person's baseline, under the owner's ruling (tvofi, #201 comment 6708225978, 2026-11-07, "Arbiter too"), which retracts the 2026-09-26 "off writes nothing" ruling for that slot. No finding, no issue to close, no finder harness: the build is the owner's ruling.

**What changed** (only `pump_arbiter.py` in production; the off_restore hook is consumed as built, unedited).
- The space set-point is an off_restore consumer, key `pump_arbiter_space`: `Restorer(space_setpoint_entity, write_setpoint_c, baseline_of=read_setpoint, restored=_space_restored)`, the writer registered for rule R. Off and unload restore it through the hook's existing `async_mode_change` and `async_unload_entry` call sites: no second owner of either path.
- `_write` arms before every space write (`_held_back`, which also takes `_write`'s retry and read-only-mode guards, unchanged), so the baseline is on disk before the write is sent. `_arm_space` refuses a first capture whose reading equals the arbiter's own last write (`ArbiterState.written`, the existing persisted record; no second record), latched once per entity, and holds the write until the controller reads anything else.
- A person's edit between writes becomes the baseline (`_adopt` / `_edited`, read before `hold` rewrites it), bounded to the entity's own range and step (`_bounded`, the arbiter's existing clamp), so off writes back a value the entity takes. It is adopted only when the reading differs from the arbiter's write once `ECHO_GRACE_S` has passed, on the first miss, and differs from the reading when that write was sent (`ArbiterState.space_before`). `space_before` is unknown after a restart and reset while the power switch reads off, so the pump's own reset on power-up is never adopted. While active, the edit is still written over.
- A value set while the optimizer is off is captured at the next arm, because a successful restore disarms the key (hook behaviour).
- `release` (unload) writes the fallback row without the space set-point and saves the record; `_space_restored` drops the slot from the arbiter's record; the Off pass saves that drop.
- Docs: `docs/configuration.md` (Pump duty control) and the module docstring.

**Repair round 1** (dispatch at PR head `a57d1fe92223f8e53c908613eef5a494b9404d63`, continued, not re-cut). Built: the range bound at adoption (Carry 11), a check observing the write-ahead order (Carry 10), and checks killing the two sites `tests / mutation` refused (`_edited`'s `>= ECHO_GRACE_S`, `_restorer`'s no-entity guard). Mutants M17 to M20 added to the harness; M07 re-anchored on the rewritten `_adopt` line.

**The roster's carries, `Carry N` being roster index N-1 ( `origin/handoff/audit-r10-roster`, group R10-ARBITER-OFF-RESTORE, field `carry`).**
- Carry 1 (73eb63bd): met. The space set-point is a `register_consumer` consumer that arms before every space write; `off_restore.py` and `__init__.py` are unedited.
- Carry 2 (a94cb8b6) and Carry 3 (0a8663d2), entity keying: met. The baseline entry records its entity, so rule R restores a changed entity to its own value; `_space_restored` is the `restored` callback and drops the arbiter's own record on any restore of its key (M09 to M11).
- Carry 4 (8755bcb3) and Carry 14 (its repeat): met. Consumed as built through `register_consumer`, `Restorer(..., baseline_of=, restored=)`, `async_arm`, `async_armed_entry` and `async_rebaseline`; no class attribute named `state`.
- Carry 5 (76ae476a), Carry 6 (2bcac34a), Carry 15 and Carry 16 (their repeats): not this group's. The reserve rule binds a consumer that budgets writes; the arbiter has no per-day write cap (`_write` keeps no counter; `hold` retries every `RETRY_MINUTES`), so no restore write is reserved (`## Forward-carry`).
- Carry 7 (the 2026-11-10 stacking ruling): met. #3402 and #3405 (R10-WATER-SETPOINT-FEEDBACK) are both merged to main, and origin/main `a7628041dc` is merged in at `acb7122c75`, so this pull request carries only this group's diff.
- Carry 8 (a070f930) and Carry 9 (its repeat), WSF's dropped space record: built in repair round 2 (below). At the plain merge it was live: `_note_sent` drops `written["space_setpoint"]` so that a loop move is sent, and `_arm_space` read the missing record as "no own write".
- Carry 17 (WSF's restatement of Carry 8 from its own merge base): met by the same build. `_arm_space` no longer reads the space record's absence as "never written" without checking `ArbiterState.feedback`: it reads the run's `prev_c` (M23, M24). The Off and unload restores read the arbiter's state after the pass, as the carry says, and `_space_restored` drops the run with the record (M25).
- Carry 10 (648c3c80) and Carry 12 (its repeat), write-ahead: built. The arm (which saves the baseline) precedes the send; the new check reads the off_restore store at the moment the space write's service call is made and finds the baseline `53.0` there, the store having held nothing before that pass. M18 (send, then arm) is killed by it and survived every other check. The arbiter's own write record (`held.written`) stays after the send, deliberately: a record lost to a crash between send and save leaves `space_before` unknown after the restart, so `_edited` adopts nothing, and the armed baseline already makes the own-write refusal moot.
- Carry 11 (5b825bae) and Carry 13 (its repeat), range bound at adoption: built. `_adopt` rebaselines to `_bounded(inp, "space_setpoint", edit)`. Control: `number.water_set` declares min 25, max 63; an edit reading 70 is restored as 63, and at the PR head it was restored as 70 (failing first, below); 40 is restored as read.

**Departure from the brief, for the reviewer.** The brief restores "on unload while Home Assistant is not stopping"; the hook as built restores on every unload, a stop included (`off_restore.py` module docstring, "Home Assistant stopping changes nothing"). A per-consumer stop rule would need an edit of the hook, which Carry 1 forbids ("never a second owner of the unload"), so this consumer follows the hook, and the docs say so.

**Repair round 2: conflict repair** (dispatch at reviewed head `561edf4c8f9b99420013b48ce1d225645ef70b95`, verdict merge; continued, not re-cut). The pull request was DIRTY on `custom_components/heatpump_optimizer/pump_arbiter.py` after main merged #3405 (`b421442efe`, R10-WATER-SETPOINT-FEEDBACK): `git log --first-parent origin/main -- custom_components/heatpump_optimizer/pump_arbiter.py` names `b421442efe` as the newest merge to touch the file, and `git merge-tree --write-tree origin/main 561edf4c8f` printed `CONFLICT (content): Merge conflict in custom_components/heatpump_optimizer/pump_arbiter.py`. origin/main was merged into the head (`acb7122c75`), no rebase.
- The one conflict hunk, `ArbiterState`'s fields after `supply_unsub`: both parents appended there. Kept `space_before` (this branch) and `feedback`, `stop_gap_k` (main), in that order; the merge touched no other line of either parent. `grep -c '^<<<<<<<\|^>>>>>>>\|^|||||||' custom_components/heatpump_optimizer/pump_arbiter.py` prints 0 at the head. `tests/closures.json` merged by the `ledgermerge` driver (`inert_reads.tests/harness_headers.py: merged as a set`); `tests/features.py` and `docs/configuration.md` auto-merged.
- Read together, the two parents met at two seams. Each is now one mechanism that keeps both intents whole:
  - Edit adoption against the clamp cut (`8577f90492`). `_adopt`/`_edited` (this branch) reads the space slot before `hold`, whose `_clamp_cut` (main) adopts a reading inside a loop write's bracket as the controller's bound. Because it reads first, `_edited` took that cut for a person's set-point and re-baselined the off restore to it: at the plain merge, `_edited` on a 26.0 reading after a 25.0 -> 27.0 loop move returned True. The bracket is now one predicate, `_cut_of`, read by both `_clamp_cut` and `_edited`; `_clamp_cut`'s behaviour is unchanged.
  - The own-write refusal against the loop's dropped record (`4831cb404f`, Carry 8). `_note_sent` (main) drops `written["space_setpoint"]` so a sub-tolerance loop move is sent; `_arm_space` (this branch) read the missing record as "no own write". On a key not yet armed (an upgrade), it then captured the optimizer's own reading as the person's baseline: at the plain merge `_arm_space` returned True (captured) after one loop move. The dropped record is the run's `prev_c`. `_note_sent` used to reset `prev_c` to None when the record was already gone, so a second move lost it; it is now kept until a write replaces it, and `_arm_space` reads it. `_space_restored` ends the run along with the record, so a restored baseline is never compared with a pre-restore loop value. No second record is added (Carry 8: "extends these fields rather than adding a second").
- Main's feedback block's `_FbCoord` gets a weak-referenceable `FakeEntry`, as round 0 did for the arbiter block's `_PaCoord`. A space write now arms `off_restore`, whose `_RECORDS` is a `WeakKeyDictionary`; with the `SimpleNamespace` entry the full suite stopped with `TypeError: cannot create weak reference to 'types.SimpleNamespace' object` in `_fb_sim`.
- The three `_clamp_cut` ledger pins whose lines moved into `_cut_of` are deleted (`2568235bb9`), as `ci_predict.py` directs for a STALE PIN.
- Alternatives that lost. Cut seam: run `hold` before `_adopt`; lost because `hold` would rewrite the edit before `_adopt` reads it, which is why this branch reads first. Carry 8, option 1: a second "last own space write" field on `ArbiterState`; lost because it is a second record of one fact, which Carry 8 refuses. Carry 8, option 2: keep the record in `_note_sent` and skip `_write`'s tolerance check by a flag; lost because it moves WSF's send mechanism, a larger change to a landed group.

## Head

`2568235bb9389bc48d9c3aa31f903134d3c1a1d6`, on merge base `a7628041dc02e298c5399003d4c0576391dd5c4e`, which is origin/main's tip at `2026-11-11T07:31Z`; `git merge-tree --write-tree origin/main HEAD` exits 0 there. Figures are this head's unless named.

## Mutation proof

Failing test first, for both seams, at the plain merge `acb7122c75` plus each new check:
- Cut seam: `env PYTHONPATH=tests/hastub python3 tests/features.py`: `1 of 5235 FEATURE CHECKS FAILED`, "R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK: a controller's cut of a loop write (26.0 inside a 25.0 -> 27.0 move) is not adopted as the person's baseline ..." `[cut True, outside True, no run True]`.
- Carry 8 seam, after the cut fix: the feedback block (`SEAM_BLOCK` in the harness): `1 of 36 FEATURES BLOCK FAILED`, "... (Carry 8): a loop move's dropped record still refuses the optimizer's own 26.0 ..." `[one True, two True (prev None), restored run FeedbackRun(... prev_c=26.0 ...), never wrote True]`.

`python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` at the head runs each mutant alone on a `git archive` copy:
- Arbiter block: `SURVIVED NULL`, then `KILLED` for M01 to M20 (statuses unchanged by the merge).
- Feedback block: `SURVIVED NULL`, then `KILLED` for M21 to M25.
- Exit status: rc 0.

The new mutants:
- M21: `_edited` without the `_cut_of` conjunct.
- M22: `_cut_of`'s bracket open at both ends.
- M23: `_arm_space` ignores the dropped record (`prev_c`).
- M24: `_note_sent` resets `prev_c` when the record is already gone.
- M25: `_space_restored` keeps the loop run.

The previous reviewer's own mutants (`origin/verdict/3404`, `evidence/reviewer-mutants.json`), each run alone through `tools/audit/seat/mutant_run.py --spec` on the arbiter block: `SURVIVED NULL`, `SURVIVED R1_own_ignores_entity_change`, `SURVIVED R2_restored_keeps_misses_retry`, `KILLED R3_arm_keeps_no_before`, `SURVIVED R4_own_refusal_reading_none_ok`, rc 0. Each status is unchanged by the merge and matches the verdict (R1 carried to WSF, R2 and R4 dismissed there). R4's `old` text was re-anchored from `last[0])` to `last)`, because the Carry 8 change rewrote that line; its mutation (`reading or 0.0` for the `reading is not None` guard) is the verdict's. R1 and R2 match unedited.

## Null control

- Arbiter block, all passing at the head:
  - With the arbiter not controlling (`pump_duty_mode` observe), off writes nothing and the hook sends 0 (`_pa_ro_null_sent == 0`, `writes() == []`).
  - Range bound: 40 is restored as read.
  - Grace: a reading one second inside `ECHO_GRACE_S` is not adopted.
  - Write-ahead: the store holds no baseline before the pass (`_pa_wa_before is None`).
- Cut seam: a 24.0 reading outside the 25.0 -> 27.0 bracket, and the same 26.0 with no loop run, are still adopted as edits (`outside True, no run True`). `_cut_of` excludes only readings inside the bracket.
- Carry 8 seam: the same 26.0 reading on an arbiter that never wrote is still captured as the baseline (`never wrote True`).
- Every WSF check in the feedback block passes unchanged, including the `_clamp_cut` bracket and replay checks.

## Figures

At `2568235bb9389bc48d9c3aa31f903134d3c1a1d6` unless named.
- Full suite: `env PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 5236 FEATURE CHECKS PASSED` (at `4831cb404f`; `2568235bb9` deletes three ledger files only).
- Mutants: `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py`: NULL survives in both runs, M01 to M25 KILLED, rc 0 (at `4831cb404f`, the last production edit).
- Reviewer mutants: `python3 tools/audit/seat/mutant_run.py --spec <evidence/reviewer-mutants.json, R4 re-anchored> --cmd <the harness BLOCK>`: as quoted under `## Mutation proof`.
- Scoped gate: `python3 tests/closure.py select --diff a7628041dc --workdir $D`: `MODE: SCOPED -- 23 script(s) run, 10 scoped out`; `PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=a7628041dc bash tests/run.sh`: `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, rc 0 (at `4831cb404f`).
- Ratchet: `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. Every `RESULT` line equals origin/main's and `561edf4c8f`'s (a `diff` of the three `RESULT` sets shows nothing moved), so the merge moved no metric up; no budget re-recorded.
- Score: `python3 tools/audit/archscore/score.py --diff a7628041dc`: `Architecture score: dS +0.0006 IMPROVES` (`coord_footprint 2497 -> 2496`).
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted against a7628041dc02`. Before `2568235bb9` it predicted three ledger reds, the STALE PINs deleted there.
- Unpinned sites' kills: `python3 tools/audit/seat/mutant_run.py --spec <five site mutants> --cmd <the harness SEAM_BLOCK>`: `SURVIVED NULL`, then `KILLED` for each of:
  - S1: `_cut_of`'s guard off.
  - S2 and S3: each bound of the bracket open.
  - S4: `_cut_of`'s return deleted.
  - S5: `_clamp_cut`'s guard off.

  Exit status: rc 0.
- Class seams (fixer.md step 8): every reader or writer of the arbiter's space record, `git grep -n -E '"space_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py | grep -E 'written|misses|retry|space_before|feedback'`: seven lines.
  - `_note_sent` (two lines, read and drop): the drop is now kept in `prev_c`, in this diff.
  - `_clamp_cut`'s adopt write: unchanged; its bracket is now shared with `_edited`, in this diff.
  - `_edited` (two lines, record and misses): reads `_cut_of`, in this diff.
  - `_arm_space`: reads `prev_c`, in this diff.
  - `_flow_command` (`state.written.get`): reads the record for the draw censoring guard and answers None while the record is missing. That gap is WSF's own transient between `_note_sent` and `_write`; this group leaves it unchanged, and it is already the landed behaviour on main.

## Unpinned sites

`ci_predict.py` lists four sites. All are `_cut_of`/`_clamp_cut` lines moved from WSF's pinned `_clamp_cut` lines. Each is killed (S1 to S5 under `## Figures`), so each is `mutation-autofix`'s to pin (its lane mutates `custom_components/`):
- custom_components/heatpump_optimizer/pump_arbiter.py:1028 GUARD_OFF: pinned by `mutation-autofix`; killed by S1.
- custom_components/heatpump_optimizer/pump_arbiter.py:1031 CMP_BOUND*2: pinned by `mutation-autofix`; killed by S2 and S3.
- custom_components/heatpump_optimizer/pump_arbiter.py:1031 RETURN_DEL: pinned by `mutation-autofix`; killed by S4.
- custom_components/heatpump_optimizer/pump_arbiter.py:1047 GUARD_OFF: pinned by `mutation-autofix`; killed by S5.

## Red checks

- `mutation` (`tests / mutation`, job 130227732011, round 1): "MUTATION TABLE REFUSED -- 2628 unpinned site(s) against 2627 at the ratchet base 45adb0c3b4, 2 of them added by this diff".
  - The two sites: `_edited`'s `>= ECHO_GRACE_S` CMP_BOUND and `_restorer`'s `if not entity` GUARD_OFF. Both survived the mutants then; round 1 killed them with M19 and M20 and pinned them.
  - Cheaper detector: prepr's step 6d (`ci_predict.py`), which listed both before the first handoff. That body answered them as `mutation-autofix`'s to pin, which was wrong for survivors.
  - This round's four unpinned sites are each shown killed above before being left to `mutation-autofix`.
- `merge_train.py owed-reds` lists `tests / mutation` among the required contexts. This round has run no CI yet, because the head was DIRTY.

## Forward-carry

none

## Friction

- brief-stop-restore: contradiction: the brief restores "on unload while Home Assistant is not stopping", while the hook it must reuse restores on every unload, a stop included. Built to the hook. Carry: dismissed: the departure is raised in the body for the reviewer; a stop-exempt restore would be a change to the hook, R10-GENERIC-HEAT-CURVE's seam
- pin-killed-timeout: cost: `python3 tests/mutation_table.py --pin-killed --base origin/main` ran 30 minutes and the seat's background limit stopped it before it pinned anything (it runs the full `tests/features.py` per mutant: `baseline tests/features.py: rc=0 failed=0 464s`). The four sites were instead shown killed by hand-written spec mutants on the feedback block. Carry: dismissed: mutation-autofix pins killed custom_components sites after the head moves
