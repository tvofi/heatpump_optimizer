Fix review: merge 632d2fe261b5293e718363485cd816909bf3290c

bus-nonce: d190b84d1b9c6093eadae293bb02a765

This is **round 7** of PR #2579 (R10-FLOW-YIELD-PROBE), an adversarial re-review limited to the two edits the round-6 verdict named (review/2579 f7a6bdf0c). I measured head 632d2fe261b5293e718363485cd816909bf3290c from detached worktrees. Its code head is 8a01caf2e. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current. `git ls-remote` still showed the branch at that head when I wrote this verdict (ev/head_at_post.txt). Every required item passes.

## Findings

This round raises no new finding. Both round-6 Block items and the round-6 GROUP_RE wording finding are settled at this head (Evidence). The seven equivalent hand mutants were dismissed in round 6 and are not re-opened.

## Evidence

- **Item 1: the probe-slice survivor is dead** (ev/hand_mutants.txt). I applied each mutant to `load` line 130 in a scratch worktree, ran the self-test and restored the file; `git diff --quiet` then printed `RESTORED-IDENTICAL`.
  - `nonce[:8]` → `nonce[-8:]`: `FAIL: cloud: the nonce is the line-start bus-nonce, read in full hex, matched to a probe ref (16)`, `87 checks, 1 failed`, rc=1.
  - `nonce[:8]` → `nonce[8:16]`: the same FAIL line, `87 checks, 1 failed`, rc=1.
  - I added two more mutants, `nonce[16:24]` and `nonce[1:9]`. Both are killed by the same check.
  - Unmutated: `review_strength self-test: 87 checks, 0 failed`, rc=0 (ev/selftest_head.txt, Python 3.11). That matches the body's 87.
  - The new fixture nonce is `09abcdef1234567876543210fedcba98`. Its first 8 hex appear nowhere else in it.
- **Item 2: the class sweep.** `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` ran at this head and printed `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=0`, rc=0. M0 printed `87 checks, 0 failed` (ev/sweep_head.txt). Every figure matches the body. `--list` at 45754ede2 (a `git archive` copy) and at this head are identical, 2351 lines each (`MUTANT-LIST-IDENTICAL`, ev/mutant_list_identity.txt). The code head's hunks are `DISPOSED` line 153 and `_self_test_seams` lines 563 and 570 only, so no line that `load` or the bundle runs changed (ev/code_head_hunks.txt).
- **Item 3: the GROUP_RE disposition** now reads "every roster group and every delivery row's group token holds two or more characters after the dash". The harness holds no 150 or 151 (ev/group_re_disposition.txt). The roster at origin/handoff/audit-r10-roster holds 151 groups, the shortest with 2 characters after the dash, so the equivalence still holds and the body's figure is right.
- **Item 4: the forward-carry** (ev/forward_carry.txt). c98fb4c27 ("roster_edit append-carry R10-ORCH-MACHINERY") is an ancestor of origin/handoff/audit-r10-roster (2501a0a16e65). The R10-ORCH-MACHINERY carry there cites review/2579 f7a6bdf0c and states both points:
  - (1) P(X ≤ 4 | n=30, p=0.28) = 0.0495, so the 30-PR arm trips at 4 or fewer, not 3;
  - (2) any ALPHA must be checked at P = 0.0526 (k = 2 of 20).

  It states its control as a precondition. I recomputed P(X≤4|30,.28)=0.0495, P(X≤3|30,.28)=0.0166 and P(X≤2|20,.28)=0.0526 (ev/binom.txt).
- **Item 5: red checks.** I read the check-runs API for all 35 PR commits (ev/red_history.tsv):
  - `instrument-self-tests` and `pr-contract` failed at 6ad8089c1. The body names and answers both.
  - `nightly-status` failed at 81d617cec, 468781122, 816b1e20f, eb9f7e89d, 6ad8089c1, 45754ede2 and this head. The body names it as grading main; the diff reaches nothing it reads. It is not this PR's check, it is not a required check and it does not block. This head's red is the same check.
  - The 13 `cancelled` runs at 81d617cec were superseded.
  - No other red.
- **Merge-tree.** `git merge-tree --write-tree origin/main 632d2fe26…` with origin/main at 738d950aa is clean: rc 0, tree ee326fb0d39b (ev/merge_tree.txt).
- **Carry audit.** `carry_audit.py --roster-ref origin/main check --body` and the same with `--roster-ref origin/handoff/audit-r10-roster` both print `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt).
- **CI on this head** (ev/check_runs_head.tsv): 32 success, 7 skipped and 1 failure, `nightly-status` (above). `closures` and `Analyze (actions)` were still in progress when I wrote this. The three `pr-contract` runs succeeded, the latest started at 14:31:02Z.
- **Steps 5 and 7.** The three-dot diff touches no `VERSION`, manifest, `RELEASE_NOTES.md`, claim file or `*_budgets.json` (ev/untouched.txt). `## Head` names 632d2fe261b5293e718363485cd816909bf3290c with code head 8a01caf2e, the head I measured.

RESULT selftest=87/0 probe_slice_mutants=4_killed(nonce[-8:],nonce[8:16],nonce[16:24],nonce[1:9]) sweep=2350/2306/44_disposed/0_undisposed/0_stale mutant_list=identical group_re_count=none forward_carry=present(c98fb4c27_on_handoff) red_history=all_named merge_tree=clean carry_audit_body=0_unrouted_0_bad round=7
