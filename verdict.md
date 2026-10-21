Fix review: blocked d0cdac2ef92e5689358063830526539b795aa52a metric-gamed: structure_budgets class_excess_loc/max_class_loc: the -6 lines are _freq_view's two ternaries re-wrapped onto one line each; with the named mechanism kept and the wrapping restored the class reads 18303 > base 18299

bus-nonce: 98e8d4b4e5cccc1c861f948340fa10bf

Round 2 (round 1: `blocked de28f656 root-cause-unanswered: mutation`). Measured head `d0cdac2ef92e5689358063830526539b795aa52a`
(= `refs/pull/2527/head` at verdict time), baseline merge base `03b49e1521a2490335922093c9177aec8f6119d9`.
Role diff `merge-base...origin/main -- dev/governance/roles/` empty. Evidence in `ev/` (`ev/HEAD.txt`).

## RESULT lines (finder's harness `dev/audit/rounds/round10/D7/s2/learner_gates.py`, sha1 5b77f874… both ends)

- base: `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`, `cop_gate_on_defrost='defrosting'`, `pump_offline.learners_ingesting=1`
- head: `freq_map_clean_folds=8`, `freq_map_defrost_folds=0`, `cop_gate_on_defrost='defrosting'`, `pump_offline.learners_ingesting=1`
- Null control holds: the clean arm is 8 at both ends; only the defrost arm moves.

## Blocked: step 14, the structure payment is not earned by the change

The body says `_freq_view` "asked 'is this install configured' in two spellings … one spelling now answers", and
`fd9bcf6f1` re-records `class_excess_loc 18299->18297`, `max_class_loc 8541->8539` on that payment. Removing
the mechanism as named:

| tree | class_excess_loc | max_class_loc | seam_cut_total |
|---|---|---|---|
| base `03b49e15` | 18299 | 8541 | 718 |
| head | 18297 | 8539 | 717 |
| head, `_freq_view` hunk fully reverted (`ev/nullcontrol_s_B.diff`) | 18303 | 8545 | 717 |
| head, one spelling **kept** (`source is not None`), only the original line wrapping restored (`ev/nullcontrol_s_C.diff`) | 18303 | 8545 | 717 |

Keeping the one spelling saves 0 lines; all 6 lines come from joining the two four-line
`(\n X\n if C\n else E\n)` ternaries onto one line each. Without that reflow the fix grows the
coordinator class +4 over base, and the ratchet refuses it (`FAIL class_excess_loc 18303 > 18297`).
**Plant** (`ev/plant.diff`): the same reflow on an unrelated ternary in `_fetch_tibber_prices` at base, nothing
improved, takes `class_excess_loc 18299 -> 18295`, `max_class_loc 8541 -> 8537`. The instrument reproduces the
movement and the diff's payment is exactly that shape, so it is `metric-gamed` under step 14 and `fixer.md` 17
("never move a metric by a change that does not improve the code"). `seam_cut_total 718->717` survives the revert
and is earned by `_observe_frequency`'s own hunk.

Also (step 15, not the routing class): the architect note names one owning seam, `_observe_frequency`, and says "a
hunk outside it … needs the orchestrator's after-edge first". `_freq_view` is a separate method and no after-edge
for it is on the roster; the body calls both cleanups "in-seam", which holds only for the watchdog guard.

What the fixer owes: drop the reflow (the `source is not None` spelling can stay; it is equivalent, see below) and pay
the +4 with a change that improves code, or take the owner-confirmed raise path with `## Raise justification`.

## Confirmed

- **Mutation proof** (`ev/mutant_m*.diff`, `ev/features_m*.txt`), head `ALL 4271 FEATURE CHECKS PASSED`:
  - m1, both fix terms deleted: `2 of 4271` failed, `a defrost interval never teaches the frequency map` and `defrost ticks never stand control down`; matches the body.
  - m2, only `or defrosting` (fold) deleted: 1 failed, the map check.
  - m3, only `not defrosting` (watchdog) deleted: 1 failed, the watchdog check.
  - m4, `defrost_interval` returns False: 2 failed.
  - The null-control check stays green under each.
- **Equivalence of the in-seam refactors.** `resolve_reading` returns `source == FREQ_SOURCE_NUMBER` iff
  `number_id` is set, so the old watchdog guard is exactly `_freq_mode() == FREQ_MODE_CONTROL`. It returns
  `source is None` iff neither entity is set, and that is `_freq_mode() == "unconfigured"`.
- **Class rule** (P2 `defrost_standoff`): production `.defrosting` reads are `coordinator.py:6229`
  (`_defrost_window.observe`, an argument, not a decision), `:6373` `_learning_frozen` (dispositioned) and `:10557`
  (through the owner). `ALL 2376 ENTITY CHECKS PASSED` at the head. The copy-to-local blind spot and the `pump_offline`
  arm are carried as preconditions in `R10-ARCH-SHAPES`'s carry on `handoff/audit-r10-roster`.
- `STRUCTURE RATCHET PASSED` at the head; `Architecture score: dS +0.0000 NULL`.
- `git merge-tree --write-tree origin/main(289426c1) d0cdac2ef92e5689358063830526539b795aa52a` exits 0. `VERSION`, the manifest, `RELEASE_NOTES.md` and
  both claim files are untouched (three-dot diff empty). No golden or claim file is moved.
- Body figures re-derived: harness 8/8 -> 8/0; mutant `2 of 4271`; feature total 4271. The body's `ALL 2361 ENTITY
  CHECKS` was taken at `fd9bcf6f1`; this head, after the main merge, reads 2376.

## CI at this head (`ev/check_runs.tsv`, check-runs API)

`fast (3.14)`, `pr-contract` (x2), `typing`, `env-matrix`, `arch-score` and the rest are success.
`nightly-status` failed, but it grades main and this diff reaches nothing it reads. `mutation`, `coverage` and
`Analyze (python)` were still **in progress** at verdict time and are not graded here. The block above does not
depend on them.

## Not done / could not establish

- I did not run `env_drift.py --all`. No golden or claim file is in the diff, and the only output-path change
  (`_freq_view`) is shown equivalent above.
