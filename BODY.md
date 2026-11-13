R10-HOTFIX-FLOW-SETPOINT-STUCK: a production hotfix for a defect the owner (tvofi) reported on 2026-11-13 from his own install on v7.1.15. The install is a Tuya Rotenso Windmi under Pump duty control at Control, with a flow set-point entity. The flow set-point sat at 25 °C on every step, a space-heating boost included, and the house was at 16 °C at 0 °C outdoors.

**Cause.** #3404 (R10-ARBITER-OFF-RESTORE, merge 1aeaf273a4, first shipped in v7.1.12) arms the off restore before every space write (`pump_arbiter._arm_space`). When no baseline was armed and the entity read the arbiter's own last write, the arm refused, and the write was held until the controller read anything else. On an upgrade from v7.1.11 or earlier, the persisted record is the arbiter's last write, and the pump holds that value by design (`hold` rewrites any differing reading). On an idle step that value is the gate, `FLOW_GATE_C` = 25 °C. So every later space write was refused, and nothing wrote the entity again: not a heating step, not a boost's 55 °C ceiling, not a restart (the record is persisted). docs/configuration.md documented the hold ("set it on the pump once"); the v7.1.12 release notes did not.

**Fix: an own-write reading never holds the write.** `_arm_space` now always sends the write. Where the reading is the arbiter's own last write, the baseline the off restore captures is the baseline row's own space target instead: `_space_target` with no duty, which is 35 °C or the weather curve for a water unit and the planned room temperature for an indoor one. That is the value the arbiter holds when the plan is not in charge. The seam is a new keyword on `off_restore.async_arm`, `baseline_c`: the value to capture in place of the reading, used only on a first capture by a consumer with no neutral.

**Design decision, with the alternative refused.** The alternative was to capture the reading as the baseline. That was refused because, on an upgraded flow install, the reading is the 25 °C gate. Optimizer off would then write the gate back, which on a flow set-point means no heat, and keep writing it after every unload. #3404's guarantee (the optimizer's own number is never restored as the person's) is kept at no cost in heat. A value the person sets by hand is still adopted as the baseline, as before (`_edited`).

**Off keeps the own write until a restore replaces it** (the root-cause seat's finding (b), R10-RCA-SETPOINT-LATCH-DEADLOCK). `_forget`, run on Off, used to clear the dropped own write along with the record. With nothing armed, Off restores nothing, so the entity still reads the optimizer's 25. The arm after On then captured that 25 as the person's baseline, and a later Off would have written it back. `_forget` now keeps the arbiter's own last space write on `ArbiterState.dropped` until a restore replaces it (`_space_restored`). `_arbitrate`'s Off pass no longer re-forgets a state whose only record is that kept write, so an Off install does not re-save on every pass. The root-cause seat's second latch entry (c), a written 55 over a dropped own 25 with the entity reading 25, is released by the same `_arm_space` change and has its own check.

**The options page told the owner the entity is never written.** The text was "Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point." It is in strings.json and in en, sv and de, from 6f02b8a71e (#483, 2026-09-06). It has been false under Control since the set-point became a power command. Now it says that under Control the entity is written on every plan step and that Optimizer active off writes back the value read before the first write; under Off or Observe it is only read. docs/configuration.md now describes the new upgrade behaviour.

**Release notes correction, at the owner's request** (2026-11-13: "Also update the release notes for v7.1.12 if possible"). This adds one paragraph under the existing `### #3404` entry of the `## v7.1.12` section. No `## ` or `### ` line is added, removed or changed, and the top section is untouched. The orchestrator patches the GitHub Release body for v7.1.12 after the merge.

**Tests re-pinned, by name.**
- `R10-ARBITER-OFF-RESTORE: a reading equal to the arbiter's own last write is never captured as the baseline ...` (the `_pa_upgraded` check in tests/features.py). It pinned "the write waits", the deadlock, as correct. It now pins the invariant the root-cause seat proposed in (ii): the write is sent, and Off restores the baseline row's 35, not the own 30.
- The three Carry 8 checks of the water-setpoint feedback block, `R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK (Carry 8)`, `(Carry 8, round 2)` and `R10-ARBITER-OFF-RESTORE (Carry 8, round 2): the dropped own write is not consulted ...`. They pinned `_arm_space` returning False. They now pin that the arm sends the write and captures 30.0 (the rated 35 in return terms, under the 32 ceiling), never the own 26.0. The last of them pins that Off with nothing restored keeps the dropped write.

**New checks.**
- `R10-HOTFIX-FLOW-SETPOINT-STUCK: a boost over an idle step, and a space step, write the 55 degC ceiling in one pass from a persisted own write of 25 ...`. It covers the state in memory and loaded from the pre-#3404 store shape (no `dropped` key), with a null control without a record.
- `R10-HOTFIX-FLOW-SETPOINT-STUCK (R10-RCA-SETPOINT-LATCH-DEADLOCK (b)): a stuck install turned Off ... and On writes 55 at once, and a later Off restores the baseline row's 35 ...; (c): ...`.
- `R10-HOTFIX-FLOW-SETPOINT-STUCK: Optimizer off after the write a persisted own 25 no longer holds restores the baseline row's 35, never the 25 gate; null control: a value set by hand, 40, is restored as set`.

**The root-cause seat's detector is taken into this pull request unchanged.** It is `dev/audit/harnesses/r10_rca_setpoint_latch.py`, from origin refs/heads/handoff-wip/r10-rca-setpoint-latch-deadlock 2e20aa5d4e, under the INERT `dev/audit/harnesses/` prefix, with credit to that seat. The RCA document lands separately.

**Owner workaround on v7.1.12 to v7.1.15.** This was checked against origin/main code in the hastub stub and is unverified on hardware. Set the flow set-point entity once by hand to any value but 25, e.g. 40, while Optimizer active is on. The next arbiter pass, within a minute, writes the plan's target again, and Optimizer off later restores 40. Probe: `probe/workaround.py` in this seat's scratch directory under the session's state directory (`seat/hotfix-flow-setpoint/`), out of tree; the orchestrator holds the path for the reviewer.

## What PR 3404 guaranteed, and what this changes

The owner asked (2026-11-13) that the hold-off v7.1.12 introduced on purpose is not broken. This table covers every guarantee #3404 (merge 1aeaf273a4) stated, in its release-note entry and in docs/configuration.md, and every check it added to tests/features.py. A guard_pins.py change in the same pull request only gave its fixtures a weak-referenceable entry. Each row was run at this head in the pump-duty arbiter block (57 of 57 pass) or the feedback seam block (53 of 53 pass).

| #3404 guarantee or check | At this head |
|---|---|
| Off writes the person's baseline back (`switching the optimizer off writes the space set-point's baseline back, once, and nothing else ...`) | passes, unchanged |
| Unload restores it (`unloading restores the space baseline and the release writes the fallback row ...`) | passes, unchanged |
| The baseline survives a restart (`the baseline survives a restart: off after it restores 53, not the 25 the optimizer wrote`) | passes, unchanged |
| The optimizer's own write is never captured as the person's baseline (`a reading equal to the arbiter's own last write is never captured as the baseline ...`, the `_pa_upgraded` check) | **re-pinned, and the one narrowed guarantee.** Old: no capture of the reading AND the write waits (`_pa_up_first == []`, off restores nothing). New: no capture of the reading still holds; the baseline captured is the baseline row's own target (35) instead; the write is sent (`_pa_up_first == [25.0]`, off restores 35). Why: the wait had no release but a person's edit, and held every space write on an upgraded install. |
| A value the person sets between writes becomes the baseline (`a space set-point a person sets between writes becomes the baseline off restores ...`) | passes, unchanged |
| Echo grace: a reading inside `ECHO_GRACE_S`, or one that holds the write, is no edit (two checks, `a reading inside the echo grace ...` and `a reading exactly ECHO_GRACE_S after the write ...`) | passes, unchanged |
| A second differing reading is a refused write, not a second edit | passes, unchanged |
| The restored value stays within the entity's range and step (`an edit outside the entity's own range is adopted bounded to it ...`) | passes, unchanged |
| Write-ahead: the baseline is saved before the first write is sent | passes, unchanged |
| No space set-point means no restorer | passes, unchanged |
| A restored baseline equal to the plan's value is captured again after a restart (`_pa_restored_twice`) | passes, unchanged |
| A controller's cut of a loop write is no edit (`R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK: a controller's cut ...`) | passes, unchanged |
| Carry 8: a loop move's dropped record still identifies the own write | **re-pinned.** Old: `_arm_space` returns False (the write is refused). New: it returns True and the baseline captured is 30.0, never the own 26.0. Same narrowing as the `_pa_upgraded` row. |
| Carry 8 round 2: the own-write fact survives every end of the loop run | **re-pinned.** Same change: after each run end the arm sends the write and captures 30.0, not 26.0. The fact still survives each end. |
| Carry 8 round 2: the dropped write is not consulted once a write lands; a restore ends it; Off ends it | **re-pinned for Off only.** Old: Off ends it. New: Off with nothing restored keeps it, so the arm after On does not capture the optimizer's 25 as the person's (R10-RCA-SETPOINT-LATCH-DEADLOCK (b)). A restore still ends it. |
| docs: "after an upgrade ... the set-point is not written until it reads anything else, so set it on the pump once" | **removed.** Replaced by the baseline-row text in docs/configuration.md. |

No other #3404 check changed meaning.

**What "pause" could mean.** A grep of #3404's production diff for pause, hold, wait, settle and grace finds four things:
- (1) The own-write hold in `_held_back`/`_arm_space`: "not writing it until it is set at the controller". This is the only hold-off #3404 introduced, and the one this pull request changes.
- (2) `ECHO_GRACE_S` (20 s, older than #3404), which #3404 reads in `_edited` so that a reading within 20 s of a write is not taken as a person's edit. Unchanged; its two checks pass.
- (3) `_pump_off` forgetting the reading taken before a write while the power switch reads off, so the pump's own reset is never adopted. Unchanged.
- (4) `hold()`, the pre-existing write-back of a differing reading. Unchanged.

The supply switch's minimum run and minimum pause (`supply_hold.py`, R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE, #3512) shipped in v7.1.15, not v7.1.12. This pull request does not touch it.

## Release note

### Space set-point no longer held after an upgrade (R10-HOTFIX-FLOW-SETPOINT-STUCK)

Under Pump duty control at Control, an install upgraded from v7.1.11 or earlier to v7.1.12 or later could stop writing the space set-point. On a flow set-point the pump then stayed at its last idle value, 25 °C, through heating steps and boosts alike, until the set-point was changed once by hand. The optimizer now writes it from the first pass. When the set-point reads a value the optimizer wrote itself, turning the optimizer off restores the value the optimizer uses when the plan is not in charge (35 °C or the weather curve for a water set-point, the planned room temperature for an indoor one), never the 25 °C off value. The options page no longer says the space set-point entity is never written.

## Root cause

Root cause per dev/governance/rules/defect-root-cause.md: the defect reached v7.1.12 through v7.1.15.

- **Cause.** A refusal on an actuator write (the arm's own-write refusal) whose only release was a person acting at the controller. The upgrade path that triggers it is the common case, because the pump holds the arbiter's last write by design.
- **Process state.** The root-cause seat runs separately (R10-RCA-SETPOINT-LATCH-DEADLOCK, dev/audit/rca/R10-RCA-SETPOINT-LATCH-DEADLOCK.md at refs/heads/handoff-wip/r10-rca-setpoint-latch-deadlock 2e20aa5d4e, landing separately). Its stated finding: no contract asks that a refusal on an actuator write have a release that needs no person. The hold was driven, tested, documented and reviewed as intended, and the test that pinned it (`_pa_upgraded`) pinned the deadlock as correct.
- **Countermeasure in this pull request.** The detector `dev/audit/harnesses/r10_rca_setpoint_latch.py` drives 36 persisted starting states and requires each to reach the demanded write with no person acting. It is rc 1 at origin/main (4 of 36 fail) and rc 0 at this head (Figures). The re-pinned `_pa_upgraded` check states the same invariant in tests/features.py.
- **Policy lines.** Those proposed by the RCA seat for fix-review.md and fixer.md are owner-gated and not in this pull request.

## Head

90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1

Branched from origin/main 154dbb4c61 (merge base). `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main c67c1933be (after #3526), with `tests/closures.json` resolved as a set by its ledger driver; no main merge was needed. Against the open pull requests, the merge-tree of this head shows no conflict in tests/features.py or pump_arbiter.py:
- #3526, #3531 and #3511 merge clean.
- #3532 conflicts in coordinator.py only, and identically against origin/main.
- #3481 conflicts in dev/audit/rounds/round4/D6/claims.md and claims.py, docs/architecture.md and tests/deployment_shape.py, all identically against origin/main.

## Mutation proof

Failing first, at origin/main 154dbb4c61's production code with this branch's tests/features.py, the pump-duty arbiter block (`tools/audit/seat/features_block.py` from `R.section("pump-duty arbiter — mode and set-points per plan step` to `_pa_subs = _PaCoord(`) printed `3 of 56 FEATURES BLOCK FAILED`. The three are the re-pinned `_pa_upgraded` check and the two R10-HOTFIX-FLOW-SETPOINT-STUCK checks of the first commit. At the head the same block prints `ALL 57 FEATURES BLOCK PASSED`, and the feedback seam block (`# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380` to `_fb_floor = _fb_sim(clamp=(26.4`, with the arbiter block's four imports as preludes) prints `ALL 53 FEATURES BLOCK PASSED`.

`python3 tools/audit/seat/mutant_run.py --diff origin/main...HEAD --cmd 'bash <both blocks>'` at the head generated 14 mutants of the added production lines, and all 14 were KILLED (rc 0, no SURVIVED line):
- `off_restore.async_arm`'s `baseline_c` substitution (STMT_DEL);
- `_own_space_write`'s return (RETURN_DEL) and its record index (CONST_SWAP `record[1]`), and its record read (STMT_DEL);
- `_forget`'s three statements (STMT_DEL each);
- `_held_back`'s call carrying `now` (RETURN_DEL);
- `_arm_space`'s `if own:` (GUARD_OFF), its baseline statements (STMT_DEL) and its return (RETURN_DEL);
- `_arbitrate`'s Off-pass guard (GUARD_OFF).

At an earlier head the `_LOGGER.info` guard (`if baseline is not None:`) survived as an equivalent mutant. The guard is now `if own:`, which also decides the baseline, so its mutant is killed.

## Null control

- With no persisted record, the same boost and space-step passes write 55 at origin/main and at the head (`_pa_stuck_null`).
- A hand-set 40 is restored as 40 at the head (`_pa_stuck_off("40")`), as `_pa_upgraded("31")` restores 31.
- A dropped 40 that is not the reading reaches 55 (`_pa_dropped_over(55.0, 40.0)`).
- The detector's own skip control is rc 2 on a tree whose reference install is never written, per its docstring. It was not re-run here.

## Figures

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

- detector at origin/main 154dbb4c61: `python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <origin/main worktree>` from /tmp, rc 1: `SUMMARY ... demanded=55 states=36 failed=4 passes=10 dropped_axis=True armed_axis=True`. The four failures are `written=None dropped=25.0 reading=25 armed=False`, `written=25.0 dropped=None reading=25 armed=False`, `written=25.0 dropped=25.0 reading=25 armed=False` and `written=55.0 dropped=25.0 reading=25 armed=False`, each `reads 25 after 10 passes, demanded 55`.
- detector at this head: the same command on this worktree, rc 0: `SUMMARY ... demanded=55 states=36 failed=0 passes=10 dropped_axis=True armed_axis=True`.

## Red checks

- `tests / mutation` at 90eb45f69f51: red by construction on the 6 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. Cheaper detector: none is needed for this red: `mutant_run.py --diff` above already killed all 14 mutants, and the red only waits for the lane to record the pins.

## Unpinned sites

Each is an added production line the committed ledger cannot yet name (`python3 tools/pr/ci_predict.py`, the ADDED UNPINNED lines). The pump-duty arbiter block of tests/features.py drives every function they sit in, and the Mutation proof above kills each. The lane pins what it kills after the push.

- `custom_components/heatpump_optimizer/pump_arbiter.py:1492 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1623 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1623 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1645 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1650 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/pump_arbiter.py:1764 GUARD_OFF`: pinned by mutation-autofix

The four pins ci_predict named STALE PIN (lines this branch rewrote: `_arbitrate` GUARD_OFF 59013da4, `_arm_space` RETURN_DEL cbe69d47, `_held_back` BOOLOP and RETURN_DEL 605f504a) are deleted in commit 920fa2e031.

## Forward-carry

- The `space_setpoint_unit` description in strings.json and its translations ends "this integration never recommends a space set-point". That is true of a recommendation but reads like the sentence this pull request corrects. It was left as written to keep this hotfix to the sentence the owner quoted. Carry: R11-INTAKE-R10-RESIDUE
- `dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` (#3404's mutation proof) names mutants whose `old` text this pull request changes: the `space_baseline_own` log line, `_arm_space`'s return and `_held_back`'s call. That harness refuses those mutants before running. It is a closed group's record, not re-run here. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
