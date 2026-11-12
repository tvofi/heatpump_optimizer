Fix review: merge bdc2e986fa5f8f72c7194c685b20b0c0041f66a2

bus-nonce: 9ecc51be47815ad4825be588b57e191d

Round 2, scoped re-check of the one point that blocked round 1 (verdict/3479 at de925f9c, blocked b6c080db harness-vacuous: carry 7 (PREPR-SLOT-LIVELOCK) null control cannot fail). Head measured: bdc2e986fa5f8f72c7194c685b20b0c0041f66a2 (ev/HEAD.txt). Body judged: BODY.md at handoff-body/r10-prepr-residue d51e17d637ec06c239f04daf3dbd569f6b99060b. No pull request, no review packet and no CI exist for this head yet; nothing was waited on. Everything else in the round-1 review stands and was not re-opened. The block is settled: the rebuilt harness's null control fails under perturbation, and its labelled arm fails under the mutant.

## Evidence

- RESULT harness at head (ev/harness_head.out): rc 0, 9.2 s; pool_full=1 outer_exported_label=1 nested_finished=1 nested_queue_empty=1 nested_joined=1 bare_finished=0 bare_queued=1 warn_no_label=1 warn_finished=1 selftest_branch_takes_slot=0, verdict=ok. Every figure in the body's `## Figures` harness line reproduces at this head.
- RESULT `--mutant` (ev/harness_mutant.out): rc 1, verdict=FAIL on outer_exported_label, nested_finished, nested_queue_empty, nested_joined; matches the body's mutation proof.
- Both ends: the head's harness run in a worktree at merge-base 046736a49f8c (tools/pr/prepr.sh and tests/gate_lock.py byte-identical to head) gives the same verdict=ok rc 0 and mutant rc 1 (ev/harness_base.out). The dismissal holds at main, as a "not reproducible" dismissal must.
- The bare arm now discriminates. At head, slot-status shows `queue=prepr-<pid>` for the bare arm and `queue=-` after the labelled nested arm. Round 1's objection (both arms only missed a bound) no longer applies: the arms differ by a queue entry.
- Perturbation P1 (ev/perturbations.out, ev/perturbations_guarded.out): adding `--no-wait` to take_slot's slot-take, so the bare arm cannot queue, turns the harness red (rc 1). With only the bare-arm killpg guarded, it reports bare_finished=1 bare_queued=0 verdict=FAIL. The null control can fail.
- Perturbation P2: forcing take_slot to always join (`if true; then` at prepr.sh:4259) turns the harness red: bare_finished=1, bare_queued=0, verdict=FAIL, rc 1.
- Perturbation P3: a bare `take_slot` line inserted in prepr.sh's `--self-test` branch gives selftest_branch_takes_slot=1, verdict=FAIL, rc 1.
- The harness no longer injects the label. The outer shell runs prepr's real take_slot (text cut from prepr.sh) against the real tests/gate_lock.py with 3 of 4 slots held, and the label comes from the real export. Step 3h at head (prepr.sh:4447-4448) is `take_slot` followed by heavy_run of `--self-test`. heavy_run (prepr.sh:813-825) passes the environment through unchanged, so the nested arm models what 3h's child inherits.
- Merge: `git merge-tree --write-tree origin/main bdc2e986fa5f8f72c7194c685b20b0c0041f66a2` at origin/main 2ced371c1af5 exits 0, with no conflict.
- Note on the dispatch: the earlier verdict measured b6c080db, and bdc2e986 is a later head that contains 79c063dcd (harness rebuild) and fe9beb2bf (repo_root inline). Those are the delta this re-check judged. The other delta lines come from main and are already reviewed there, and the round-1 scope stands for them.
- Red checks: none, because no check has run on this unopened head.
- RESULT carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body verdict.md --pr-group R10-PREPR-RESIDUE: CARRY-AUDIT 2 finding items, 2 routed, 0 unrouted, 0 bad destinations, rc 0.

## Findings

- Follow-up: the body's `## Null control` cites prepr.sh:4184 (the label export) and :4192 (the WARN path). Those are b6c080db line numbers. At bdc2e986 the export is prepr.sh:4265 and the WARN path is :4273, and 4184/4192 now land in the REUSE and transport code. The substance is verified as true at head, so only the line numbers are stale. Carry: R10-PREPR-RESIDUE | dismissed: stale line numbers only, the cited export and WARN path are verified at prepr.sh:4265 and :4273 of this head
- Follow-up: the static arm's regex (`^\s*take_slot\s*$|&& take_slot$`) misses `take_slot || true` and `take_slot; heavy_run x` in the `--self-test` branch: perturbations P4 and P5 stay green (ev/perturbations.out). This does not reopen carry 7, because the dynamic nested arm shows that any nested take_slot under an inherited label joins whatever its spelling. The static arm is supplementary. Carry: dismissed: supplementary arm; the dynamic nested arm covers every spelling, and prepr's own self-test row (prepr.sh:3674) pins the call count with a broader pattern
