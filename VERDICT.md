Fix review: merge f2f204fc3ed608a69b56ee9ebc0c2eee23e74dc1

Round: second review of this PR (round 2). Round 1 blocked daac94b43 (claim-refuted: 0.120 red on an idle 4-core box).
Measured head: f2f204fc3ed608a69b56ee9ebc0c2eee23e74dc1. I re-read it on origin after measuring, and it is still the head. Merge base 289426c1f.
Group: R10-REPLAY-CAP. Brief read from origin/handoff/audit-r10-roster (31e162fd3). Finder harness: dev/audit/harnesses/r10_replay_loopnorm.py (#2339), unmodified; --self-test checks=7 failed=0. I built no harness.
Environment: a cloud container, 4 cores, load average 0.4-0.9, Python 3.11 venv with tests/requirements-ci.txt's pins. This is a fifth environment, outside the body's four.
Contract currency: git diff merge-base...origin/main -- dev/governance/roles/ touches only orchestrator.md (newer main 22615537a). fix-review.md is current.

## Round-1 blocking item: resolved

Round 1 refuted two things: the runner-class model, and the 5.0 % within-job band as the cap's sizing. This head drops both. It sizes the cap at the centre of the spread between environments, sqrt(2*0.0823*0.1236) = 0.143. The test is whether that cap holds on a box it was not sized on. This box is one.

RESULT finder_both_ends interleaved 3 rounds x 2 runs: base(289426c1f) 0.1058 0.1160 / 0.1223 0.1201 / 0.1160 0.1162; head 0.1390 0.1022 / 0.1365 0.1259 / 0.1160 0.1193 (ev/finder_harness_both_ends.txt). The code is identical at both ends, so this is the box's own spread: 0.1022-0.1390, 1.36x on one box.
RESULT replay_lane_head tests/replay.py at head: clean loop_cpu_ratio 0.0974 (loop_ref_ms 183.5), memory arm 0.1225, loop doubled 0.203; ALL 93 replay checks PASSED (ev/replay_head_full.txt)

All 14 of this box's readings (0.0974-0.1390) fall under 0.143. Under the old caps, 0.120 reds 5 of them and 0.111 reds 10. Each doubled reading is over the cap: the lane's doubled arm reads 0.203, and the lowest reading doubled is 0.195. So the cap holds out of sample, and the leave-one-out claim survives a sixth trial.

Recorded caveat, not blocking: this box's maximum, 0.1390, is 2.8 % under the cap. Pooled with the body's 44 readings, the spread is 0.0823-0.1390, a factor of 1.69, not 1.50. That is still under the 2x the band can hold. The body itself says the next box outside the band reds it again, and it carries a paired-reference design to R10-REPLAY-LANE. This measurement supports that carry. The orchestrator may want to add 1.69x to the carry text.

## Verified

- Step 1, mutation proof (ev/mutation_proof.txt). I mutated the literal in tests/replay.py, re-imported COST_BUDGETS and fed cost_offenders. At 0.143, none of 0.1390, 0.1225, 0.1236, 0.1206 (high) or 0.0974, 0.0823 (low) is an offender. At 0.120: 0.1390, 0.1225, 0.1236 and 0.1206 are over. At 0.111: the same four are over. At 0.165: 0.0823 is flagged "cannot see a 2x cycle; re-record 0.1164". The literal is load-bearing in both directions, and I restored the tree afterwards (git diff clean).
- Step 8, figures. I re-ran the body's centre/leave-one-out command verbatim. It prints 44 0.0823 0.1236 0.143; ci128 0.143 0, ci80 0.143 0, m1 0.145 0, idle 0.138 0; per-cap offenders 0.111 15, 0.12 3, 0.143 0, 0.165 1. Every figure matches.
  - The idle box's 16 readings match round 1's evidence (probe/rev-2548-a7501349: n8 run lines 0.1171 ... 0.1155, interleaved six, lane clean 0.1206 and memory 0.1236).
  - CI slow class: I spot-checked run 39106988523, slow job 117614882824. Its clean reading is 0.0875 at loop_ref_ms 127.9 and its memory arm 0.0852, both in the body's ci128 list. Its loop-doubled arm is 0.1769, over 0.143, though the body's list of doubled arms omits it.
  - The red rows (0.1114/0.1162, 0.1138/0.1081) were verified in round 1.
  - Not re-derived:
    - the other CI ci128 values;
    - --series, which needs gh API access (gh here is unauthenticated: api_failures=23);
    - the M1 bisect readings, and the M1 full lane at load about 550. These are the fixer's own box and I cannot reproduce that box.
- Step 4: no golden or claim file is in the diff (tests/replay.py and dev/programme/delivery/2548.md only; ev/diff.patch).
- Step 5: VERSION, the manifest and RELEASE_NOTES.md are untouched.
- Step 6, class: the body names no enumeration rule, and the issue (#2272) states one seam, the loop_cpu_ratio literal. The class is that one seam. The other configurations the harness accepts were the other environments, covered above.
- Step 7: the body names f2f204fc3ed608a69b56ee9ebc0c2eee23e74dc1 as head (it merges code head a77d0628c, then origin/main 289426c1f).
- Step 10: the forward-carry to R10-REPLAY-LANE is at origin/handoff/audit-r10-roster 31e162fd3, groups[50].carry[4]. It states its control as a precondition: record from at least both CI classes plus one outside box, or use a same-job paired reference. It is marked as replacing the round-1 text.
- Step 11, CI on this head (ev/check_runs.json, 49 runs, all concluded). Everything is success, skipped or neutral except nightly-status. That check grades main's 2026-10-21 scheduled slow lane, the defect this PR answers. The body names it in "## Red checks" and answers it: the cheaper detector is the lane's own cost_offenders, at no extra standing cost. pr-contract ran twice, the second time at 13:20:45, after nightly-status concluded at 12:37, and both runs succeeded. budget-raise-gate (two runs) succeeded too. The gate lanes (closure-scope, fast (3.14), typing, browser, coverage, closures, composed-proof, mutation) are all green. This diff writes only a test literal and its comment, so the mutation lane draws no production mutant.
- Step 13: git merge-tree --write-tree origin/main(22615537a) f2f204fc3ed608a69b56ee9ebc0c2eee23e74dc1 exits 0 (ev/merge_tree.txt). Newer main touches nothing the lane reads (custom_components, tests/replay.py, tests/hastub, tests/stress.py).
- Step 14, the raise:
  - Architecture score dS +0.0000 NULL, reproduced, and tests/structure.py prints STRUCTURE RATCHET PASSED (ev/structure_archscore.txt).
  - Remove the mechanism and the movement goes: the cap's justification is the measured spread, and the literal alone moves the gate (see the mutation proof). It is not a score movement.
  - Payments: I hunted for one the body missed and found none that improves code inside this PR's scope. Loop-CPU work belongs to R10-LOOP-CPU. A paired reference changes what the lane measures and is carried to R10-REPLAY-LANE.
  - Mandate 6175172275 (scope all) is named in the roster's owner_gate. I did not read the mandate comment itself.
- Step 15: the added lines are a literal and its comment. There is no architecture concern.

Non-blocking nit: the PR title still reads "re-record loop_cpu_ratio at 0.120". The value is 0.143. pr-contract does not refuse it.

bus-nonce: 2246ae046f7e4d4683a374de41c516aa
