Fix review: blocked 54bf182104e450c0ac2e6eb007da59b9315e0565 carry-missing: not carried to R10-POLICY-FIXER-MD

Reviewed head: 54bf182104e450c0ac2e6eb007da59b9315e0565, re-read from the PR at 2026-10-21T15:22Z and unchanged. This is review round 4, so `fixer.md` owes a re-cut, not a repair (fix-review.md). The cause here is in the roster, not the code.
Role file is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. I worked from a detached worktree at the head.
There is no roster group for R10-ROW-ONLY-UPDATE on origin/handoff/audit-r10-roster (2c76c3128) or on origin/main, so I reviewed against the PR body, as the earlier verdicts did.
Evidence in ev/: HEAD.txt, head_reread.txt, mutants.py, mut.sh, mutants_result.txt, selftest_*.txt, body_checks.txt, forward_carry.txt, class_rule.txt, figures*.txt, merge_tree.txt, check_runs*.tsv and pr_body_at_review.md.

## Blocking

1. **The forward-carry is not in the tree (step 10, finding-propagation.md "Enforcement").**
   - The body's `## Forward-carry` records a finding that changes a later stage: prepr.sh does not run `carry_audit.py check`, so fixer.md step 5's "body passes prepr" gate is not pr-contract's body gate. It routes the finding with `Carry: R10-POLICY-FIXER-MD`.
   - That group on the roster branch (origin/handoff/audit-r10-roster at 2c76c3128bf6d4e0cf37488eb8d29af830df54a0) is `not-started` with 5 carries. None mentions carry_audit or #2567. `git log -S'carry_audit.py check'` on the roster file finds no commit (ev/forward_carry.txt). The same group on origin/main is the same.
   - The body names no roster file or branch SHA for the carry.
   - So the finding is recorded only in this PR, which is the case step 10 blocks. The precedent shows the expected shape: #2447's Forward-carry into this same group is in its `carry` array ("Source: #2447 ...").
   - The marker passes `carry_audit.py check`, which proves only that the group exists, not that the carry landed.
   - The fix: write the carry into R10-POLICY-FIXER-MD's `carry` on the roster branch. State the precondition (prepr runs `carry_audit.py check --body` beside step 7, or step 5 names it beside prepr) and the control (this PR's three pr-contract reds on 947d3631/93015eca, which prepr passed). Then name the roster SHA in the body.
   - No code change is needed. Everything below holds at this head.

## Verified at this head

- **The previous block (W11) is killed.** Deleting `len(ls) == 1 and ` gives `app_push self-test: 182 checks, 2 failed`: `omulti` (got '002', want '110') and `real git: a row file of two lines, the first the open row anchored on #7, runs prepr`. My two variants of the same property are also killed, 2 failed each: W21 (`len(ls) >= 1`) and W22 (`splitlines()[:1]`).
- **My mutants** (ev/mutants_result.txt; mut.sh restores the file, ending "restored to 54bf1821..."):
  - M0: 182 checks, 0 failed.
  - W1: 4 failed. This is my widening of (b) to `grep -qF "$row"` of the path; the body's W1 greps the row line.
  - W2: 1 failed.
  - W3: 1 failed. This is my `and 0` on (d)'s predicate; the body's W3 is `|| :`.
  - W4: 2 failed.
  - W5: 8 failed.
  - W7: 1 failed.
  - W8: 1 failed.
  - W9: 3 failed.
  - W10: 2 failed.
  - W11: 2 failed.
  - W12: 1 failed.
  - W13: 2 failed.
  - W15: 1 failed.
  - W2, W4, W5, W7–W13 and W15 match the body's counts exactly. I did not re-derive the body's own W1, W3, W6, W14, W16, W18–W20 forms. Mine of the same predicates are all killed except W23, below.
- **Null control.** The real-git `the same commit with one more file runs prepr (null control)` fails under W1, and `ensure_row's own row commit on the live head skips prepr` passes at M0. So the predicate separates a row-only commit from a row-plus-one-file commit. A code sha never asks for `--row-only`: `pr_args self-test: 57 checks, 0 failed` at the head, and the body's W6 kills it.
- **Self-tests at the head:**
  - `app_push self-test: 182 checks, 0 failed`
  - `delivery_row self-test: 5 checks, 0 failed`
  - `pr_args self-test: 57 checks, 0 failed`
- **Class (step 6).** The body's rule, `sed -n '/^row_only_verdict() {/,/^}/p' tools/pr/app_push.sh | grep -o '_rv_no "[^"]*'`, returns 10 lines: 9 refusals and 1 success line (ev/class_rule.txt). That matches the body. Each refusal is pinned or has written triage in the body.
- **Figures.** These reproduce at a8bb9a9c1, where the body states them (ev/figures_at_a8bb9.txt):
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out` against 5d433771a
  - `ALL 124 closure shrink pins PASSED`
  - `layout self-test: ok`
  - `claims hygiene: 5d433771... ok`

  At this head: `MODE: SCOPED -- 0 script(s) run, 33 scoped out` against origin/main e7c664856, `Architecture score: dS +0.0000 NULL`, and `STRUCTURE RATCHET PASSED`. The `--diff 5d433771a` select at this head prints FULL, because main's own commits since 5d433771a are inside that range. That is not this PR's change.
- **Not re-run.** harness_headers (109) and entities (2375): this container lacks `voluptuous`. I cite CI instead: `fast (3.14)` and `instrument-self-tests` are success at this head.
- **Body checks on the live body at this head** (ev/body_checks.txt):
  - `carry_audit.py check`: `2 routed, 0 unrouted`, rc=0.
  - `policy_lint.mjs --pr-body`, given gh's token: `record red-history 10 commit(s) ... nightly-status` and `PR-BODY: 0 error(s)`.
- **Merge.** `git merge-tree --write-tree origin/main(e7c664856) 54bf1821...` exits 0 with tree e3466b7de. There is no conflict.
- **Untouched:** VERSION, the manifest, RELEASE_NOTES, claim files and goldens. The three-dot diff is 5 files. `## Head` names 54bf182104e450c0ac2e6eb007da59b9315e0565.
- **CI** (check-runs API, ev/check_runs_final.tsv):
  - Concluded, all success, skipped or neutral, except nightly-status: failure. nightly-status grades main's scheduled Tests run, and this diff (seat tooling plus its own row) does not reach what it reads, so it is not this PR's. The body answers it under `## Red checks`.
  - pr-contract run 119298521309 started at 15:03:05Z, after nightly-status concluded at 15:02:40Z, and is success. So step 11 stands answered.
  - Still in progress at 15:22Z: `coverage` and `Analyze (python)`. I judged on the rest.

## Non-blocking

- W23 (deleting the `--row-only`/`--branch-only` refusal) survives: 182 checks, 0 failed. It fails closed anyway. With `--branch-only` the listing is never read, so `row_only_verdict` hits an unbound `$listing` under `set -u` before any mint. Carry: dismissed: defensive usage guard, the path fails closed without it

## Carry of the previous review's items

Carry: dismissed: the round-3 body was re-taken whole and no longer says this (item f053a70e)
Carry: dismissed: the round-3 body was re-taken whole and no longer says this (item d3bf9b75)

bus-nonce: b1b280e7efb0939ec05a8f6b4be26f74
