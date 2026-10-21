Fix review: blocked daac94b439baf15b1ce8ea6c39bc73731eb076c6 claim-refuted: the head's own replay lane reads loop_cpu_ratio 0.1206 over the new 0.120 cap on an idle 4-core box whose ruler is slower than either CI class, so the runner-class model and 5.0 % noise band the cap rests on do not hold out of sample

Round: first review of this PR (round 1).
Measured head: daac94b439baf15b1ce8ea6c39bc73731eb076c6 (re-read on origin before writing this, still the head). Merge base 6961f06637964001a2ed544e495ea0312eeefa37.
Group: R10-REPLAY-CAP. Brief read from origin/handoff/audit-r10-roster (65b6b9cf1). Finder harness: dev/audit/harnesses/r10_replay_loopnorm.py (committed on main by #2339/cdec077ac). The brief names no other harness.
Environment: Python 3.13 venv with tests/requirements-ci.txt's pinned versions (hashes dropped; the system python 3.11 lacks voluptuous), 4 cores, load average 0.5-0.9.

## Blocking

Step 6 (attack at other configurations) and step 8 (re-derive every quoted number).

RESULT replay_lane_head tests/replay.py at head: cost loop_cpu_ratio 0.1206 loop_ref_ms 178.3 -> FAIL cycle_cost [loop_cpu_ratio 0.1206 over its budget 0.12]; 1 of 93 replay checks FAILED (ev/replay_head_full.txt)
RESULT finder_head_n8 new=min0.1094_max0.1184_factor1.082 median0.1163 loop_ref_ms 172.7-190.1 (ev/finder_harness_head_n8.txt)
RESULT finder_both_ends interleaved 3 rounds: base 0.1121 0.1089 0.1118 / head 0.1170 0.1109 0.1206 (ev/finder_harness_both_ends.txt; the code is identical at both ends, only the literal differs, so this is the box's own spread)

All 12 readings fall in 0.1089-0.1206 (factor 1.107). The median, 0.116, is above both CI red rows.

What this refutes in the body:
- "The cause is the runner class ... the ratio rises by about 1.28x on a fast runner" (corr with loop_ref_ms -0.72, n=6). This box's ruler is slower than any CI row (about 178 ms, against 79-84 on the fast class and 128-161 on the slow class), yet it reads the fast-class figure or higher. The ratio does not follow ruler speed out of sample, so the "fast-class factor" is not the variable that sets the figure. That leaves the cap without a model of which runners it holds on.
- "the measured within-run noise band (5.0 %)" is the cap's sizing. On one idle box, the spread across runs is 8.2 % over n=8 and 10.7 % over n=12. The 5.0 % comes from comparing a clean arm with a memory arm inside one job, and it does not bound how the figure varies between runs.
- The null control reads 0.0854-0.0869 at load 30-60 on the fixer's box. Here, at load under 1, the same main tree reads 0.109-0.112, and so does the base. The body's local figures do not reproduce, and the figure moves with the box (and possibly with load) by more than the headroom the cap leaves: 0.120 is 0.5 % above this box's maximum on the clean code and 3 % above CI's memory-arm 0.1162.

So the cap does not do what the PR says it does: it is the largest observed row plus a band the data does not support, and it goes red on the next runner that differs. It does not keep nightly-status green on more than the two runners already seen.

What would pass: size the cap from the figure's spread between runs rather than from the clean/memory pair, or do payment 5 (a ruler that removes the factor, or a per-class band) here instead of carrying it. Either must be shown on a runner outside the series. This box's readings are in ev/ for that.

## Verified (these hold)

- Step 1, mutation proof (ev/mutation_proof.txt), run through cost_offenders on the CI 2026-10-21 cost line: head 0.120 -> []; mutant 0.111 -> 'loop_cpu_ratio 0.1138 over its budget 0.111'; mutant 0.113 -> over; mutant 0.25 -> 'cannot see a 2x cycle; re-record 0.1609'. Every band reading in the body is clean, and its doubling is over 0.120 (lowest 0.1236). replay.controls() all pass.
- CI red rows, re-derived from the job logs (ev/ci_red_rows.txt): run 39387919507 has 0.1114 at loop_ref_ms 84.05 and a memory arm of 0.1162. Run 39563978649 (job 119101702593) has 0.1138 at loop_ref_ms 79.44 and a memory arm of 0.1081, a deviation of 5.0 % (0.1138 x 1.05 = 0.1195 -> 0.120). Both loop-doubled arms (0.2616, 0.2264) are over 0.120, so detection holds on CI.
- Not re-derived: the other four clean/memory pairs, and the --series line (gh is unauthenticated here). Nor the fixer's 15-run interleaved bisect (my box cannot reproduce its level, see above).
- Step 4: no fixture or claim file is in the diff (ev/diff_stat.txt: tests/replay.py and dev/programme/delivery/2548.md only).
- Step 5: VERSION (7.0.2), the manifest and RELEASE_NOTES.md are untouched.
- Step 6, class: the body names no enumeration rule. The issue states one seam, the loop_cpu_ratio literal, so the class is one seam.
- Step 7: the body's head is daac94b439baf15b1ce8ea6c39bc73731eb076c6.
- Step 10: the forward-carry to R10-REPLAY-LANE is present in origin/handoff/audit-r10-roster at 65b6b9cf1, and it states its control as a precondition (record from both CI classes).
- Step 11: nightly-status is red because the 2026-10-21 scheduled slow lane failed on main. The body names it and answers it, and it is main's. pr-contract (two runs) and budget-raise-gate succeeded. Still in progress when read: coverage, and Analyze (python). Every other check concluded success, skipped or neutral.
- Step 13: git merge-tree --write-tree origin/main daac94b439baf15b1ce8ea6c39bc73731eb076c6 exits 0 (ev/merge_tree.txt).
- Step 14: architecture score dS +0.0000 NULL, reproduced (ev/archscore.txt). tests/structure.py: STRUCTURE RATCHET PASSED. The mandate (6175172275) is named in the roster's owner_gate. I did not read the mandate comment itself.
- Step 9: I built no harness. The finder's harness ran unmodified; its --self-test gives checks=7 failed=0.

bus-nonce: a750134988b08f27aa567c2e73c5fce0
