Fix review: merge 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b

bus-nonce: 75efa4ed1fae707601d6c800030da7e6

Round 2 of this review (answers the round-1 block at ec36f34aa, class-open on approval_owed). Head measured: 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b, from detached worktrees at that SHA and at the merge base e4c9e2016a455d787d3a7604ef88c803c3ba5c70 (origin/main's tip; the branch is 0 behind). The head was re-read after CI concluded and is unchanged (ev/check_runs.txt, ls-remote). Role files: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Findings

None. Round 1's O1 (the over-fire) and O2 (surviving mutant R5) are both settled at this head (Evidence 1, 2).

## Evidence

1. Finder's harness (round 1's verdict/3073 evidence/overfire.py, copied unchanged to ev/finder_overfire.py).
   - At this head it reads every case RED rc 1, the #3045 control included (ev/finder_overfire_both.txt). That is because it stubs no gate-log read, and `gate_raise_only` fails closed on an unread log. At the base, the round-1 base variant reads all RED rc 1 (ev/finder_overfire_at_base.txt), since the base has no `--pr` path.
   - So the finder's harness alone cannot show the control at rc 4. I extended it myself (ev/reviewer_overfire_logs.py; it is reviewer-built and is neither the finder's nor the fixer's). It keeps the same cases and adds a gate job log carrying the reasons tools/ci/gate.py prints for each shape. It also plants every other FAIL path in gate.py's `gate()`, `judge()` and `main()`.
   - Results at the head (ev/reviewer_overfire_logs_head.txt):
     - control #3045 shape: rc=4 APPROVAL-OWED
     - SKIPPED, ABSENT and in_progress: rc=1 RED
     - `tests / browser` failure: rc=1 RED
     - every null control: rc 1 RED, plus the two designed owed shapes from round 1 (an approval on an older head, and a non-gate red) at rc 4
     - each of these FAIL paths reads rc=1 RED: prelude not success, the prelude cross-check, the attempt cap, both workflow_dispatch reasons, PR unreadable, fork head, the deferral bound, unreadable run title, "no run at this head judged base", ApiError, the raise unit cancelled, the raise unit SKIPPED, the raise plus another unit's failure (in either order), RATE-LIMITED, and an unreadable (410) log
     - the raise failing in an earlier run (`failure (run 123)`): rc 4, which is correct
   - The fixer's companion (dev/audit/harnesses/r10_fly_raise_reviewable_overfire.py) agrees at the head (ev/selftests_head.txt).
   - Hunting a further shape: every FAIL path prints `FAIL <why[0]>` followed by why[1:], and only `budget-raise-gate / budget-raise-gate: failure (this run|run N)` matches RAISE_REASON. I found no other gate.py reason that reads APPROVAL-OWED.
2. Mutants against the new predicate (ev/mutants_round2.txt). Baseline: `merge_train.py --self-test` at the head gives 417 checks, 0 failed (ev/merge_train_selftest_head.txt).
   - KILLED:
     - N1, dropping the `gate_raise_only` call (8 rows red: SKIPPED, ABSENT, PENDING, deferral, prelude, raise-unit SKIPPED/PENDING, unreadable log, every suite read)
     - N2, `all` changed to `any` (the SKIPPED, ABSENT and PENDING rows)
     - N3, dropping the pending-suite guard
     - N6, reading only the first red suite
     - N7, `return True`
     - N8b, an unread log read as raise-only
   - Equivalent over gate.py's output grammar:
     - N4 (drop `out[0] != "fail"`): a RATE-LIMITED line never matches RAISE_REASON.
     - N5 (RAISE_REASON keeps `: failure` but drops its `(this run|run N)` suffix): no GitHub conclusion other than `failure` begins with "failure", and gate.py always appends `(this run)` or `(run N)`.
     - N8 (an unread log read as `fail ["x"]`): "x" does not match.
     - N9 (accept empty reasons): `gate_outcome` always returns at least the FAIL line's own text.
   - The body's MG (RAISE_REASON widened to `.*`) is a different mutant, and the raise-unit SKIPPED/PENDING row kills it.
   - Round 1's R5 is now pinned by the `#3073 O2` row (diff at rc 128).
3. Readers on a raise-only red, at the head (ev/readers_rows.txt, ev/bus_selftest_head.txt, ev/selftests_head.txt). All behave as before:
   - review_packet: 65/0, including the P345 advisory-instead-of-refusal row and its rc-4-only nulls.
   - orchestrator_tick: 243/0, including the `P345 PRS` rows. The tick routes the gate-log read through its own gh (`_approval_owed`), and its #3073 SKIPPED null is present.
   - cloud_dispatch: 124/0 (the reviewer waits on `classify --pr` until 0/1/2/4).
   - bus.sh: 115/0 on Linux bash. The P345 dispatch-on-rc-4 row and every P348 row pass.
   - review_carry: 26/0.
   Carry: dismissed: evidence, not a finding
4. Real heads (ev/real_heads.txt, ev/real_head_3045.txt).
   - Null #3055 at 6a988a23 with `--pr 3055`, through the body's harness: `RED ... red: gate`, rc=1.
   - #3045 at 9ef51b82 now carries 120 check runs. That is more than one page, which the body's single-page shim cannot read in this seat: REFUSE rc 2, and at the base too, so this is transport and not the PR.
   - With my own page-stitching shim (ev/real_head_pagesshim.py, reviewer-built), #3045 now reads `GREEN ... red: none` at both base and head, because its raise has since been approved and its gate re-run green.
   - So the body's F10 live control (APPROVAL-OWED rc 4 at 9ef51b82) cannot be re-derived now: its input moved. The self-test row 1 and the log-carrying harness above stand for that shape.
5. Merge-resolution delta (ev/resolution_delta.txt, ev/resolution_cc.txt, ev/merges_cc.txt).
   - `git show --cc 03ef99f28` has combined hunks in two files only: tools/audit/seat/review_packet.py and its instrument page. The only line taken from neither parent is `"branch": branch, "unlanded": unlanded,` beside the branch's `"approval_owed": owed` in `gather()`'s dict, which is the union of both sides.
   - Every other hunk is either main's (carry-landed, head-note repair, SELF_AUDIT) or the branch's (the approval_owed wiring) unchanged. The instrument page is likewise the union of both sentences.
   - 325b1fd11 and 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b have no combined hunks (clean merges).
   - Self-tests re-run at the head: review_packet 65/0, merge_train 417/0.
6. Merge: `git merge-tree --write-tree origin/main(e4c9e2016) 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b` gives rc=0, tree 7b42e3a7446e2438c7f5297e4dbe087709769f05, with no conflict and no MERGE-CLAIM line (ev/merge_tree.txt).
7. CI at this head:
   - `merge_train.py classify 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b`: `GREEN ... pending: none red: none`, rc=0 at 16:15 UTC (ev/ci_classify.txt).
   - The check-runs API read in full (two pages) gives total_count 55: 38 success, 17 skipped, none red. That includes both `gate` suites, both `pr-contract` runs (which therefore checked this body), both `budget-raise-gate` runs and `governance / instrument-self-tests`, now green after #3086 (ev/check_runs.txt).
   - Nothing is red at the head, so ## Red checks owes nothing for it. The three reds that section lists are at the earlier head 27ae023c, each answered there.
8. Standing items (ev/gate_checks.txt, ev/tree_standing.txt):
   - `tests/structure.py`: STRUCTURE RATCHET PASSED. No `*_budgets.json` is in the diff.
   - Scoped gate: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
   - `policy_lint --budgets`: rc 0, with orchestrator.md at 294/295 lines and 4245/4251 tokens.
   - `rules_sync --check`: RULES-SYNC ok.
   - Claim files, VERSION, the manifest and RELEASE_NOTES.md are untouched three-dot.
   - Delivery row dev/programme/delivery/3073.md is present.
   - tests/closures.json adds exactly the three new harnesses to INERT.
   - The body's ## Head names 828b6e8ce5b5b646d0c291ee3998b8e284e26f4b.
9. Class rule (F12): the readers the rule returns are the CLI, the tick, bus.sh, review_packet and cloud_dispatch. The first two call `approval_owed`, which now owns the red set and the gate-log read. The other three go through `classify --pr`. The diff leaves the merge path untouched (`classify` without `--pr`, `wait_ci`, `main_green`).
10. Forward-carry: the body says none, and no finding here changes a later stage. orchestrator.md's clause is a policy change that merges only on the owner's approving review, or the orchestrator's under mandate 6329234399, at the head, as the body's ## Approval states. That condition stands at merge and does not block this verdict. Carry: dismissed: evidence, not a finding
11. Not re-derived:
    - the body's macOS entities figures, F13's archscore dS +0.0000 and F14's pre-merge 53/398 counts. CI's green `arch-score` and `tests / closures` runs stand for the first two.
    - the `prepr.sh` rc=0 line.
