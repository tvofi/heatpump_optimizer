Fix review: blocked 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1 carry-unmet: carry 12's named retryable ci predict refusal is classed body-content by the bare unpinned-site alternative, so it is never retried

bus-nonce: 2a38e07315c82c180a620f043204f1c8

## Round

First round. This review is of part 3 of R10-HANDOFF-PATH, at head 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1. The head is unchanged at post time (ls-remote).

## Block

- Carry 12 is not delivered for the case it names. `tools/audit/seat/cloud_relay.sh:619` classes a refusal as body-content when `grep -qiE 'REFUSE[: ]+(unpinned sites?|carry|pr-body|figures|brief)|unpinned site'` matches anywhere in the whole `update.out`. The second alternative, a bare `unpinned site`, has no `REFUSE` anchor. A full prepr run prints a step line for unpinned sites on every run that gets past its early exits. That line reads `skip unpinned sites ... the diff adds no unpinned mutation site`, `ok unpinned sites ...`, or `WARN unpinned sites`: `say` writes it to fd 3, which is app_push's inherited stdout and so lands in `update.out`. The `ci predict` step (prepr.sh:4453) does not exit; `step` only sets rc. So the run always reaches step 7d (prepr.sh:4603) and prints that line, and every `ci predict` refusal is recorded at once, never retried. The same holds for closures, mutants, policy_lint and every other late step. Carry 12 names `ci predict` explicitly as a retryable class. Only the early-exit `ancestry reds` (prepr.sh:4098) escapes, and that is the only class the fixture exercises: its `rt.sh` stub prints one REFUSE line, not prepr's real output. Reproduction, using the production regex read from line 619 at the head: `ev/regex_demo/RESULT.txt` gives `ci_predict_refusal.out content` and `early_ancestry.out retry`. Remedy: classify only on the step names of `REFUSE` step lines, and drop the unanchored alternative. Add a fixture arm whose stub prints a prepr-shaped `REFUSE ci predict` run that includes the unpinned-sites skip line, and show that arm red against today's line.
  Carry: R10-HANDOFF-PATH

## Findings

- Carry 6's third clause ("the sweep's disk floor names which checkouts it could collect") is left unbuilt. The body's reason for that is wrong: it says "no such floor instrument was found in the tree", but the instrument exists. It is `tools/audit/seat/beat_jobs.py:77`/`:490` (the beat's `disk` row with `disk_floor_gib`), which runs `tools/audit/worktree_gc.sh`, and it is documented at `tools/audit/seat/sweep_template.md:48,87`. The re-cut owes either that naming or a disposition that cites this instrument.
  Carry: R10-HANDOFF-PATH
- Follow-up: the relay key changes from `<topic> <hs>` to `<topic> <hs> <bs>` for non-body-only failures, so existing two-field entries in `cloud-handoff-failed` stop matching. Each such topic is rerun once on the first pass after deploy. Carry 8 wants that, because the reasons of the 28 measured entries were unrecoverable, but the body does not state it. Disclose it in the re-cut body.
  Carry: R10-HANDOFF-PATH

## Evidence

- RESULT CI: `merge_train.py classify 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1 --pr 3317` printed `GREEN 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1 pending: none red: none` with rc=0 (ev/classify1.txt). There is no concluded red at the head, so step 11 owes nothing. The body's local prepr `closures` refusal is answered as the sandbox's.
- RESULT merge: `git merge-tree --write-tree origin/main 4bfb5d13` against origin/main 6188936a gives rc=0 with no conflict (ev/merge_tree.txt).
- RESULT self-tests at the head: `pr_args self-test: 189 checks, 0 failed` and `cloud_relay self-test: 380 checks, 0 failed`. Both match the body's figures (ev/pr_args_selftest.txt, ev/cloud_relay_selftest.txt).
- RESULT mutants (my own copies, the marked line deleted, run against the whole cloud_relay self-test). `mut:retryall` gives 6 failed, among them (b). `mut:trylimit` gives 1 failed, (c). `mut:backoff` gives 2 failed: "a failed update is tried once" and "the backoff holds...". All three are killed as the body claims (ev/mut_*.txt). The pr_args mutants (`colremove`, `opcollect`, `elsewhere`, `updreusewt`, `unpushed`, `unlock`) are arms built into the self-test, and 189/0 reads each one red on its mutant copy.
- Untouched: the three-dot diff leaves `VERSION`, the manifest, `RELEASE_NOTES.md`, `*_budgets.json`, `tests/closures.json` and `tests/closure.py` alone. No claim files are moved.
- Roles: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Carries 8 and 19/40 read sound. update_pr exits 75 through `pr_busy` on both named stops. The relay already retries 75 on its next pass. The `mut:unlock` arm now awaits the holder within a bound. The 1-in-9 rate is not re-measured, and the body says so honestly.
- Group brief read at origin/handoff/audit-r10-roster 9fd3d6a250dd040de54931e3d2da282dc77f0cc1, carries 6, 8, 12, 19 and 40.
- The finder's harness: none is named (the packet says "none named"). The demo in ev/regex_demo is my own instrument, built for this review.
