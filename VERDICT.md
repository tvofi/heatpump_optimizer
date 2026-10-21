Fix review: blocked 93015ecada7190edc054e49a47538704b14e1f34 mutation-survivor: widened skip predicates W4 (open-status) and W7 (row-only head pin) survive the self-test; pr-contract red on the body (carry_audit); row-only drops prepr 7c ancestry reds

Reviewed head: 93015ecada7190edc054e49a47538704b14e1f34 (re-read from the PR at the end of the review: unchanged). Review round: 1 as far as this seat can see.
No roster group: reviewed against the PR body, as the brief says. Role file current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
Worktree: detached at the head. Evidence is in ev/: mutants.txt, mut.sh, body_checks.txt, check_runs.tsv, merge_tree.txt, the self-test logs, and pr_body_at_review.md.

## Blocking

1. **W4 survives: (c)'s "open" conjunct is unpinned.** I deleted ` and OPEN_STATUS in ls[0]` from row_only_verdict's row read, so any anchored row (merged, closed) passes (c). Result: `app_push self-test: 167 checks, 0 failed`. The body says (c) checks "one open row anchored on <N>", but no arm drives a row that is anchored and not open. orow's row is anchored on #8, so it fails the anchor first. Missing test: an anchored #7 row whose status is not open must run prepr.
2. **W7 survives: the claim "The push is pinned to the HEAD the verdict judged, as --recarry's is" is untested for --row-only.** I narrowed the head-moved guard back to recarry only (`[ "$recarry" = 0 ] || [ "$head" = "$RV_HEAD" ]`). Result: `app_push self-test: 167 checks, 0 failed`. Without the guard, a HEAD that moves between the verdict and the push gets pushed with prepr skipped and nothing having judged it: the predicate widens from "this head" to "whatever head is there at push time". The head-moves stub arm exists only for --recarry. It needs a --row-only twin.
3. **pr-contract is red on this head, and the cause is the body.** The failing step is "Every finding the body records names its destination" (jobs API, run 39606287184). I re-ran it locally: `python3 -I tools/audit/carry_audit.py check --body <body>` gives `CARRY-AUDIT: 2 finding item(s): 0 routed, 2 unrouted`, rc=1. The two unrouted items are `## Forward-carry` "none. The --row-only arm ..." and `## Friction` "fixer.md-step-5 ... Carry: none (environment ...)". The same body passes policy_lint --pr-body (0 errors), figure_lint (12 resolved) and preflight (clean). The previous head 947d3631 also carried two red pr-contract runs. The head cannot merge until the body routes those items.
4. **The skip drops prepr step 7c (ancestry reds), and that check can fail on a row-only push.** 7c reads the check runs on the commits already pushed. That is CI state on the live head that can turn red after the live head was pushed, and (a)+(b) pin none of it. So the header's justification, "The other prepr steps read what the verdict has already pinned to the live head, which passed them", is false for 7c. The body's "Why the other prepr steps are not re-run" does not mention 7c.
   - prepr's 7c reads a credential through `gh auth token` (prepr.sh gh_credential).
   - row_only_checks runs only `policy_lint.mjs --pr-body`. Its own red-history walk reads only GITHUB_TOKEN/GH_TOKEN from the environment, and neither update_pr.sh nor app_push.sh sets one before the check (grep: no GH_TOKEN/GITHUB_TOKEN in update_pr.sh or pr_args.sh, and app_push mints only after the gate).
   - Shown in ev/body_checks.txt: with the env token unset, the same command prints `skip red-history ... UNCHECKED` and passes.
   - So on a seat whose credential sits in gh's store (the case 7c exists for, #1860), a row-only push at dispatch time no longer refuses an unanswered red. The first reader of that red becomes the reviewer, as root-cause-unanswered, which is the expensive detector.
   - Cheap repair: run reds_line, or export `GH_TOKEN=$(gh auth token)` around row_only_checks. Pin it with a mutant.
   - Note for propagation, not this PR's to fix: prepr itself does not run carry_audit (no match in prepr.sh). So "pr-contract's own command" is one of pr-contract's steps, not all of them, on both paths. Item 3 got through prepr for that reason.

## Verified

- **Mutants that are killed** (my own, in ev/mutants.txt; mut.sh applies each one and restores the file):
  - W1, widening (b) to "the diff contains the row": 4 failed, including the real-git null control "the same commit with one more file runs prepr".
  - W2, accepting more than one parent: 1 failed (otwo).
  - W3, dropping (d): 2 failed.
  - W5, dropping row_only_checks: 3 failed.
  - W6, update_pr asking for --row-only on a code sha too: `pr_args self-test: 57 checks, 1 failed`, the null control "a code sha never asks for --row-only".
- **Null controls the brief asked for** (diff touching another file, a code sha, a body change): each exists in the self-test and fails under the matching widening mutant (W1, W6, W3). So for those three axes the predicate is exact.
- **Self-tests:**
  - At the head: app_push 167/0 failed, delivery_row 5/0, pr_args 57/0.
  - The body's figures (167/0, 5/0, 59/0) are stated at the code head e6dba2408. Re-run there they reproduce: `pr_args self-test: 59 checks, 0 failed` (ev/selftest_update_pr_at_e6dba240.txt).
  - The 59→57 change at this head comes from main's merge rewriting pr_args.sh's open_pr cap arms, not from this PR.
- **The body's M0–M7 mutant counts:** not re-derived one by one. My own W1–W7 cover the same predicates.
- **Merge with main:** `git merge-tree --write-tree origin/main(22615537a) 93015ecada7190edc054e49a47538704b14e1f34` exits 0, tree 153ec75a, no conflict.
- **VERSION, the manifest and RELEASE_NOTES:** untouched (the three-dot diff is 5 files: the row, INSTRUMENTS.md, pr_args.sh, update_pr.sh, app_push.sh).
- **Claim files:** untouched. env_drift: there are no fixture changes.
- **## Head** names 93015ecada7190edc054e49a47538704b14e1f34.

## CI at this head (check-runs API, ev/check_runs.tsv)

- **pr-contract: failure.** See Blocking 3.
- **nightly-status: failure.** This one grades main. The diff does not reach what it reads (it touches only seat tooling and its own row), so it is not this PR's.
- **Analyze (python) and coverage:** still in progress at verdict time.
- **Everything else:** success, skipped or neutral.

No figure in the body was found false at the head it names.

bus-nonce: 68a19d6bd6420145d20641357a1b572a
