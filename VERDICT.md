Fix review: blocked f16956542b2c4470de5a3e12fc843f97cef1840e mutation-survivor: W11 (row-only (c) drops its one-row conjunct) survives the self-test; a two-line row file skips prepr

Reviewed head: f16956542b2c4470de5a3e12fc843f97cef1840e (re-read from the PR after CI concluded: unchanged). Review round: 2 by this PR's comments (one prior verdict, on 93015eca); the brief calls it round 3.
Role file current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. Worktree detached at the head.
Evidence in ev/: HEAD.txt, mutants.py + mut.sh + mutants_result.txt, w11_demo.sh + w11_demo.txt, body_checks.txt, check_runs.tsv, merge_tree.txt, selftest_*.txt, pr_body_at_review.md.

## Blocking

1. **W11 survives: (c)'s "one row" conjunct is unpinned.** I deleted `len(ls) == 1 and ` from row_only_verdict's row read, so a row file with the open #N row on line 1 and any further lines passes (c). Result: `app_push self-test: 179 checks, 0 failed`.
   - The body says (c) is "That file is one row", and "The row lint is (c)", so (c) is what replaces prepr's row lint on the skip. No arm drives a multi-line row file.
   - ev/w11_demo.txt runs the production row_only_verdict against real git with a two-line 7.md: at the head it prints `... is not one open row anchored on #7`, rc=1. Under W11 it prints `prepr SKIPPED`'s reason, "one open row for #7", rc=0.
   - This is the same shape as round 1's W4 (an unpinned conjunct of (c)). Missing test: a row file of two lines, the first the open anchored #7 row, must run prepr. The stub arm (`rocase` with a two-line `row`) and the real-git arm (`ensure_row` then append a line, amend) each kill it.

## The four items of the previous block, at this head

1. W4 (open-status): killed. 2 failed (`oclosed`, `real git: a row anchored on #7 that is not open runs prepr`).
2. W7 (row-only head pin): killed. 1 failed (`romoved`: got 018, want 100).
3. pr-contract body: both pr-contract runs at this head are success (119272289018, 119273335117). My `carry_audit.py check --body` on the live body: `2 finding item(s): 2 routed, 0 unrouted`, rc=0.
4. 7c ancestry reds: row_only_checks hands the contract gh_credential's token. W8 (drop the `gh auth token` fallback) is killed: 1 failed. The real walk, with gh's stored token and my own invocation at this head: `record red-history 7 commit(s) between origin/main and this head, every failure conclusion across them: nightly-status`, `PR-BODY: 0 error(s)`.

## Mutants (my own, ev/mutants_result.txt; M0 = no replacement)

- M0: 179 checks, 0 failed.
- W1, widening (b) to "the diff contains the row": 2 failed, including the real-git null control `the same commit with one more file runs prepr`. **So a diff touching one more file still runs prepr**, which is the brief's null control.
- W2, `-eq 1` to `-ge 1`: 1 failed.
- W3, dropping (d): 2 failed.
- W4: 2 failed.
- W5, replacing the row_only_checks call with `true`: 8 failed.
- W6, `RO=--row-only` for every code sha: `pr_args self-test: 57 checks, 1 failed` (the null control: a code sha never asks).
- W7: 1 failed.
- W8: 1 failed.
- W9, dropping the carry check: 3 failed.
- W10, dropping (a)'s parent = live check: 2 failed.
- **W11, dropping `len(ls) == 1`: 0 failed. SURVIVES.**
- W12, dropping the anchor: 1 failed (orow).
- W13, dropping the contract's rc propagation: 2 failed.
- W14, skip taken unconditionally: 9 failed.
- W15, `--head HEAD` instead of the judged sha: 1 failed.

These agree with the body's W1–W9 counts exactly.

## Figures re-derived at this head

- `app_push self-test: 179 checks, 0 failed`, `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 57 checks, 0 failed` all reproduce. The body states them at daa1d0dbd. This head adds only main's merge on top.
- `closure.py select --diff 22615537a`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out` reproduces. The same holds against merge base 5d433771a.
- `archscore --diff 22615537a`: `dS +0.0000 NULL` reproduces.
- `carry_audit` 2 routed / 0 unrouted reproduces.
- figure_lint on the body: `FIGURES: 13 resolved, 0 not verified, 0 refused`. preflight: clean.
- Not re-run by me: entities, structure, closure selftest, layout and harness_headers. My container's python3 is 3.11, as the body's Friction says. Cited instead: CI at this head is green on fast, closures, instrument-self-tests and policy-docs.

## Non-blocking (body accuracy, for the next push)

- The body says the skip runs "the two body checks that pr-contract runs". pr-contract runs four body steps: the contract, figure_lint, preflight and carry_audit, plus the version-edit refusal. prepr runs figures (7a) and preflight too. The skip drops figures and preflight, and "Why the other prepr steps are not re-run" does not name them.
- Under (b) and (d) both are functions of the live body plus the caller's note over a tree that changed only by the row, so the drop is defensible. But the body should say so, not undercount.

## Other checks

- Merge: `git merge-tree --write-tree origin/main(5d433771a) f16956542b2c4470de5a3e12fc843f97cef1840e` exits 0, tree fafc1251. There is no conflict.
- VERSION, the manifest, RELEASE_NOTES, the claim files and goldens are untouched. The three-dot diff is 5 files.
- `## Head` names f16956542b2c4470de5a3e12fc843f97cef1840e.
- CI at this head (check-runs API, ev/check_runs.tsv), all concluded: everything is success or skipped, except **nightly-status: failure**. That check grades main's scheduled Tests run, and this diff (seat tooling plus its own row) does not reach what it reads, so it is not this PR's. The body answers it under `## Red checks`, and also answers the earlier pr-contract reds on 947d3631 and 93015eca.
- Forward-carry: the body routes the prepr-lacks-carry_audit finding to R10-POLICY-FIXER-MD.

bus-nonce: add37b67f64bb470070faa4b0f8e06af
