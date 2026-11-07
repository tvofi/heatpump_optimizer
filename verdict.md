Fix review: blocked 3189559b21ddf1d5517ea7ec34f0df470c480103 mutation-vacuous: outside_intake.py Thread.mark third-party-bot guard survives the self-test

bus-nonce: 990dee62cc5f67975d7170e16ff65360

This is round 2 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head 3189559b21ddf1d5517ea7ec34f0df470c480103. I worked from a detached worktree at that head. The merge base with origin/main is f2a015142714383722bf49d7ab20d8398ec9674c, which is also origin/main, so the role contract is current. The head's tree is the same as the authored head 296bc921d0023a52d194c1f8d16d5afa418c098f (`git diff` is empty). Since round 1 (48acc104), the branch's only authored change is 296bc921d. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The brief asks for the mutation proof to be re-run on every changed line, not only the lines the body names. Commit 296bc921d restructured `Thread.mark` (`tools/audit/seat/outside_intake.py` L133-136). One of its new lines survives `python3 -I tools/audit/seat/outside_intake.py --self-test` (rc 0):

- **Inner `outside()` guard** (L134). Changing `if outside(c["login"], c["type"]):` to `if True:` SURVIVED. That lets a third-party bot's comment move `last_out`. It contradicts the docstring and body line it implements: "a third-party bot's is neither ours nor outside activity". The mutant is not equivalent. Drive #3225: outside submission, then our ANSWER_MARK, then a later comment by `renovate[bot]` (Bot). The head gives `owed=None`; the mutant gives `owed=reply`. So any review or dependency bot commenting on an answered thread would raise a false `reply` owed line on every beat. The null control is a later comment by `Bankaifan` (User), which gives `owed=reply` both at the head and under the mutant. `marker_any_bot` does not cover this: it reverts the whole guard to `outside()`, so the third-party branch itself is never asserted. Evidence: `ev/thirdbot-survivor.txt` and `ev/reviewer-mutants.txt`.

Cure: one case that adds a third-party bot comment after our answer on a disposed thread and asserts `owed` is None, plus a mutant on L134.

## Findings

- **Unpinned guard.** Claim: the `outside()` guard inside `Thread.mark`'s non-OURS branch (L134) is not pinned by the self-test. Evidence: `ev/thirdbot-survivor.txt`. Harness: `python3 -I tools/audit/seat/outside_intake.py --self-test` and a direct `Thread`/`owed` drive (`ev/thirdbot.py`; mutant runner `ev/mut.py`). Metric: self-test rc, and the owed word. Perturbation: `if True:` at L134. The self-test stays rc 0, while owed moves from None to reply for a `renovate[bot]` comment after our answer. Null control: an outside `User` comment gives reply under both. Carry: R10-OUTSIDE-INTAKE
- **Head's gate red not yet answered.** Claim: `## Red checks` names the reds of 48acc104 only, and says no check had run at 296bc921. At 3189559b, `gate` check run 128272376901 concluded `failure` with `FAIL run(s) [42329336154] at this head are still being judged; their gate decides`. That is the edit-run deferral to an in-progress code run. Evidence: `ev/check-runs.tsv` and `ev/classify.log`. Harness: the head's check-runs API, all pages. Metric: concluded reds not named. Perturbation: none applies; this is a read of state. The code run's own `gate` (128282233458) later concluded success, at 03:09:48Z. The concluded red still owes the body a line naming it as the ordering deferral, as the body did for 48acc104's four. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
- `review_packet.py render`: `REFUSE required-red: required context gate concluded failure at 3189559b...`. The packet was written, and live checks were re-read.
- Round-1 survivors, re-run by me in place (`ev/reviewer-mutants.txt`). Null control: unmutated rc 0. All six round-1 mutants are now KILLED (rc 1):
  - cursor read and cursor write, each by "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass";
  - post rc, by "post: a failed gh_comment read-back (rc 1) is a non-zero answer";
  - `--dry-run` drop and script path, each by "post: gh_comment.py post is run with the body file, --dry-run passed, rc 0 kept";
  - list rc, by "main list: ...".
- Changed-line mutants (my own, beyond the body's): 12 run, 11 KILLED, and 1 SURVIVED (`mark_thirdbot_moves_out`, see Block).
  - Killed: `mark_revert_old`, `mark_no_last_out`, `who_no_suffix`, `who_never_bot`, `who_typ_user`, `cursor_exists_guard`, `cursor_write_skip`, `dry_always`, `post_issue_arg`, `last_ours_drop` and `keep_now`.
- Self-tests at head (`ev/checks.txt`):
  - `outside_intake self-test: all checks passed`, rc 0. There are 44 `ok` lines: 25 cases plus 19 `mutant` lines. That matches the body's "25 cases and 19 mutants".
  - `plan_public self-test: all checks passed`.
  - `beat_jobs self-test: 136 checks, 0 failed`.
  - `ref_privacy --check`: 0 refused.
  - `STRUCTURE RATCHET PASSED`.
- No change to VERSION, RELEASE_NOTES.md, any manifest or any `*budgets.json` in the three-dot diff. `dev/programme/delivery/3262.md` is in the diff.
- Merge: `git merge-tree --write-tree origin/main 3189559b` gives rc 0 with no conflict. origin/main is f2a015142714383722bf49d7ab20d8398ec9674c.
- `## Head`: the body names 3189559b as the merge of the authored head 296bc921, with an identical tree, so it is current.
- I did not re-derive from scratch the round-1 figures this delta does not move: the policy_lint budgets, the scoped gate count and archscore dS. The role contracts, pages.yml and plan_public are unchanged since 48acc104 in the branch's authored range. Round 1 verified those figures.
- Policy part: it merges only on tvofi's approving review at the head. The ruling is quoted verbatim in the body.
- CI at return (`ev/check-runs.tsv`, 55 runs, all pages, `filter=all`): all completed. The one concluded red is `gate` 128272376901 (the edit-run deferral). `gate` 128282233458 concluded success. `pr-contract / pr-contract` 128281910559 concluded success at 03:08:23Z. `governance / instrument-self-tests` concluded success (02:54:52Z), not cancelled. `tests / mutation` concluded success. CodeQL is neutral. Everything else is success or skipped.
- `merge_train.py classify 3189559b... --pr 3262` printed `RED 3189559b21ddf1d5517ea7ec34f0df470c480103 pending: none red: gate` (rc 1) after every run had concluded (`ev/classify.log`). It keys on the deferral's failed `gate` run beside the later green one. The block above is independent of CI.
- The head was re-read before return: the PR head is still 3189559b21ddf1d5517ea7ec34f0df470c480103.
