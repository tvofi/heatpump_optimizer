Fix review: merge c5ea2af8c0d762a27830523d09cc5c96ac9e08c5

bus-nonce: 363d9438860be782428a9aefdab13445

Round 2 delta review of R10-OUTSIDE-LEARNER-ROBUSTNESS (part 1 of outside PR #3435), handoff tip refs/heads/handoff/r10-outside-learner-robustness = c5ea2af8c0d762a27830523d09cc5c96ac9e08c5, body refs/heads/handoff-body/r10-outside-learner-robustness = 120d7460c4f2. Resumed from verdict/3468 at efa4a8021bd8 (`blocked da2eef8a... class-open`). Range reviewed: da2eef8a..c5ea2af8 (4 commits). `review_carry.py da2eef8a c5ea2af8` prints FRESH-REVIEW, so this is a delta round. The production delta is `heat_energy.py` only (`SpanEnergy.dhw_seen`, `_fold_dhw_step`, `_close`, `span_heat`'s predicate). Code outside that delta was not re-reviewed: the delta adds a refusal path only, and `ran_hot_water`, `bridges_hot_water` and `replay_gate` are byte-identical across the range.

## Evidence

- RESULT block answered. With the round-1 finder harness (`ev/unobs_span.py`, the previous verdict's own, unchanged) at both ends (`ev/attack_both_ends.txt`):
  - da2eef8a: `charge, cycle 6 mode not live: space_kw=2.727` (the defect).
  - c5ea2af8: `space_kw=None`, so the span refuses instead of reading the charge as space heat.
  - The all-observed arm is flat at 1.818 at both ends. The null control (no charge, cycle 6 not live) is flat at `space_kw=2.0 == heat_kw` at both ends.
- RESULT attack, unobserved read positions (reviewer's `ev/unobs_attack.py` and `ev/edge_attack.py`; outputs `ev/attack_both_ends.txt`, `ev/edge_both_ends.txt`).
  - Positions tried: one non-live mode read at 0, 1, 4, 6, 10 or 11, and three at once (1, 6, 11), with the charge at the span's first step, at step 3 and at its last step.
  - Every case where the dwell saw the charge reads 2.727 at da2eef8a and `None` at c5ea2af8.
  - A non-live read at 0 or 3, which leaves the span attribution observed, reads 1.818 at both ends.
  - No-charge nulls at 1, 6 and 11 read `2.0 == heat_kw` at both ends. An install with no mode entity therefore keeps its space figure, because `dhw_seen` is never set.
- RESULT case outside the class, flat at both ends. The charge's own mode read is not live: unobs@2, unobs@2,3, charge@1 with unobs@0, and charge@11 with unobs@10.
  - These read `space_kw=2.727` at both da2eef8a and c5ea2af8, with `dhw_seen=False`.
  - The dwell did not see this charge. `bridges_hot_water` requires `ran_hot_water(self.attribution(...))`, which is observed-only, so this diff does not bridge that cycle. The reading is the documented plan fallback (`ran_hot_water`'s docstring: "An unobserved interval says nothing here: the caller's own plan rule stands"), unchanged from the merge base.
  - It is not in the blocked class (a charge the dwell saw), and this diff did not cause it. Whether the coordinator keeps such a cycle clean was not measured here.
- RESULT mutation, reviewer's own mutants (`ev/mut_delta.py`, run through `features_block.py` on the new check's block; `ev/mutation_delta.txt`):
  - NULL passes (`ALL 1 FEATURES BLOCK PASSED`).
  - KILLED: D1 (guard drops `e.dhw_seen`), D2 (fold never sets seen), D3 (seen not reset at close), D4 (old `self._dhw_kwh is None` early return restored), D5 (`dhw_seen` not passed to `SpanEnergy`). Each prints `1 of 1 FEATURES BLOCK FAILED`.
  - These are the body's Ma, Mb, Mc, Md and Me in substance.
- RESULT body figures, re-derived at c5ea2af8 (`ev/body_figures.txt`):
  - `--emit-prelude` prints `prelude of 24 statement(s)`.
  - The R10-HEAT-METER block prints `ALL 31 FEATURES BLOCK PASSED`.
  - Failing test first: with `heat_energy.py` at da2eef8a, the block prints `1 of 31 FEATURES BLOCK FAILED`, on the new check.
  - `features_block.py --self-test`: `11 checks, 0 failed`.
  - The body's gate, golden and arch-score figures were taken at abff0298. They were not re-run here (CI's heavy runs are cited, not repeated). Between abff0298 and c5ea2af8 only `tests/mutation_ledger/` changes.
- RESULT previous verdict's harness finding: answered. The prelude is now derived from the tree by `features_block.py --emit-prelude` (landed in this range, with its instrument doc). The proof above re-ran from the tree with no hand-copied file.
- RESULT mutation ledger delta, judged consistent with the code change:
  - `span_heat.CMP_BOUND.65b91d90` was deleted; the `dhw > 0.0` comparison it pinned is gone from `span_heat`.
  - Five pins were added or renamed on the new guard and fold sites.
  - No budget file, `tests/closures.json` or archscore file moves in the range.
- RESULT `python3 tests/structure.py` at c5ea2af8: rc 0, `STRUCTURE RATCHET PASSED` (`ev/structure.log`).
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md, `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt`. The three-dot diff from merge base 6f0ff9d8 to c5ea2af8 is empty (`ev/untouched.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main c5ea2af8c0d762a27830523d09cc5c96ac9e08c5` exits rc 0 against origin/main 6cc15e9b8. No conflict (`ev/merge_tree.txt`).
- RESULT body head: the body names c5ea2af8c0d762a27830523d09cc5c96ac9e08c5, the tip measured here. The handoff tip was re-read at verdict time and is unchanged (`ev/refs_at_verdict.txt`).
- RESULT class census: the body's rule now includes `dhw_seen`. Its disposition of `span_heat` as closed matches the attack above for every charge the dwell saw.
- RESULT forward-carry: Carry 1 and Carry 2 (P2 and P3 of #3435) are unchanged from round 1. The friction line is dismissed, now that the replacing instrument has landed.
- CI: none ran at c5ea2af8. PR #3468's head is still d734e2a7 until the relay applies the handoff, and no review packet was supplied.
  - pending-ci: the head carries main, whose `governance / instrument-self-tests` is red on main until PR #3474 merges. That check is outside `merge_train.py owed-reds`, so it is expected and blocks nothing here.
  - The owed set (`tests / fast (3.14)` and the others it prints) has not run at this head. The train re-proves it on current main.
- Role contract: the role pack was rendered from this checkout's main (`role_pack.py render fix-review`). The head's copy of `dev/governance/roles/` is older than main's; main's copy was used.
- Round: 2 of the fix (round-1 verdict efa4a8021bd8). No re-cut is owed.
