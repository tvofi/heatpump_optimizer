Fix review: blocked 86501f71dcdd7841aad715682f4ca16e9c7f28df mutation-vacuous: null_control_preds call site in unpinned() and is_red() survive the self-test

bus-nonce: e6b0ac7d0110bb602babe3b19bc243d9

Round 1. Head measured: 86501f71dcdd7841aad715682f4ca16e9c7f28df (detached worktree).

## Block

The two new predicates are killed by the self-test. The path that turns them into a refusal is not exercised by it. I planted two mutants there and the self-test stayed at `ci_predict self-test: 0 failed`:

- M3: in `unpinned()`, replace `nonull = null_control_preds(...)` with `nonull = []`. Survives (ev/mutant3-callsite.txt). The "refuses a pool with no whole-line comment" behaviour from carry (2) can be deleted from the predictor's real path with no red.
- M4: in `is_red`, drop `or line.startswith("NO NULL CONTROL")`. Survives (ev/mutant4-isred.txt). The refusal then no longer sets rc=1 or names the job in `main()`.

The null-control self-test arm calls `null_control_preds` directly. Nothing runs `predict`, `unpinned` or `is_red` over a diff that adds an unpinned site in a comment-free file. Carry (2) asks that the predictor refuse, so the arm needs to reach that call site. Add a self-test arm at `predict(..., only="mutation")` or at `is_red` itself, plus a null control.

## Findings

- `dev/governance/rules/ci-autofix.md` (and its two generated copies) lose text unrelated to this fix. The first line reads "`skip-manual-repair-owed` —" then "and did not happen.", so the dropped "a repair was owed" leaves the sentence ungrammatical. The diff also strips `(#523)`, `(#1886, R9-CI-1)`, `(#1864)`, `(#1310)`, `(R9-CI-1)`, `(#2840)`, "kept until M-3" and "(`orchestrator.md` section 11)". The rule's obligations survive, so it is not loosened, but this is a policy edit the body must state, and it needs the owner's approval before merge. Restore the sentence, or say why the citations were removed. Carry: R10-FLY-CIPREDICT-GAPS | #3042 | O1 | dismissed: fixed in this PR's next round, not deferred.

## Evidence

- `env -u BASH_ENV python3 tools/pr/ci_predict.py --self-test` at the head: summary line `ci_predict self-test: 0 failed` (ev/selftest-head.txt).
- Carry (1): all five kinds are now kept (UNWIRED, MISMATCH, UNINDEXED, DUPLICATE, MISSING), filtered to changed files. The planted-MISMATCH arm and its null control (an unchanged tree predicts nothing) are both present and pass.
- Mutant M1 (filter restored to UNWIRED only): killed. `FAIL a planted MISMATCH on a changed instrument page is predicted red`, 1 failed (ev/mutant1-wiring.txt).
- Mutant M2 (`null_control_preds` always empty): killed. `FAIL a pool of only a comment-free file is predicted red`, 1 failed (ev/mutant2-null.txt).
- Base vs head for the new arms: the arms do not exist on the base. M1 and M2 stand in for the base behaviour of each predicate.
- Merge with origin/main: `git merge-tree --write-tree` exits 0, no conflict.
- CI classify at the head: rc=3 WAIT, checks still pending (`tests / fast`, `closures`, `coverage`, `browser` and others in_progress). Not GREEN at the time of this verdict, so CI is not cited.
- The review packet reports 4 figures resolved, 0 refused, 0 carry-audit findings. The packet's note says the head lacks origin/main 14ed135512e3d7db899081f2c2639ce5674b8f2a.
- `closing summary completeness claim`: the docstring says "every index gap ... naming a changed file". The filter also accepts a path suffix match (`c.endswith("/" + p)`) for DUPLICATE targets, which is wider than exact naming. This is intended and stated in a code comment.
- I did not check VERSION, the manifest or the notes heading beyond the diff stat. The diff touches none of them.
