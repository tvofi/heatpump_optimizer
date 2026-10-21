Fix review: blocked c071fa5f37abdac0da2284547b9282549eb4d607 harness: class-rule-missing -- the body states three pusher seams and names no enumeration rule; tools/audit/seat/handoff_push.sh (live, named by HANDOVER.md) runs app_push.sh as an untrapped foreground child at lines 75, 94 and 108 and is neither in the diff nor dispositioned: TERMed, it leaves 4 of 4 tree pids alive

bus-nonce: 1253d5aed794d2d9b104a3b1dd1921e3

Round 1 (first review of this head). Head measured: c071fa5f37abdac0da2284547b9282549eb4d607; still the head at post (ev/head_at_post.txt).
Contract: dev/governance/roles/fix-review.md from origin/main (roles diff since merge base touches only orchestrator.md).
Finder harness: roster group R10-UPDATE-PR-SIGNALS (origin/handoff/audit-r10-roster, jq) carries no committed harness; its resume note gives the requirements (TERM/INT reap the whole tree, never a pattern kill, unrelated sleeper survives). The self-test arms are the fixer's; the class harness below is mine, disclosed as reviewer-built (ev/hp_shape.sh, ev/hp_fixed.sh, ev/stub.sh).

## Blocking

- harness: class-rule-missing. The body names open_pr.sh, update_pr.sh and app_push.sh ("each ran their push ... as a foreground child") and gives no rule that enumerates the pushers. My enumeration (callers of app_push.sh under tools/) returns a fourth: tools/audit/seat/handoff_push.sh, which has no trap and runs app_push.sh in a foreground pipeline at lines 75, 94 and 108. Its own header says it stays while dev/programme/HANDOVER.md names it, and HANDOVER.md:33 names it. Reproduced with that line's shape and preamble (set -uo pipefail, no trap) and the PR's two-level stub tree: after TERM the pusher is gone and 4 of 4 tree pids are alive (non-zombie), 3 of 3 runs. As a control, the PR's own mechanism on the same shape (pr_args.sh sourced, pr_signal_traps, async plus wait) leaves 0 of 4, 3 of 3 runs (ev/class_handoff_push_shape.txt). The PR's app_push.sh traps do not cover this case: app_push.sh never receives the signal. Repair: add handoff_push.sh to the diff, or disposition it in the body under a named rule. cloud_relay.sh (in the group's files; it runs update_pr.sh in the foreground) and merge_train.py's recarry subprocess are the other callers that rule must answer.

## Also open at this head (each must be fixed before a merge verdict)

- pr-contract is red at this head, both on the push-time run and on run 119202885071, which started after the last workflow concluded. carry_audit.py refuses 3 unrouted body items: ## Forward-carry "none ..." and both ## Friction lines (ev/pr_contract_carry_audit.txt). The body's "## Red checks: none" does not answer this. Because that run refused rather than checked the body, I do not post root-cause-unanswered. nightly-status is also red; it grades main, and this diff (tools/ scripts plus one delivery row) does not reach what it reads.
- Mutation gap, not named by the body. Deleting app_push.sh's pr_signal_traps call, or its EXIT pr_reap (amut traps / amut exitreap), fails nothing: app_push self-test is 135/0 and pr_args is 62/0. Nothing pins app_push.sh's own reap when it is signalled directly, and that is the seat the finding names ("closure.py record under a stopped prepr"). The pr_args.sh pr_signal_traps call (mut traps), the KILL escalation (mut grace) and both EXIT backstops (openexit, updexit) also survive. The traps call survives because the EXIT-trap backstop covers TERM. The KILL escalation is pinned by nothing.

## Verified

- Mutation proof (step 1). The deletion the body names, mut:stop in pr_kill, gives 62 checks, 2 failed, and the two failures are the named survivor arms. My extra mutants: recurse (no recursive walk) also fails 2. openfg (open_pr back in the foreground) fails 1. updfg (update_pr back in the foreground) fails 2, the reap arm and the lock arm. Logs: ev/mut_*.txt and ev/amut_*.txt. The preprfg app_push mutant is my own construction artifact (59 failures, crash-shaped) and is not evidence.
- Failing test first. The head's arms against base production (base open_pr.sh, update_pr.sh and app_push.sh, with pr_trap installing no signal traps) give 62 checks, 3 failed, the three the body names. At the head: 62/0. The base's own self-test is 56/0.
- Figures re-derived at this head. MODE: SCOPED -- 0 script(s) run, 33 scoped out. pr_args self-test 62/0. app_push self-test 135/0. STRUCTURE RATCHET PASSED. claims hygiene ok (against merge base 6961f066). tmp_paths: 0 refused, 0 stale. I did not re-run "ALL 124 closure shrink pins": not verified.
- Carry (step 7/12). The body measured 9719443b. The PR's tools/ diff at 9719443b and at the head is byte-identical, and so are all four file blobs (ev/carry.txt). The only other change is the delivery row.
- Steps 4 and 5. No claim files, VERSION, manifest or notes heading touched.
- Step 13. git merge-tree --write-tree origin/main c071fa5f37abdac0da2284547b9282549eb4d607 exits 0 (ev/merge_tree_final.txt).
- Null control. The unrelated sleeper survives TERM and a successful run, in the fixer's arms; the reap goes by pid only, with no pkill or group signal in the diff.
