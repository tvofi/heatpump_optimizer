Fix review: merge 580f12908056021e9448d5f0520919044e6de41a

bus-nonce: 8ff03f19a812307162aa7aa0d0fe712d

Round: second (a delta review). It resumes from `verdict/3469` at 85f2fa2c27fa, which returned `blocked 6f1dd2040ce5 class-open`. Measured head: 580f12908056021e9448d5f0520919044e6de41a, which is the handoff tip. Repair range: 6f1dd204..580f1290. `review_carry.py` prints `FRESH-REVIEW` for this range, so only the delta is reviewed here.

## Findings

none

## Evidence

- Both items of the earlier block are answered.
  - Block item 1, the high-limit sensor at or below the gate. The finder's harness is the earlier verdict's `probe2.py` and `probe.py`, run against the harness file of the reviewed head (blob d6a63655). I ran it against the production tree of 6f1dd204 and of 580f1290 (`ev/finder_probe_both_ends.txt`).
    - At 6f1dd204, a high limit of 5.0, 15.0 or 20.0 gives 30 of 62 writes at or below the 20.0 gate, the lowest being 5.0, 15.0 and 20.0.
    - At 580f1290 the same limits give 0 writes at or below the gate, lowest 26.0. The write list is 65 writes, identical to the no-sensor row.
    - Null control, identical at both ends: no sensor gives 65 writes, lowest 26.0. Limits of 21.0 and 22.0 above the gate still give 62 writes with lowest 21.0 and 22.0, so a usable limit is still used. A limit of 24.0 is unchanged. A low limit of 40 or 31.9 against the 32 ceiling is unchanged.
  - Block item 2, the combi census.
    - The head merges cleanly with current origin/main c71d3f6e8983, which includes #3466: `git merge-tree --write-tree` exits 0, tree 8021b1ecd020, empty stderr, no MERGE-CLAIM line (`ev/merge_main.txt`). On the merged tree, `combi_type_branch census` is `ok` (`ev/features_merged_main.txt`).
    - At the head alone, in a git worktree, `tests/features.py` fails only the census (1 of 5252), on main's six pre-#3466 lines. Neither `config_flow.py:1704` nor `const.py:836` is among them (`ev/features_head_worktree.txt`).
- Attacks on the new clamp (`ev/attack.py`, `ev/attack_both_ends.txt`). These probes are mine, not the finder's.
  - I called `_feedback_bounds` and the write's `_bounded` directly. The grid was 2 units × entity steps 0.1/0.5/1.0 × sources sensor/cut/both × 11 offsets (gate −25 or −5, −step, 0, +0.005, +0.01, +step/2, +step−0.001, +step, +step+0.001, +2·step). The offsets cover the sensor equal to the gate, equal to the gate plus one step, and `cut_hi_c` under the gate.
    - At the head, every row writes above the gate.
    - At 6f1dd204, 144 rows wrote at or below it.
    - A limit at the gate plus one step is kept (hi 20.10, 20.50, 21.00 for return; 25.10, 25.50, 26.00 for flow). A limit 0.001 under that is dropped (hi 32.00, the ceiling).
  - Placeholder high-limit states, run through `sim`. The states `unavailable`, `unknown`, `''`, `nan`, `-20.1`, `100`, `100.1` and `inf` are the same at both ends: lowest 26.0. The states `0` and `-20` are inside `WATER_RANGE_C`: at 6f1dd204 they gave 30 writes at or below the gate (lowest 0.0 and −20.0); at the head, 0 such writes and lowest 26.0.
  - Unset space_setpoint entity: `_bounded` returns None at both ends. The bounds at the head are 25.70 and 32.00, since the sub-gate 20.0 limit is dropped through the `or clear` fallback.
  - Controller clamp maximum of 18.0, 20.0, 20.1 or 21.0 with no sensor: identical at both ends (31 writes, lowest 25.7, 235 retry passes), so the cut filter does not regress the readback path in `sim`. In this fixture `sim` never learns a cut below the gate. The direct grid's `cut` and `both` sources cover that path.
- Group harness at the head (blob b0202406…), run at both ends (`ev/group_harness_both_ends.txt`). The body's figures check out:
  - Old head: rows 15.00, 20.00, 20.05 (return) and 20.00, 25.00, 25.05 (flow) print lowest 15.0, 20.0, 20.0, 20.0, 25.0, 25.0 and `above the gate False`.
  - New head: each prints `writes 24 lowest 26.0 above the gate True`, the no-sensor row's count.
  - The `unset` and `+0.10` rows and the seven earlier rows are byte-identical at both ends.
- Mutation proof, run with `tests/features.py` on a `git archive` copy of the head (`ev/features_{HEAD,M1,M2,M3}.txt`). In an archive copy, `recorded_at (#363)` fails at the unmutated head too; it passes in the git worktree, so it is an artifact of the copy.
  - The unmutated copy fails 2 checks, census plus that artifact.
  - M1 (`and v >= lowest` deleted), M2 (`v > gate`) and M3 (`lowest = clear`) each fail 5 checks: the three part-3 I2 checks the body names, plus those two. The grid counts are 2304, 1008 and 792 of 3024 passes at or below the gate. The M1 count matches the body's failing-test figure, 2304 of 3024.
- Not re-derived at this head:
  - O1–O7 were not re-run. `_setpoint_limits_c` is untouched by the delta, and the earlier verdict ran O1, O2 and O4–O6 at 6f1dd204.
  - The body's hand-run ledger mutants for lines 993 and 994 (BOOLOP, CMP_BOUND, RETURN_DEL) were not re-run individually. My M2 is a comparison mutant on line 993 and is killed.
  - The body's seam rules were not re-run. The delta adds no new reader of the limit sensors.
- Ledger pin removal: the removed `_feedback_bounds.RETURN_DEL.1af408a4.json` pins the old return-line text, which the delta rewrites. The removal is earned by the change and moves no budget.
- Cheap checks at the head (`ev/cheap_checks.txt`):
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `archscore --diff origin/main`: `dS +0.0000 NULL`.
  - `tests/entities.py`: ALL 2707 ENTITY CHECKS PASSED.
  - VERSION, manifest, RELEASE_NOTES and both claim files are absent from the three-dot diff at merge base 0a2139b1dd.
  - `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- CI: no review packet came with this dispatch.
  - PR #3469's check runs, read live: no owed check (`merge_train.py owed-reds`: coverage-ratchet, fast (3.14), mutation, typing, validate-hacs) has concluded red. `validate-hacs` passed. The gate, mutation and most governance jobs were still queued or in progress at read time.
  - I did not wait for them. The `tests / fast (3.14)` red that the body answers is main's census, which #3466 has since repaired on main.
- Forward-carry: the body names none, and the delta adds no finding for a later stage. The body's ceiling-under-entity-minimum note is outside this class (it is `_flow_target`'s value on main), recorded and not carried. I agree with that disposition.
- `ev/HEAD.txt` holds the head reviewed.
