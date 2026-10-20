Fix review: merge 07db35124d69251ad755baffc61460e833e67d88

Round 3. Round 1 blocked 4d1730bd1 (control-failed); round 2 blocked c4a357e5e (root-cause-unanswered). The next round is the fourth, and from there `fixer.md` owes a re-cut, not a repair.

Measured head: 07db35124d69251ad755baffc61460e833e67d88. It was still the PR head when I wrote this. The authored code head is dd3a44474. Both merges above it are exact automatic merges: bebb85c54's tree equals `merge-tree(c4a357e5e, dd3a44474)` (00c7e15d), and 07db3512's tree equals `merge-tree(bebb85c54, 52011c69a)` (a5397abd). The main merge touches none of run.sh, entities.py, ci_ratchet.py, coverage_tree.sh, ci.yml or the harnesses. `roles/` is unchanged against origin/main.

## RESULT lines

RESULT ci_head Tests run 39358539208 (pull_request, 07db3512, `MODE: FULL`). `fast (3.14)` (check run 118419093330) passed, 02:22:46Z to 03:14:58Z. Every check run concluded success, skipped or neutral, with none red; composed-proof was the last to finish, at 03:34:44Z, with success (ev/check_runs_head.txt, ev/composed_proof.txt).
RESULT a_sysid **Confirmed.** This head's FULL fast log reads `sysid_estimator_frontier.py: cpu=141.9s of the 480s bound` and `ALL 109 HARNESS HEADER CHECKS PASSED`. The base band is 142.5-164.0, so 141.9 sits 0.6 s below its floor and not above it. The round-2 PR-layout readings were 199.6, 149.1, 231.0 and 306.4, so co-running is not refuted as the cause. harness_headers.py ran alone: it started at 03:12:05, after stress.py (03:07:26-03:12:05, 279 s), and the parallel lanes ended at 03:07:26. Its wall time was 167 s, against 188 s on base push job 118257300582 and 411 s at round 2 (ev/excerpt_fast_head_job_118419093330.txt).
RESULT b_saving **Measured 5.18 min against the 5.0 bar: passes on this run.** The fixer's projection of about 4.5 min was pessimistic.
- The body's instrument `r10_ci_layout_p0_fast_offsets.py --after 39358539208` reads queue 0.45, dur 52.20, offset 52.65 against a before median of 57.83: `saved_offset=5.18 PASS` (ev/offsets_head_only.txt).
- My own `gh api` reader (ev/offsets_own.py) re-derives every figure: saved_offset 5.18, saved_dur 5.57 (ev/offsets_own.txt).
- Over all five PR-layout runs, the median offset is 52.65 and saved_offset is 5.18 (ev/offsets_all5.txt).
- **Caveat: one pull_request run against push runs.** lane_golden is now the critical lane. It ran env_drift `--all` 339 s, arch_score 2256 s and arch_score_head 42 s, ending at 03:07:26, while lane_units ended at 02:59:06. On push runs env_drift `--all` reads about 443 s (job 118257300582). The +104 s lands directly on the critical path, so a push run projects to about 3.4 min saved (my estimate, not a measurement).
RESULT b_body_option The body does not recommend the A3 fallback. It says the binding control "stays push against push (the window rule)". It routes the A3-versus-window choice to the orchestrator only if this head's FULL run misses the bar, and this run met it. So the body's position is: keep R(a) and let the post-merge window rule decide. I agree, given the push caveat above. The window rule, with a stop and re-measure after 6 push runs, is the right control. R(b), R(c) and the stub do not depend on it.
RESULT mutants_harness `r10_ci_layout_p0_mutants.py` at this head: M1-M8 are all KILLED on their aimed check, and M8 is killed by `the CPU-bounded harness check runs alone: in lane_stress after stress.py, in no parallel lane`. It prints `RESULT survivors=0`. M0 reads FAIL, 1 of 2358, with no aimed check red (ev/mutants.txt).
RESULT m0_environmental Each run's one counted extra red is `graders-head-copy's delivery_status step ...`. Rounds 1 and 2 showed it identical at main in this container type, and CI's entities is green at this head. The remaining `  FAIL` lines are planted controls from sub-harnesses.
RESULT reviewer_mutants_r3 My own instrument is ev/extra_mutants_r3.py: an exact-once substitution in tests/run.sh, then a full entities run.
- KILLED, on the aimed pin:
  - X6: harness_headers moved to the end of lane_golden.
  - X7: harness_headers placed before stress.py inside lane_stress.
  - X8: `stress` added to `LANES`.
- **SURVIVED:**
  - X9: the parallel launch loop iterates `$LANES stress` while the `LANES` string stays unchanged.
  - X10: the alone phase runs before the `wait` on the parallel lanes.
- Both survivors put harness_headers back beside the lanes, and only the environmental red shows (ev/extra_mutants_r3.txt).
- The pin reads text placement (function bodies and the `LANES` string), not the scheduler that makes lane_stress "alone". Neither line is in this diff. stress.py's own alone-ness was equally unpinned against X9 and X10 before this PR. That is why this is a note, not a block: see Non-blocking note 1.
RESULT lease_stub `_gl_stub_tree` gains a `harness_headers` stub because `lane_stress` now calls it. The lease test still drives `lane_stress` under jobs 1 and 3. I read it and it is consistent.
RESULT class_rule The body's rule `git grep -ln 'RLIMIT_CPU\|process_time\|getrusage\|thread_time' -- 'tests/*.py' 'tests/*.sh'` returns the 4 files the body names: harness_headers, replay, stress, structure. replay.py is on run.sh's not-a-test list, and structure.py only reports a factor. The class has no open seam.
RESULT scope `closure.py select` prints `MODE: FULL`, reason `.github/workflows/ci.yml changes the gate itself` (matches the body).
RESULT cheap_checks `STRUCTURE RATCHET PASSED` (ev/structure.txt). `bash -n tests/run.sh` returns 0.
RESULT merge_tree At origin/main 52011c69a: exit 0, tree a5397abd. Main then moved to bb5b21a88 (delivery-row records only): exit 0, tree f041f6b2. There is no conflict (ev/merge_tree.txt).
RESULT version_files The three-dot diff of VERSION, RELEASE_NOTES.md, the manifest and both claim files is empty.
RESULT red_checks Range: pr-contract 118419106293 (success) prints `record red-history ... closures, fast (3.14)`.
- The body's `## Red checks` names both:
  - fast (3.14), with cause, fix, cheaper detector and standing cost.
  - closures UNDER-SCOPED.
- It also names round 2's pr-contract red.
- No check is red at this head.
RESULT carries 1604c987 is on handoff/audit-r10-roster (its tip) and not on main.
- R10-CI-LAYOUT carry[13] (`Carried from #2464 ... at dd3a4447, round 3`) states the alone-phase obligation and its control, "the run-alone pin refuses otherwise".
- The R10-STAMP carry is present.
- pr-contract reads `CARRY-AUDIT: 3 routed, 0 unrouted` (ev/carries_1604c987.txt).
RESULT round2_notes **Window-rule wording: fixed.** The body reads "Five of the eight under the bar is enough, but not required".
**R10-STAMP carry line: fixed in the body but not on the roster.** The roster's R10-STAMP row at 1604c987 still reads "once the B4 window above reads green", and the STAMP stage has no "above" (note 2).
RESULT figures I re-derived these at this head or from their runs:
- the failing line at round 2 (306.4, in round 2's evidence);
- the 9 before offsets and the 57.83 median;
- the 4 earlier after runs, re-read through the body's instrument;
- the 49-check count at c4a357e5e (round 2);
- the 53 = 34 - 1 + 20 count (rounds 1 and 2; untouched since);
- the base harness_headers timings in job 118257300582: 20:09:01 + 188 s, env_drift `--all` 443 s.

I did not re-derive the round-2 job's "404 of 411 s overlap". Its endpoints (00:54:49 + 411 s; arch_score from 00:20:17 for 2476 s) are consistent with that figure but come from round 2's evidence, not my own read.

## Non-blocking notes

1. **The run-alone pin is a text pin, and the forward-carry overstates it.** The carry says any later lane edit, "PR 1's W1 or the umbrella's split of `tests.yml`", keeps harness_headers alone because "the run-alone pin refuses otherwise". X9 and X10 are exactly the scheduler-shaped edits such a split makes, and the pin does not refuse them.
   - Ask: the orchestrator should amend the R10-CI-LAYOUT carry before merge (`finding-propagation.md`). It should say the pin covers placement and `LANES` only. The stage that rewrites the scheduler owes a behavioural check that lane_stress starts after every parallel lane has ended.
   - Alternative: a later PR strengthens the pin, for example by driving run.sh's scheduler with stub lanes, as `_gl_run_sh_leases_stress` already does.
2. **R10-STAMP roster row.** It still says "the B4 window above". It should restate the window: the median wall time of the 8 newest completed push Tests runs is under 54.825 min.
3. **`## Head`** names `88e29a866989057c5da001ebeba275355a5af720`, which does not exist in the repository. This is the orchestrator script's defect again; round 2 found 6caa7842. The 07db3512 paragraph is correct.
4. **Watch item for the window rule.** On push runs the critical path is now lane_golden: env_drift `--all` (DRIFT_WARM_CACHE), then arch_score. The stage-one saving there projects below 5 min (est. 3.4). If the window stays red, look first at that lane, not at lane_units.

bus-nonce: 26509a33afa7ad7987a53f2f3edcf9a6
