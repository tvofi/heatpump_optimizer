Fix review: merge 1713468b91e6d7fb1345ad391b03213df1148ce9

bus-nonce: 4a09d66c01d059ae37f6d81af5759740

## Round

First review of handoff r10-outside-disinfection-setpoint (group R10-OUTSIDE-DISINFECTION-SETPOINT), measured from detached worktrees at the tip 1713468b91e6d7fb1345ad391b03213df1148ce9 and at its merge base a7628041dc02e298c5399003d4c0576391dd5c4e. No pull request exists yet, so there is no review packet and no CI run to read: no check has gone red on this head, and none is owed a `## Red checks` answer.

## Evidence

- RESULT oracle (finder's harness: `desired` driven through `tests/block_duty.py`'s `_snap`/`_Coord`/`NOW`, stock pair 55/60, `ev/probe.py`, `ev/probe_base.txt`, `ev/probe_head.txt`): a step booked with dhw_reason legionella writes base 55.0 / head 60.0; a step held by `disinfecting` writes base 55.0 / head 60.0; an ordinary hot-water step writes 55.0 at both ends; an everyday set-point of 62 writes 62.0 at both ends, booked or held. This reproduces the roster brief's 55.0 versus 60.0 figures.
- RESULT rows: at the head, the None, idle, dhw and both rows all write 60.0 on a booked step and on a held step. The space row on a booked step stays the 30.0 gate; on a held step it becomes Heating + DHW and writes 60.0. With the cycle disabled, every row writes 55.0 at both ends. Brief item (4) is pinned by the test "the space-only gate stays a gate on a booked step…", and my mutant R3 (the booked space row writing `dhw`) is killed by it.
- RESULT rounding (hygiene adversarial):
  - A disinfection temperature of 60.3 on step 0.5 writes 60.5, and 59.6 on step 1 writes 60.0, so a cycle target is never snapped below itself.
  - An entity maximum of 58 writes 58.0, and an off-step maximum of 59.5 on step 1 writes 59.0, so the write stays inside the entity's range. As the brief says, a target above the range is left to the guard's unreachable notice.
  - My mutant R5 (`rounding="down"`) is killed.
- RESULT repair (second face), stock pair:
  - The arbiter wrote 55 and the pump reads 55: base raises the repair with Fix 60; head raises nothing.
  - The arbiter wrote 55 and a person set 50: the repair is raised at both ends with Fix 60.
  - No arbiter write and the pump reads 55: the repair is raised at both ends with Fix 60, so the repair is unchanged on an install where the arbiter does not write.
  - The cycle disabled: no repair at either end.
- RESULT named mutants: `tools/audit/seat/r10_disinfection_setpoint_mutants.py` exits 0 at the head (`ev/named_mutants.txt`). NULL survives with 61/61 checks; M1 through M9 are each killed by the checks the body names. I read the script's old/new pairs, and each is the mutation the body describes.
- RESULT own mutants (`ev/own_mutants.py`, `ev/own_mutants.txt`):
  - R0 null: `block_duty`, `features` and `rolling` are all green.
  - R2 (`dhw_hard_max_temp` ignores the cycle): killed by `tests/features.py`, through the legionella ceiling checks.
  - R3: killed (see the rows line above).
  - R5: killed (see the rounding line above).
  - R1 (`cycle <= everyday` changed to `<`): survives. See the Findings.
  - R4 (the arbiter reads `dhw_disinfection_temp` in place of `dhw_cycle_temp`): survives. This mutant is equivalent at that site: the `cycle <= everyday` branch already returns the everyday set-point whenever the disinfection temperature is not above it. The max is pinned on its owner by M8's check.
- RESULT failing first at main: the head's `tests/block_duty.py` copied over the base fails 8 of 61 checks (`ev/failfirst_base.txt`), both faces among them. The body says 7; see the Findings. Every null-control check passes at the base.
- RESULT null control (`dev/audit/harnesses/r10_disinfection_setpoint.py`, the fixer's instrument, disclosed as the builder's): run at the base and at the head (`ev/h_base.txt`, `ev/h_head.txt`), the 80 `null_*` lines are IDENTICAL; 36 of the 40 `stock`/`offstep` lines differ. Both figures match the body.
- RESULT claims: `tests/env_drift.py --all` at the head prints NO UNCLAIMED DRIFT over 56 scenarios and NO STALE FIXTURE over 56 (`ev/env_drift_tail.txt`). Neither claim file is touched, which matches the body's statement that no fixture is claimed.
- RESULT VERSION, `manifest.json`, `RELEASE_NOTES.md` and both claim files: `git diff --stat` against the merge base is empty.
- RESULT structure: `tests/structure.py` prints STRUCTURE RATCHET PASSED. `class_excess_loc` moves only down (17537 to 17534), and is paid by docstring tightening in `thermal_model.py`.
- RESULT merge: `git merge-tree --write-tree origin/main` at f24d107bd7aa170bea7419251a4b7f4f48b732f6 exits rc=0 (`ev/merge_tree.txt`). The head is behind main and merges cleanly. Main has not changed the legionella enabled flag since the base, because #3398 has not merged, so brief item (1) is correctly not rebased.
- RESULT authorship: adopted commit feeb0b6b3 has author Bankaifan. Its diff stat equals that of the author's fork commit f9a7bcb4e (3 files, +57/-2). `refs/pull/3439/head` is still f9a7bcb4ee. The body's head SHA is the head I measured.
- RESULT class (step 6): I ran the body's rule `git grep` for the legionella enabled flag and the legionella temperature readers under `custom_components`. Every non-config reader (`coordinator.py`, `dhw_planner.py`, `legionella.py`, `thermal_model.py`) is dispositioned in the body, and the arbiter's hot-water writes all go through `_dhw_write` or the `DHW_GATE_C` gate. The rule returns no undispositioned seam.
- Brief item (3): `dhw_target_temperature` is left as the everyday target, and the body records why. No golden fixture moves.
- Figures not re-derived:
  - `Architecture score: dS +0.0023`: I did not re-run archscore.
  - The scoped-gate run: CI's heavy run, not re-run (step 11). It is owed to CI when the PR opens.
- Owed reds: `merge_train.py owed-reds` printed the required set (`ev/owed_reds.txt`). There is no run on this head to read, and the body's predicted `mutation` red is answered under its `## Red checks`.
- Forward-carry: the body says none. I found no finding that changes a later stage. R10-OUTSIDE-DHW-START-HYSTERESIS builds after this group on `desired`, as its roster entry already states.

## Findings

- The body's failing-first figure "fails 7 checks" does not re-derive: the head's `tests/block_duty.py` over a7628041dc fails 8 of 61 (`ev/failfirst_base.txt`). The likely cause is that the check added after M8's first cut also fails at main. Both faces fail as claimed, so no conclusion changes. Carry: dismissed: a stale body count, harmless to the verdict, corrected by the opener's re-read when the PR opens
- Surviving mutant R1 (`cycle <= everyday` to `cycle < everyday` in `_dhw_write`). It differs only when the everyday set-point equals the disinfection temperature and both sit off the entity's step: then the everyday branch rounds to nearest, possibly below the guard's credit threshold. The brief's null control requires an everyday set-point at or above the disinfection temperature to be written byte-identical to main, which the `<=` keeps. Carry: dismissed: equivalence region mandated by the brief's null control; only a config pair equal and off-step reaches it
- `dhw_gated` judges a reading against the arbiter's last write, not what it would write this step. A person's value (50) beside the arbiter's 55 still raises the repair with Fix 60, which the arbiter rewrites to 55 at its next write. This is transient: the arbiter writes back the difference and the repair then stands down. It is not the standing contradiction the brief measured. Carry: dismissed: self-clearing within one arbiter write, pinned by the fixer's check "a person's value beside the arbiter's write still raises the repair"
