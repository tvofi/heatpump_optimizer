Fix review: blocked 0fd9bc6da6a5f562c7104c1e4d921189f492cff1 mutation-vacuous: outside_intake.py one_thread review-comment read for a pull request survives the self-test

bus-nonce: fda2562f99fc192a50f4ddbd7f39ea73

This is round 3 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head 0fd9bc6da6a5f562c7104c1e4d921189f492cff1, the merge of 9ffed3f2a and main. I worked from a detached worktree at that head and used a second worktree for the mutants. The merge base is 294a880dae608502b62055775e34a5db93217b98. origin/main is be813ecd4924865b75489f12c56600e9432d5727, and `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current. Round 4 would owe a re-cut (`fixer.md`). This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The round-2 block is cured. Commit 9ffed3f2a deleted the guarded `last_out` move in `Thread.mark`, and the self-test's new `thirdbot_moves_out` mutant kills the unguarded form. The brief also asks for the mutation proof to be re-run on every changed line. `tools/audit/seat/outside_intake.py` is new in this PR, so every one of its lines is a changed line. I ran 47 mutants and counted case failures only (`outside_intake_selftest.run(False)`), the counting the fixer adopted in this round. One non-equivalent mutant on the thread reader survives:

- **`one_thread_pr_reviews_drop`.** Changing `if r["kind"] == "pr":` to `if False:` (L210) drops the read of a pull request's review comments. The cases-only self-test stays rc 0.
  - The mutant is not equivalent. In the self-test's own fixture world, `listing` prints `OUTSIDE #3240 owed=triage comment by=reviewer-x`, an outside review comment on our PR.
  - At the head, `dispose(..., 3240, ..., "not in scope", dry=True)` gives `outside_intake: #3240 refused rc=0`.
  - Under the mutant, it gives `outside_intake: REFUSED: #3240 has no outside activity` (rc 1). That owed triage line could then never be disposed through the tool, and it would print on every beat.
  - Evidence: `ev/drive.txt` (script `ev/drive.py`) and `ev/reviewer-mutants-casesonly.txt`.

Cure: one case that refuses (or answers) a thread whose only outside activity is a review comment, plus a MUTANTS entry on L210.

## Findings

- **Unpinned review-comment read.** Claim: `one_thread`'s read of `pulls/{n}/comments` for a PR (L210) is not pinned by any case. Evidence: `ev/reviewer-mutants-casesonly.txt` (`one_thread_pr_reviews_drop SURVIVED rc=0`) and `ev/drive.txt`. Harness: the self-test's cases (`run(False)`) plus my own drive of `dispose` over the self-test's `Fake(world)`. Metric: case rc, and dispose's rc and message for #3240. Perturbation: `if False:` at L210. The cases stay rc 0, while dispose moves from `refused rc=0` to `REFUSED: #3240 has no outside activity`. Null control: the head gives rc 0. Carry: R10-OUTSIDE-INTAKE
- **Unpinned discussion kind (plausible).** Claim: in `scan`, `if t.n in disc: t.kind = "discussion"` survives (`scan_disc_kind SURVIVED rc=0`). Evidence: `ev/reviewer-mutants-casesonly.txt`. Harness: the self-test's cases. Metric: case rc. Perturbation: `if False:`. By reading the code, `saw()` sets the kind only from an outside opener. A discussion opened by us, with only outside comments, would then print `comment` rather than `discussion` on its OUTSIDE line. I did not drive that world, because the fixture world holds no discussions, so this one is not demonstrated. Carry: R10-OUTSIDE-INTAKE
- **Same-second reply boundary.** Claim: in `owed`, `>` to `>=` survives the cases-only run (`owed_reply_ge SURVIVED rc=0`). In the full `--self-test` it read KILLED only through the `reply_never: stale` text check. Evidence: `ev/drive.txt`. An outside comment in the same second as our answer on #3225 gives no line at the head and `owed=reply` under the mutant. Harness: my drive. Metric: the #3225 line. Perturbation: `>=`. The head's choice, which treats a same-second outside comment as answered, is unasserted and arguably the wrong way round. Carry: R10-OUTSIDE-INTAKE
- **`## Red checks` is stale at the PR head.** Claim: the body says the measured head has no check runs and that its "reds, if any, are named at the next read". Its section names no red of 0fd9bc6d. Evidence: `ev/check-runs.tsv` (200 runs, two pages, `filter=all`) and `ev/red-details.txt`. Harness: the commit's check-runs API. Metric: concluded reds not named. Perturbation: none applies; this is a read of state. Unnamed at this head:
  - `gate` 128304775378, 128316374818 and 128324526998 concluded failure. Each log says `FAIL run(s) [42339563999] at this head are still being judged; their gate decides`, the edit-run deferral.
  - `gate` 128305369003 and `arch-score / arch-score` 128304887981 concluded cancelled.
  - `governance / instrument-self-tests` 128304160651 (04:45:23Z-05:15:38Z) and 128314670086 (05:30:48Z-06:01:03Z) concluded cancelled, each at the 30-minute timeout. That is the owner's standing line, cure R10-PROCESS-SLIM, #3245.
  - Attempt 3 (128322483648) concluded success at 06:35:48Z.

  Carry: R10-OUTSIDE-INTAKE
- **Gate green over a cancelled required job.** Claim: `gate` 128321406871 concluded success at 06:04Z while instrument-self-tests attempt 2 was cancelled. Evidence: `ev/check-runs.tsv`. Harness: the check-runs API. Metric: gate conclusion against the required job's conclusion. Perturbation: none applies; this is a read of state. The brief records it already (s12-3262-gate-green-over-cancel.txt). I did not rely on it. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. `review_packet.py render` reported no refusals and wrote a green digest. I re-read the live checks after that.
- Round-2 survivor: `thirdbot_moves_out` KILLED (rc 1) by "identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply". The round-2 form, the inner guard made `if True:`, has no line left at the head. The same holds in both counting modes.
- The fixer's correction of the round-2 runner is right. Run in full, `--self-test` counts its own stale-mutant check as a kill. My full-mode run (`ev/reviewer-mutants.txt`) showed `mark_old_restored_EQUIV` and `owed_reply_ge` as KILLED only through `stale`. Cases-only, both survive. My runner stopped at its timeout after 28 mutants. I then restored the worktree (`git checkout`, tree clean) and re-ran all 47 cases-only on a separate worktree.
- Cases-only results (`ev/reviewer-mutants-casesonly.txt`): the null run is rc 0. Of 47 mutants, 41 were KILLED and 6 SURVIVED:
  - `one_thread_pr_reviews_drop`: the block.
  - `scan_disc_kind` and `owed_reply_ge`: the findings above.
  - `mark_old_restored_EQUIV`: the equivalence the body declares and measures (`mark_outsider_moves_out`).
  - `has_disc_ignored`: dismissed as equivalent in output. On a repository without discussions, the GraphQL call it no longer skips returns no nodes.
  - `plan_live_200`: dismissed as near-equivalent. `urlopen` raises on 4xx and 5xx and follows 3xx, so `status == 200` only separates other 2xx codes. `plan_live` is network-only, and LIVE/DOWN fakes stand in for it.
- Killed by a named case, among others: all of `Thread.mark` (`mark_guard_false`, `mark_guard_outside`, `last_ours_drop`, `mark_answered_drop` and `mark_refused_drop`).
  - `saw_no_last_out` and `saw_first_max` are killed. That confirms `saw` owns `last_out`.
  - Every `one_thread` predicate but L210 is killed, and so is every `scan` predicate but the discussion kind.
  - The `owed` words, every `dispose` refusal (twice, discussion, no group, not live, no thread) and both markers are killed.
  - So are `post` rc, argv, dry-run and script path, plus the cursor, wait and UNAVAILABLE lines, `rows` rc and the `who` suffix.
- The class rule the body names, `last_out =` in `outside_intake.py`: at the head, `Thread.__init__` and `Thread.saw`, as the body says. The body's reasoning holds when read against `scan`. A comment `scan` does not pass to `saw` has `at < since`, and the thread exists only through activity at or after `since`, so the deletion is equivalent for outside comments.
- Self-test at head: `outside_intake self-test: all checks passed`, rc 0, 46 `ok` lines. That is 26 cases and 20 mutants, which matches the body. Cheap checks at head: `ev/checks.txt`.
- I did not re-run the full instrument-self-tests job (about 27 minutes in CI). I cite CI's attempt 3, 128322483648, success. I ran this PR's own instruments in that job myself: the outside_intake self-test above, plus plan_public and beat_jobs in `ev/checks.txt`.
- `merge_train.py classify 0fd9bc6d... --pr 3262`: `GREEN 0fd9bc6da6a5f562c7104c1e4d921189f492cff1 pending: none red: none` (rc 0), in `ev/classify.log`. The block above does not depend on CI.
- `pr-contract / pr-contract` 128328973908 concluded success. It started at 06:40:29Z, after the last concluded red at 06:18:04Z.
- Merge: `git merge-tree --write-tree origin/main HEAD` against be813ecd gives rc 0, tree e71990321e896bf719f9835bb041cb2935dac27a, with `LEDGER-MERGE: resolved tests/closures.json`.
- Cheap checks at head (`ev/checks.txt`):
  - `ref_privacy --check`: 0 refused. `tmp_paths`: 0 refused.
  - `selftest_wiring`: 120 self-testing, 120 wired, 0 unwired, 0 index gaps.
  - `plan_public self-test: all checks passed`. `beat_jobs self-test: 136 checks, 0 failed`.
  - `STRUCTURE RATCHET PASSED`. `ALL 2641 ENTITY CHECKS PASSED`, so the new tracked files are classified. `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - The three-dot diff touches no `*budgets.json`, `VERSION`, `RELEASE_NOTES.md` or manifest (count 0). `dev/programme/delivery/3262.md` is in the diff.
- `## Head`: it names 0fd9bc6d as the PR head and 9ffed3f2a as the measured head, which matches what I measured.
- I did not re-derive the round-1 figures this delta does not move: the policy_lint caps, archscore dS and the live intake pass. The delta touches only `outside_intake.py` and its self-test.
- Policy part: it merges only on tvofi's approving review at the head. The 2026-11-06 ruling is quoted verbatim in the body.
