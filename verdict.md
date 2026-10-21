Fix review: merge 4ef1a8270f3bd30bc6c313c950f6f44713a1442d

Reviewed head: 4ef1a8270f3bd30bc6c313c950f6f44713a1442d, re-read from the PR API at the end of this review and unchanged (ev/head_reread.txt). By this PR's comments this is review round 6. The brief calls it round 5. The earlier merge verdict (comment of 16:21Z, on 54bf1821) does not carry over, because the head took a hand-resolved main merge.
Role file is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, with origin/main at 57f0c9c77. I worked from a detached worktree at the head.
Evidence is in ev/: HEAD.txt, head_reread.txt, remerge_4b46b23.txt, remerge_head.txt, mutants.py, mut1.sh, mutants_result.txt, mut_*.txt, selftest_*.txt, body_checks.txt, figures.txt, class_rule.txt, roster_carry.txt, check_runs.tsv, merge_tree.txt, pr_body_at_review.md and title.txt.

## The previous block (merge-conflict in pr_args.sh): fixed

- `git merge-tree --write-tree origin/main 4ef1a827` exits 0 with tree fecc8e147, and origin/main is 57f0c9c77 (ev/merge_tree.txt). The head's merge base with main is main's tip. The three-dot diff touches 5 files: app_push.sh, pr_args.sh, update_pr.sh, INSTRUMENTS.md and the PR's own row 2567.md.
- `git show --remerge-diff 4b46b23` shows the only hand resolution, in tools/audit/seat/pr_args.sh (ev/remerge_4b46b23.txt). Main's open_pr/update_pr race arm and its unpushed-work arms are kept verbatim. The branch's row-only arm moved after them, on fixture branch `fix/w` with marker `$t/fixw`, which nothing else in the file uses. Main's race arm keeps `fix/r` and `$t/fixr`. This matches the body's account.
- The orchestrator's merge 4ef1a827 of main 57f0c9c77 has an empty remerge-diff, so it is clean (ev/remerge_head.txt). Relative to 54bf1821, app_push.sh changed only by main's own delta.
- The moved arm works after the resolution: W6 and W6b each fail 1 of `pr_args self-test: 63 checks` (below).

## Mutation proof (step 1), re-run at this head

Each mutant is one exact-string replacement, run in its own throwaway worktree at the head against the owning self-test, and then discarded. The runner is the round-5 runner (copied from review/2567~1's evidence and read before use), extended with W6, W6b, W14, W24 and W25 (ev/mutants.py, ev/mut1.sh, ev/mutants_result.txt).

- RESULT M0 (no replacement): `app_push self-test: 182 checks, 0 failed`.
- RESULT killed: W1 4, W2 1, W3 1 (my form), W4 2, W5 8, W7 1, W8 1, W9 3, W10 2, W11 2, W12 1, W13 2, W14 10 (my form: the verdict's `&& skip=1` becomes `; skip=1`), W15 1, W21 2, W22 2, W25 8 (the row_only_checks call guard becomes `true ||`).
- RESULT update_pr.sh: W6 (`RO=--row-only` for every code sha) and W6b (`RO=""`, the row-only arm deleted) each give `pr_args self-test: 63 checks, 1 failed`.
- My W3 and W14 differ in form from the body's, so my counts differ from the body's 2 and 30. Both mutants are killed either way.
- Non-blocking, W23 survives (`[ "$rowonly$bonly" != 11 ] ||` becomes `true ||`, 0 failed). It is the usage guard that refuses `--row-only` together with `--branch-only`. Round 4 already dispositioned it, and nothing has changed since. Carry: dismissed: defensive usage guard, the path fails closed without it
- Non-blocking, W24 survives (`j > i and ` deleted from (d), 0 failed). The body's class triage already discloses this conjunct as unpinned: the equality beside it still holds the property. I confirm that triage. Carry: dismissed: disclosed in the body's class triage, the equality conjunct still pins (d)

## Null control and figures (steps 2, 3, 7, 8)

- RESULT self-tests at head: `app_push self-test: 182 checks, 0 failed`. `update_pr.sh --self-test` gives `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 63 checks, 0 failed`.
- `tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `archscore --diff f2fb1b0e9`, and against the current merge base: `dS +0.0000 NULL`.
- The body's `closure.py select --diff f2fb1b0e9` figure (`SCOPED -- 0 script(s) run, 33 scoped out`) re-derives at the code head 4b46b23, where the body says it was measured. At 4ef1a827 against f2fb1b0e9 the same command prints 27 scripts, because main's later commits are in that two-dot range. Against the head's actual merge base (57f0c9c77) it prints `SCOPED -- 0 script(s) run, 33 scoped out`. Carry: dismissed: the figure re-derives at the head it names, and the scope from the true base is unchanged
- The body's `## Head` names 4ef1a827 and states that it carries from the code head 4b46b23. Its figures are measured at 4b46b23, and the delta between the two is main's clean merge.
- Not re-derived: the body's always-run figures that need Python 3.13 (entities.py 2381, harness_headers 109, closure selftest 124, layout). This container's python3 is 3.11, and the diff touches none of what those scripts pin. I state them as unverified by me, not as confirmed. Carry: dismissed: environment-only interpreter gap, the diff touches nothing those scripts read
- Finder's harness (steps 2 and 9): this finding has no committed harness and no roster group named R10-ROW-ONLY-UPDATE on origin/handoff/audit-r10-roster (23ef06dc6). The instrument is the fixer's self-test arms plus the 2026-10-21 queue incident the body cites. Every round so far reviewed against the body on that basis, and so do I. Carry: dismissed: incident-driven seat-tooling fix, the self-test arms are disclosed as the fixer's own

## Class (step 6)

The body's rule (every `_rv_no` refusal in `row_only_verdict` plus the conjuncts of its two inline Python predicates) prints 8 refusals and the success line at this head (ev/class_rule.txt), the same set the body enumerates.
- Pinned by killed mutants: parent count (W2), parent-is-live (W10), the one-file diff (W1), (c)'s three conjuncts (W11/W21/W22, W12, W4), (d) (W3), and no open PR (W14).
- The rest is triaged in writing in the body: HEAD read-back, diff read, delivery_row load, and `j > i`.
No seam is open.

## Claims, versions, budgets (steps 4, 5, 14)

The three-dot diff touches no claim file, `VERSION`, manifest, `RELEASE_NOTES.md`, budget file, `closures.json`, `INERT` or golden. It moves no instrument number.

## Body checks and forward-carry (step 10)

- `carry_audit.py check --body` on the live body: `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc=0.
- `policy_lint.mjs --pr-body --head 4ef1a827 ... --title <live>` with gh's token: `record red-history 13 commit(s) ... nightly-status` and `PR-BODY: 0 error(s)` (ev/body_checks.txt).
- The forward-carry is in R10-POLICY-FIXER-MD's `carry` on origin/handoff/audit-r10-roster tip 23ef06dc6: `Source: #2567 Forward-carry. prepr.sh does not run carry_audit.py check ...`. It states the precondition (run `carry_audit.py check --body` beside prepr in step 7, or name it in step 5) and the control (#2567's pr-contract reds on 947d3631/93015eca, which passed prepr) (ev/roster_carry.txt).
- Non-blocking: the body's Forward-carry line no longer names the roster SHA that round 5's body cited (c185c72). The carry stands on the roster tip regardless. Carry: dismissed: the carry is verified present on the roster tip, so the missing SHA citation loses nothing

## CI (step 11), read once after every run on this head concluded

- RESULT check-runs at 4ef1a827, read at 2026-10-21T18:40Z after every run had concluded: 52 runs, 35 success, 16 skipped, 1 failure (ev/check_runs.tsv). Nothing is pending.
- Three pr-contract runs, all success: 119394771630, 119395061730, and 119411918901, which started at 18:39:54Z after the body edit below. `mutation` is success (119394771991). This diff writes production lines in tools/, so I did not read the lane log to separate "no survivor" from "none evaluated". My own 22 targeted mutants stand in for that.
- The only red is nightly-status (119394771924). Per `defect-root-cause.md` it grades main, and the diff touches nothing it reads: tools/ and the PR's own added row only.
- The body was edited during this review; the head did not move. The `## Red checks` section went from `none` to an answer: nightly-status grades main, the diff touches no `.github/` file and no test lane, and its own failing scheduled job is the cheaper detector at nil standing cost (ev/body_diff_during_review.txt). The brief's rule-22 ask is therefore met.
- On the final body, `carry_audit.py check --body` reports `2 routed, 0 unrouted`, and `policy_lint.mjs --pr-body --head 4ef1a827` reports `PR-BODY: 0 error(s)` (ev/body_checks.txt, second block). My mutation, class and figure checks read the code and the tree, which the edit did not touch, so all of them survive it.
- Round 6 by this PR's comments is past the fourth round, where `fixer.md` owes a re-cut. This round's change, however, is a forced main-merge resolution of a head that already earned a merge verdict, not a repair of a finding. Carry: dismissed: a conflict resolution, not a fourth repair of the fix

bus-nonce: cdda16118cf7b9ea9ddfcd538c68d6d3
