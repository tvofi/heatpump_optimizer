Fix review: blocked a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737 carry-missing: the synthetic loop_cpu_ratio red-at-base finding is not on the roster, and the owner cpu_ratio 409.7 is centred on a reading the lane never takes

bus-nonce: 230908e69fe964bb8a80145f11bd7ab1

Round 1, full review of PR #3174 (R10-REPLAY-COST-BUDGET, issue 3129) at head `a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737` (authored code head 46a4a63c8afb, a main merge and the delivery row). Merge base 3905069f38a6, which is origin/main. I measured from detached worktrees at the base and at the head, using the finder's harness (verdict/3078 round 7 at 653019ace: ev/run_one.sh, ev/one60_head_null.summary, ev/my_mutants_r7.txt). The fix-review contract on main is unchanged since the merge base.

## Block

1. **carry-missing: not carried to the roster.** Under `## Forward-carry`, the body says the synthetic `loop_cpu_ratio` red at base on the faster-ruler class "Lands in dev/programme/rosters/wave-r10-groups.json (group R10-REPLAY-COST-BUDGET)". Neither the roster at e431aee1a nor the roster at f6df1ab5d (refs/heads/handoff/audit-r10-roster, re-read just before this verdict) holds that carry, in this group or any other. No carry file under dev/programme/carries/ holds it either. The group it names is also the one this merge completes, and once that group is done it is not a valid destination (finding-propagation.md, "Where it goes"). The finding itself is real, and I reproduced it: the base reads synthetic `loop_cpu_ratio` at 0.1686, 0.1871 and 0.1516 over 0.143 (loop_ref_ms 85-99), and the head reads 0.178-0.191 (ev/syn_summary.txt). The CI class reads 0.0907 (this head's replay job).
2. **The owner fixture's `cpu_ratio` 355.7 -> 409.7 is widened past what the lane ran.** The one reading over 355.7, 385.3, comes from the finder's `run_one.sh`, which ran `--step-minutes 60`: 4 cycles with `timed` 1, on a reviewer container, not a CI runner class. The lane runs the fixture's own interval: 16 cycles, `timed` 7. Every lane-configuration reading sits well under the old 355.7:
   - CI #3167: 240.69
   - CI at this head: 235.82
   - the fixer's box: 264.1
   - this container, base: 238.18
   - this container, head: 248.62

   I re-ran the finder's step-60 configuration at both ends. It reads 410.8 at the base and 320.2 at the head (ev/own_base_s60.json, ev/own_head_s60.json). That 28 % spread on identical cycle code is one-cycle noise. The base reading is over the new 409.7 too, so the raise does not even settle the configuration that motivated it. The body calls 385.3 "second CI class" and says its log "was not reachable". It was reachable: the roster carry names ev/one60_head_null.summary in verdict/3078, and run_one.sh beside it states `--step-minutes 60`. Either leave the owner entry at 355.7, which every lane reading supports, or record a step-60 budget separately from lane-config readings. Do not centre the lane budget on that reading.

## Findings

- The synthetic `loop_cpu_ratio` budget 0.143 is red at the base on a faster-ruler box (loop_ref_ms 85-99). I read 0.1516-0.1871 at base and 0.178-0.191 at head, while CI reads 0.0903-0.0907. It is not carried anywhere live. Precondition for the next stage: re-measure on both CI classes plus one box outside them, with a flat base-vs-base null, before any re-centring, and a raise needs tvofi. Carry: R10-REPLAY-COST-BUDGET
- The owner fixture's `cpu_ratio` budget 409.7 rests on a `--step-minutes 60`, single-timed-cycle reading that the lane never takes (Block item 2). Re-cut to the lane-config readings above. Carry: R10-REPLAY-COST-BUDGET
- #3167 cannot simply be re-run after this merges. `git merge-tree --write-tree a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737 7637d6634` conflicts in tests/replay.py at recorder_checks: this PR's unsupported-scheme block against #3167's `res.extend(_open_line_branches(...))`, and keeping both resolves it (ev/merge_3167_with_3174.txt). #3167 needs a main merge with that resolution, then a fresh replay job. Carry: R10-REPLAY-OPEN-LOG

## Evidence

- Head re-read just before the verdict: refs/pull/3174/head and fix/r10-replay-cost-budget both point at `a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737` (ev/head_recheck.txt). The body's `## Head` names this head.
- CI: `merge_train.py classify a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737 --pr 3174` printed `GREEN a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737 pending: none red: none` with rc 0 (ev/classify.txt, ev/classify_rc.txt). The full check-run set across all pages has no failure, timed_out or cancelled (ev/checkruns_final.txt). The replay job at this head reads `ALL 179 replay checks PASSED`: synthetic cpu_ratio 2.7543, owner cpu_ratio 235.8185 (ev/head_replay_job.log).
- Synthetic `cpu_ratio`: I ran 3 base and 3 head runs, interleaved, with `--fixture tests/replay/synthetic-dhw-only.json` on a 4-core container. Base read 1.9438, 2.3119 and 1.7035; head read 2.0738, 2.1686 and 2.0679. The base-against-base null is flat within box noise, and head matches base. Base run 2 already reads 2.312 over 2.173, so the old budget is red at base here too. The 2.81 is first-hand: #3167's replay job 125160076828 printed `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.81 over its budget 2.173]` (ev/pr3167_replay_job.log). I found no 2.615 in that job; it is a quoted figure I could not re-derive, and it is not an extreme, so it does not change the rule's output.
- The rule re-derived: sqrt(2) x sqrt(2.0 x 2.81) = 3.353, and sqrt(2) x sqrt(217.8 x 385.3) = 409.7. Both match the diff. Taking my lowest synthetic reading, 1.7035, as the extreme instead, the same rule gives 3.09.
- The new synthetic budget 3.353 still catches a real regression. The lane's own cpu-doubled arm read 4.77, 4.25, 4.36, 4.26, 4.18 and 3.96 here, and 5.70 (#3167) and 5.53 (this head) on CI. All of these are over 3.353. Its headroom over the highest clean reading, 2.81, is 19 %, which is not wider than the readings justify for a 2x detection (COST_DETECTION 2.0). A regression under about 1.6x on a slow-ref box would pass, which is the design's 2x intent rather than a defect.
- #3167's inherited red is cleared by this budget: 2.81 < 3.353, and this head's own replay job passes with 2.7543.
- Mutation proof (ev/mut_summary.txt; each mutant also carries the pre-existing loop_cpu_ratio red, which is the only other failure):
  - AWAY_COVERED misspelt as `owner-2026-10-30-awya.json` reads `FAIL AWAY_COVERED names committed fixtures [owner-2026-10-30-awya.json: declares away coverage but is not a committed fixture]`. Killed.
  - open_recorder's refusal as `f"the recorder URL {url} is neither SQLite nor "` reads `FAIL recorder:unsupported_scheme_refusal_prints_none_of_the_url`, with the canary password visible in the detail. Killed.
  - My own mutant, `away_covered_offenders` returning [], reads `FAIL control:away:covered_names_are_committed [bad=[] good=[]]`. Killed, so the control is not vacuous.
- Null for the pins: on the clean head, `ok control:away:covered_names_are_committed`, `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url` and `ok AWAY_COVERED names committed fixtures` all appear (ev/syn_head_1.txt).
- `git merge-tree --write-tree origin/main a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737` exits 0 with tree 722ada5b4 (ev/standing.txt).
- Standing checks:
  - The delivery row dev/programme/delivery/3174.md is in the three-dot diff.
  - Both claim files are byte-identical to origin/main.
  - There is no VERSION, manifest or RELEASE_NOTES change.
  - There is no `*_budgets.json` change.
  - No host path appears in the added lines.
- `## Red checks`: the head's own set has no concluded red, and #3167's inherited red is answered in the body.
- The owner `peak_kib` and `loop_cpu_ratio` entries are kept. My lane-config readings, 2603.4 / 2607.3 KiB and 0.2241 / 0.2296, sit inside 3740 and 0.249.
- I did not re-run the gate or the mutation table: these are CI's heavy runs, cited above.
