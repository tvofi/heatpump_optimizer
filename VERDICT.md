Fix review: merge 5b39c4111ca5ae464a607490c42d70c638af24a3

bus-nonce: de0e17ec4ef5aab337fef259249981d4

Round: 2

## Summary

This is round 2, reviewing the repair of the round-1 block (verdict/3260, blocked 2fa354bf, mutation-vacuous). The repair is commit 804fc0419. It adds 26 self-test lines to `tools/audit/carry_audit.py` and changes no production line: one `check --body` arm and one `pr` arm, each with a null control. Mutants A and B (`:929` and `:927`) are now killed, and so is the `pr` mutant (`:956`). The self-test figure is no longer quoted. Nothing from round 1 survives, and the repair raises nothing new.

## Findings

none

## Evidence

- Head measured: 5b39c4111ca5ae464a607490c42d70c638af24a3, which is the PR head and the head named in `## Head` (ev/HEAD.txt). The merge base is 28482eceeb6b9809e44b12d80fc994282cc21645. `git diff <base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- `review_carry.py 2fa354bf 5b39c411` prints FRESH-REVIEW, so I re-reviewed the change. The PR's own move since round 1 is 804fc0419 (+26 lines in the self-test). The rest of `2fa354bf..804fc041` is main merged in through b7bb2722b.
- Finder's harness at both ends: `python3 -I tools/audit/carry_audit.py --self-test` prints `392 checks, 0 failed` at the head and `364 checks, 0 failed` at the merge base. The difference is 28: round 1's 24 arms plus this repair's 4 (ev/mutants.txt).
- Mutant A, `tools/audit/carry_audit.py:929` with `dests` dropped from `folds_rc(...)`: `392 checks, 1 failed`, red on `check --body refuses a fold answered Carry: a group the roster lacks`. Killed.
- Mutant B, `:927` with `if FOLD_LINE.search(body):` changed to `if False:`: 1 failed, the same arm. Killed.
- Mutant C, `:956` with `dests` dropped from `pr`'s `folds_rc`: 1 failed, red on `pr refuses a fold answered Carry: a group the roster lacks`. Killed. Mutant C2, with `pr`'s whole `| folds_rc(...)` deleted: 1 failed. Killed.
- Null controls: `Fold (a): Carry: R10-CONS` is accepted (rc 0) through both `check --body` and `pr`, and both arms are green on the unmutated head.
- Mutant D, `:933` with `dests = dests or load_dests(` changed to `dests = load_dests(`, survives. This mutant is equivalent: the roster is loaded again from the same arguments, so the result is the same and only a second read is spent. Carry: dismissed: evidence, not a finding
- The file was restored after each mutant, and `git diff --stat` printed empty (ev/mutants.txt).
- Figures: the body now names the self-test as its instrument instead of quoting a count, which settles round 1's 366-against-364 finding. `python3 tests/closure.py select --diff <base>` prints `MODE: FULL`, which matches the body. The body's "39 carries" was correct when taken. At roster ref 1f11980fa the group holds 42; carries 40-42 are this PR's own body items 62b6e444, 106e7c34 and 7d9e145f, which the roster seat appended to R10-BODY-CONTRACT afterwards (ev/figures.txt).
- Merge: `git merge-tree --write-tree origin/main(80016a71f) 5b39c411` rc 0, with `LEDGER-MERGE: resolved tests/closures.json` and no conflict (ev/merge-protected.txt).
- Protected files: VERSION, manifest.json, RELEASE_NOTES.md, both claim files and every `*_budgets.json` are untouched in the three-dot diff. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/brief_lint.mjs` rc 0, with `LEGACY-CONTROL ok`. The delivery row dev/programme/delivery/3260.md is in the diff (ev/suite.txt).
- I could not run `tests/entities.py` in this container: venv-ci lacks homeassistant and venv-ha lacks paho. The `--branch "$HEAD_REF"` pin is byte-identical to round 1, where its mutant was killed (`1 of 2638 ENTITY CHECKS FAILED`). CI's `tests / fast` runs it at this head (see CI below).
- Each round-1 Evidence item (the earlier mutants, the carry-1795 move, the nine #3227 carries) concerns lines the repair does not touch, so each still stands.
- CI: `merge_train.py classify 5b39c411 --pr 3260` printed `GREEN 5b39c4111ca5ae464a607490c42d70c638af24a3 pending: none red: none`, rc 0, at 23:57:09Z (ev/classify.txt, ev/classify-log.txt).
- The earlier red `gate` (job 128221318581) was only the edit-run gate deferring to code run 42310918335 (`FAIL run(s) [42310918335] at this head are still being judged; their gate decides`). Once that run concluded, the gate went green on rerun (23:55-23:56Z). Every page of the commit's check-runs now lists no failure, cancelled or timed-out run, and `pr-contract / pr-contract` is a success at 23:54:27Z (ev/checks.txt). The body's `## Red checks` therefore owes nothing for that deferral. Carry: dismissed: evidence, not a finding
