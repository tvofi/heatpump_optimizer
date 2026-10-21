Fix review: merge 54bf182104e450c0ac2e6eb007da59b9315e0565

Reviewed head: 54bf182104e450c0ac2e6eb007da59b9315e0565, the same head as round 4, re-read from the PR at the end of this review (ev/head_reread.txt). This is review round 5. The code is unchanged since round 4, which blocked only on `carry-missing`. That gap is now closed in the roster, so this round needs no re-cut.
Role file is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty against origin/main 49c222280 (ev/roles_current.txt). I worked from a detached worktree at the head.

## Round-4 block: the forward-carry (step 10). Now closed

- The body's `## Forward-carry` item now names `handoff/audit-r10-roster at c185c7257199e3e420b29329a787edd52ab12252`.
- At that commit, R10-POLICY-FIXER-MD's `carry` list has 6 entries. The last one is the `Source: #2567 Forward-carry. prepr.sh does not run carry_audit.py check ...` entry. The same entry is at the branch tip 67eb2561e, and c185c72 is an ancestor of the tip (ev/forward_carry.txt).
- It states the precondition: run `carry_audit.py check --body` beside prepr in step 7, or name it beside prepr in step 5.
- It states the control: #2567's three pr-contract reds on 947d3631/93015eca, all of which passed prepr.
- The live body differs from the round-4 body (taken from review/2567 21141036's evidence) by exactly one thing: the added sentence on the Forward-carry line, plus one trailing blank line (ev/body_diff_round4.txt).
- On the live body:
  - `carry_audit.py check --body` reports `2 routed, 0 unrouted, 0 bad destination(s)`, rc=0.
  - `policy_lint.mjs --pr-body`, given gh's token, reports `record red-history 10 commit(s) ... nightly-status` and `PR-BODY: 0 error(s)` (ev/body_checks.txt).

## Mutation proof (step 1), re-run at this head

I used the round-4 runner (ev/mutants.py and ev/mut.sh, copied from review/2567's evidence and read before use). Each run restored the file, ending `restored to 54bf1821...` (ev/mutants_result.txt). M0 gives `app_push self-test: 182 checks, 0 failed`.

- W11 (delete `len(ls) == 1 and `): **2 failed**. The two arms are `omulti` (got '002', want '110') and `real git: a row file of two lines, the first the open row anchored on #7, runs prepr`.
- W21 (`len(ls) >= 1`) and W22 (`splitlines()[:1]`): 2 failed each.
- W4: 2. W7: 1. W1 (my form): 4. W10: 2. W12: 1. W2: 1. W3 (my form): 1. W5: 8. W8: 1. W9: 3. W13: 2. W15: 1.
- W6 (`update_pr.sh` `RO=--row-only` for every code sha): `pr_args self-test: 57 checks, 1 failed`, on the arm `null control: a code sha never asks for --row-only`.
- Every mutant is killed. W2, W4–W13 and W15 match the body's counts. W1 and W3 are my own forms of those predicates, not the body's; my counts for them differ from the body's (4 vs 2, 1 vs 2), and I did not re-derive the body's own forms.

## The finder's harness at both ends (step 2)

The finder's harness is the round-3 reviewer's `w11_demo.sh` (probe/rev-2567-add37b67, copied to ev/). It runs production `row_only_verdict` on real git with a two-line row file (ev/w11_both_ends.txt).

- The production predicate is unchanged by design, so the demo is flat at both ends:
  - At f16956542 (the finder's head) it refuses with `... is not one open row anchored on #7`, rc=1.
  - At 54bf1821 it refuses the same way, rc=1.
- Under W11 at the head it skips, rc=0. So the demo can move.
- The self-test is what changed. Under W11:
  - At f16956542: `179 checks, 0 failed` (the survivor).
  - At the head: `182 checks, 2 failed` (killed).
- Null control: M0 is `179/0` at f16956542 and `182/0` at the head.

## Other steps

- **Steps 3, 6 and 7:**
  - The real-git null control `the same commit with one more file runs prepr` fails under W1.
  - The class rule returns 10 lines, as the body says (ev/class_rule.txt).
  - `## Head` names 54bf182104e450c0ac2e6eb007da59b9315e0565.
- **Step 5 / claims:** VERSION, the manifest, RELEASE_NOTES, the claim files and the goldens are untouched. The three-dot diff is 5 files (ev/three_dot_stat.txt).
- **Figures at this head**, against merge base e7c664856 (ev/figures.txt):
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `STRUCTURE RATCHET PASSED`
  - `Architecture score: dS +0.0000 NULL`
- **Self-tests at the head:** app_push 182/0, delivery_row 5/0, pr_args 57/0.
- **Not re-run:** entities and harness_headers, as in round 4 (this container's python3 is 3.11). I cite CI's `fast (3.14)` and `instrument-self-tests` instead, both success at this head.
- **Step 13:** `git merge-tree --write-tree origin/main(49c222280) 54bf1821...` exits 0, tree 342e8c6e8 (ev/merge_tree.txt). There is no conflict.
- **Step 14:** the diff moves no budget, ledger, closure or score. archscore reads dS +0.0000.

## CI (step 11, check-runs API, ev/check_runs_final.tsv)

- The only red is **nightly-status**: failure on run 119298247901. It grades main's scheduled Tests run, and this diff (seat tooling plus its own row) does not reach what it reads, so it is not this PR's red. The body answers it under `## Red checks`.
- The body was edited at 15:47:23Z (PR updated_at). **pr-contract** run 119321268483 started at 15:47:29Z, after that edit and after the last red concluded (15:02:40Z), and is success. So step 11 stands answered on the edited body.
- Everything else is success, skipped or neutral.
- The re-run `Analyze (python)` (119321988077, started 15:48:55Z) concluded success at 16:18:57Z. At the final read (16:19:18Z) all 52 check-runs at this head had concluded, and none is still running.

## Carry of the previous review's items

The round-4 verdict (review/2567 21141036) already routed f053a70e and d3bf9b75, as `Carry: dismissed: the round-3 body was re-taken whole and no longer says this`. It also routed its non-blocking W23 as `Carry: dismissed: defensive usage guard, the path fails closed without it`. This review raises nothing new to carry.

bus-nonce: 84c4ff91ffe593f474b8b71e65da7c72
