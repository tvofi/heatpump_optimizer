Fix review: merge 73e5d43eea6b6d8ca4bba0313d12e230814595d8

bus-nonce: ce9d119718c8d5b1e7966abb0a4ae40c

Round 2 delta, measured from a detached worktree at 73e5d43eea6b6d8ca4bba0313d12e230814595d8.

## Findings

- Mutant M6 survives. Changing `main()`'s `jobs = sorted({... if is_red(j, l)})` back to `j != "mutation"` leaves `--self-test` at `0 failed`. The self-test drives `predict()`'s rc but never the summary and jobs lines in `main()`, so the "counted in the jobs/reds summary" claim in the body is unpinned. The effect is cosmetic (the rc comes from `predict`), so it does not block. Carry: dismissed: cosmetic summary line, and the rc path that gates the result is pinned by M3 and M4.
- The PR body is stale against the head. It says `ci-autofix.md` gains a table row and that the owner's approval is owed for a policy file, and its Mutation proof still discloses the `is_red` gap that round 2 closed. At this head the three diff files are `tools/pr/ci_predict.py` and `dev/programme/delivery/3042.md` only, and no `ci-autofix.md` copy has changed. The orchestrator should correct the body text before the merge. Carry: dismissed: body text, not tree content. The code and the rule files are as described here, and the policy approval is moot because no policy file changes.

## Evidence

- M3 (drop the `NO NULL CONTROL` clause from `is_red`): `FAIL an unpinned site in a comment-free file is refused, rc=1`, `1 failed`. Green at the head (`ev/M3.txt`).
- M4 (drop `nonull` from `unpinned()`'s return): the same FAIL, `1 failed`. Green at the head (`ev/M4.txt`).
- M1 (`kinds = ("UNWIRED",)`): `FAIL a planted MISMATCH on a changed instrument page is predicted red`, `1 failed` (`ev/M1.txt`).
- The null control is a real check. The same site in the commented file `button.py` gives rc=0 and no refusal, the comment-free `flow_meter.py` gives rc=1, and the MISMATCH on an unchanged page predicts nothing. It goes red under M3 and M4, so it is not vacuous.
- `env -u BASH_ENV python3 tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed` (`ev/selftest.txt`).
- `dev/governance/rules/ci-autofix.md`, `.claude/rules/ci-autofix.md` and `.cursor/rules/ci-autofix.mdc` are byte-identical to origin/main, and the three-dot diff over those paths is empty (`ev/rules.txt`).
- `git merge-tree --write-tree origin/main <head>` exits 0 with no conflicts.
- `merge_train.py classify` on the head returns GREEN (rc 0), with no red and nothing pending.
- The round-1 blockers are closed. The `is_red` and `unpinned()` call-site mutants are now killed by `predict(only="mutation")`. The policy file is no longer touched. The packet shows `FIGURES: 4 resolved`, and `carry_audit` shows 0 unrouted.
- CI's heavy runs (gate, mutation) are cited from the green check-runs, not re-run.
- The body's "Red checks: none" holds. Every gate check on the head is success or skipped.
- This is round 2.
