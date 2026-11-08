Fix review: merge 9353e700abb65ba3b46460c1e02bfd1c67e1760d

bus-nonce: 925e3ba7f305cace1acee7bf2b3f44b4

## Round

Second round. Round one (verdict/3317, at 4bfb5d134a0d5fe0c8bbc716b41ca981d24dbbe1) was blocked carry-unmet over carry 12's unanchored `unpinned site` alternative. This review covers part 3 of R10-HANDOFF-PATH at head 9353e700abb65ba3b46460c1e02bfd1c67e1760d, from a detached worktree. Its tree equals 023e49d500a75a9500c99e5c9176babb9cd71a01, the code head the body measured (`git diff` is empty). The head was the same at post time (ls-remote, ev/HEAD.txt).

## Findings

- Follow-up: carry 8's BUSY (75) exits for "branch checked out elsewhere" and "worktree holds unpushed commits" now reach the relay's busy arm. That arm retries on every pass and writes no level line. A condition that never clears is therefore retried forever with nothing owed: a human's stale worktree on the branch, or a crashed opener's unpushed row commit. Before this PR, that condition surfaced as an OWED handoff-update line. Carry 8 prescribes "retried next pass and never recorded", so this is no defect against the carry, but the visibility loss needs a bound: an age or pass count after which a BUSY of these two kinds is owed with its reason. The lock BUSY already has a STUCK andon for this.
  Carry: R10-HANDOFF-PATH
- Follow-up: carry 6's third clause ("the sweep's disk floor names which checkouts it could collect") is answered by citing the beat's `disk` row (`tools/audit/seat/beat_jobs.py:506-515`), as round one asked. That row's line names only the free GiB and worktree_gc's rc, not any checkout. The body says "the per-PR checkouts are among what it collects", but `tools/audit/worktree_gc.sh` collects only a MERGED PR's branch worktree, or a detached one whose HEAD is a proper ancestor of origin/main. An open PR's `upd-<branch>` checkout is therefore never collectable below the floor. The naming half of the clause is still unbuilt.
  Carry: R10-HANDOFF-PATH
- Follow-up: the `mut:unlock` arm's determinism rests on a `sed` that rewrites `time.sleep(0.2)  # mut:watch` in the copy, and nothing checks that the substitution applied. If that line is ever reworded, the sed does nothing and the arm silently returns to the racy 0.2 s window it was meant to retire. The arm should grep the copy for `time.sleep(30)  # mut:watch` after the sed, or `ck` on it.
  Carry: R10-HANDOFF-PATH
- Surviving mutant: deleting update_pr.sh's `git -C "$WT" merge --abort` line before the reuse leaves `pr_args self-test: 194 checks, 0 failed` (ev/mut-noabort-prargs.txt). The mutant is equivalent. `git checkout -f -B` already clears MERGE_HEAD. I checked that on a throwaway repo: MERGE_HEAD exists after a conflicted merge and is gone after `checkout -q -f -B x master`, rc 0. And pr_release_wt's abort is pinned by the existing `mut:mergeabort` arm.
  Carry: dismissed: equivalent mutant, the checkout -f -B that follows clears the merge state, verified on a throwaway repository

## Evidence

- RESULT CI: `merge_train.py classify 9353e700abb65ba3b46460c1e02bfd1c67e1760d --pr 3317` exited 0 on its first run and printed `GREEN 9353e700abb65ba3b46460c1e02bfd1c67e1760d pending: none red: none` (ev/classify.txt, ev/classify.log). `get_check_runs` lists 68 runs in one page of 100, each `success` or `skipped`, with no concluded red, so step 11 owes nothing. The body answers its local prepr `closures` refusal as the sandbox's `tests/entities.py`, and CI's `tests / closures` is green.
- RESULT merge: `git merge-tree --write-tree origin/main 9353e700` against origin/main 17e621f08c4feec724478573741fbd8b596ceaba gives rc=0 with no conflict (ev/merge-tree.txt).
- RESULT self-tests at the head: `cloud_relay self-test: 381 checks, 0 failed` and `pr_args self-test: 194 checks, 0 failed`. Both match the body's figures (ev/relay-head.txt, ev/prargs-head.txt). My first pr_args run went to the wrong checkout through a shell-precedence slip. It gave 184, from the base tree, and I discarded it. The file holds the rerun at the head.
- RESULT relay mutants. Each is my own copy with one line changed, run through the whole cloud_relay self-test:
  - `mut:retryall` gives 6 failed, (b) among them (ev/mut-retryall.txt).
  - `mut:trylimit` gives 1 failed: (c) (ev/mut-trylimit.txt).
  - `mut:backoff` gives 2 failed: "a failed update is tried once" and "the backoff holds..." (ev/mut-backoff.txt).
  - The round-one line restored, unanchored (`(unpinned site|carry|pr-body|figures|brief)`), gives 1 failed: "(d) a ci-predict refusal whose output also holds the unpinned-sites skip line is rerun". That is the body's claimed red (ev/mut-unanchored.txt).
  - The key reverted to `<topic> <hs>` (carry 8) gives 4 failed (ev/mut-oldkey.txt).
- RESULT pr_args mutants. The arms built into the self-test read each mutant red: `colremove`, `opcollect`, `elsewhere`, `updreusewt`, `unpushed` (BUSY 75) and `unlock`. All are `ok` in ev/prargs-head.txt lines 104-173. My own mutants:
  - `clean -fdq` dropped from the reuse gives 2 failed: the reuse arm and the `mut:lock` arm. The second is because its "live" marker is now cleaned rather than removed with the worktree, so it still reads the in-flight clobber (ev/mut-noclean-prargs.txt).
  - Null control for carry 19 (ev/mut-sednull-prargs.txt): the 30 s poll applied to the UNMUTATED detrun too still reads "the lock holder has exited by the time a run returns" ok, 194/0. The arm is not vacuous: the `mut:unlock` line's USR1 and wait end the holder, not its poll.
- Carry 12 classifier, attacked on prepr's real output shape. `say` prints `  REFUSE   <step>` at the line start. `refusal_lines` prefixes the log lines it replays with `    | `, so a nested REFUSE cannot match `^[[:space:]]*(update_pr: )?REFUSE`. The content alternatives map to real step names: `unpinned sites`, `carry`, `pr-body`, `figures`, and `brief` (prefix of `brief_lint`). A run with both a content REFUSE and a retryable REFUSE is recorded at once, which is right, because its body must move anyway.
- Cheap checks at the head: `STRUCTURE RATCHET PASSED`; `ALL 296 checks PASSED` (doc_claims); `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` with RUN tests/doc_claims.py. All match the body (ev/cheap-checks.txt).
- Untouched: the three-dot diff (6 files) leaves `VERSION`, the manifest, `RELEASE_NOTES.md`, every `*_budgets.json`, `tests/closures.json`, `tests/closure.py` and both claim files alone. The only new tracked file is the delivery row `dev/programme/delivery/3317.md`.
- Roles: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Round-one findings: the key-change disclosure is now in the body under Carry 8. Carry 6's floor is now dispositioned with the instrument cited; its remaining gap is under Findings.
- Group brief read at origin/handoff/audit-r10-roster: carries 6, 8, 12, 19 and 40. The body's carry answers for 0-5, 7, 9-11, 13-18 and 20-39 cite earlier parts' commits or dismissals, matching the roster marks.
- Finder's harness: none is named (the packet says "none named"). The throwaway MERGE_HEAD check and the sednull, noclean and noabort copies are my own instruments, built for this review.
- The body's old-rate figure for carry 19 (1 in 9 concurrent, 22 of 22 chained) is not re-derived, and the body says so: the arm no longer depends on that window.
- PR body used for carry_audit: ev/pr_body.md, the handoff-body ref's BODY.md. The live body differs from it only by the `## Head` sentence naming 9353e700.
