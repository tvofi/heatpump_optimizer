Fix review: merge 8c3e7591175ae151f5a27a2f2d45f2d7c8023f11

bus-nonce: 1cf79507b18cf0ec8ec9ae08a540a244

Round 1. Triage RECORD PR: the diff is dev/programme/triage/s6-batch97.md plus delivery/3079.md; no production code, no policy file.

## Findings

None.

## Evidence

- (a) a1bdb11c1 is an ancestor of origin/main (git merge-base --is-ancestor true). state_stamp in inputs.py reads last_reported, then last_updated, then last_changed; _age_minutes goes through state_age and so state_stamp; Health.ages() reads reading.age_minutes. tests/features.py D1-s5-01 has cells (5,480) and (400,400) and asserts cells[1][2]==5.0. Citations checked: debugger.py sensor_sanity ~260 and _HEALTH 88, coordinator.py ~5118-5120, snapshots.py 115, r10_scores_envelope.py 37 all say what the ruling says.
- Null control for the dismissal: I extracted state_stamp/state_age from the head and ran both cells. Main gives 5.0 and 400.0. With last_updated read first, (5,480) gives 480.0, so the D1-s5-01 assertion ==5.0 goes red. I could NOT run tests/features.py itself in this seat: venv-ci has no homeassistant, venv-ha is the typing-only install and lacks the test stubs (dt.freeze). So "D1-s5-01 passes in the suite" rests on CI, not on my run; the cells and the mutant I did re-derive.
- (b) Indexing at roster ref b3558fc7c (wave-r10-groups.json, R10-REPLAY-REAL-DAY, 11 carries, 0-based): 3 = "From R10-HEAT-METER (#2261; D15 lead L9" (unhealthy_input); 5 = "R10-REPLAY-REAL-DAY carry 4 (D15 lead L9), in its brief" and restates 3 (same ask and controls); 7 = STRANDED CARRY 34, the D15 lead L6 text (238 min power meter); 8 = STRANDED CARRY 54, the R10-SCORES --bundle scale drift; 9 = STRANDED CARRY 57 (loop_cpu_ratio), untouched. 1-based 4,6,8,9 = 0-based 3,5,7,8, so the move/dismiss assignments match the text. Each --match substring hits exactly one index (3, 5, 8, 7). 0-based 6 is the owner's day-choice ruling, not in the four and not touched, so nothing is left homeless. L6's own control (constant-value meter not flagged when last_updated advances) is covered by last_reported-first, which is stricter.
- (c) R10-ROUND-PLAYBOOK at b3558fc7c: 17 carries, resume stage not-started.
- (d) mark-carry does not exist in tools/audit/seat/roster_edit.py at origin/main (git grep finds nothing); it is in #3054 (361be3cd6). The ops cannot be applied until #3054 merges. The ruling states this hold itself. An ordering dependency, not a defect.
- Gate: roster_edit.ruling_verdict returns ACCEPT for P352; triage_refusal returns None on the real file; on a REJECT copy it returns "dev/programme/triage/s6-batch97.md#P352 is not an ACCEPT ruling (REJECT)"; with the file absent it refuses as not on origin/main (ev/gate.txt).
- tests/structure.py: STRUCTURE RATCHET PASSED. git merge-tree --write-tree origin/main head: exit 0, no conflict. Three-dot diff touches no claim file, VERSION, manifest or RELEASE_NOTES. The delivery row sits in the three-dot diff and names #3079.
- CI: merge_train.py classify at this head prints GREEN (pending none, red none), exit 0.
- Counts quoted from out-of-tree logs: none relied on; the 238 min and 2.6x figures are quoted from roster text I read at b3558fc7c.
