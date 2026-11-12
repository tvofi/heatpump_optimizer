Fix review: merge 384b43749ef0014033f8002b3c7b3aa178ef9f73

bus-nonce: a0fb6d117b8c9682e028d9d8a2c89b33
pending-ci: gate

Round 2 of this part, a delta review over the reviewed head 8e6e94427f86b0c15ecdbbe1ed639acc716737ee, from a detached worktree at 384b43749ef0014033f8002b3c7b3aa178ef9f73 with the merge base e59e21fee4629623f2f88ea83be76d527b7d0805 in a second worktree. The delta holds no `custom_components/` line, so the scope was not widened.

## Previous finding

The round-1 block (self-test-red: four instrument self-tests red at the head and green at the merge base) is resolved. Each self-test, run by this seat at both ends:

- `bash tools/pr/app_comment.sh --self-test`: base `67 checks, 0 failed`, head `70 checks, 0 failed`.
- `python3 -I tools/audit/seat/review_carry.py --self-test`: base `29 checks, 0 failed`, head `32 checks, 0 failed`.
- `python3 -I tools/audit/seat/ledger.py --self-test`: base `102 checks, 0 failed`, head `103 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: base `656 checks, 0 failed`, head `657 checks, 0 failed`.

The repair is fixture code only; `carry()` in `tools/pr/app_approve.sh` is byte-identical between the two heads' patches (rule: for each path of `git diff --name-only fc2a7edcf2be8847037d9e8dc5bde460977befa8 8e6e94427f86b0c15ecdbbe1ed639acc716737ee`, the added and removed lines of its patch against its own merge base at each head, compared; only `tests/closures.json` and `tools/ci/selftest_closures.json` differ).

## Delta

Branch-own commits in the delta: 6538f92df7 (the four fixtures), cb5e234a9d (`dev/audit/config/scopes.json`), 87b116dd7b, b16fe0ecc0 and 4dfedf6c3b (`tools/ci/selftest_closures.json`), 7e7accbe20 (`tests/closure.py`, `tests/closures.json`), 36c5e8f42e (the delivery row), and four merges of main. `git show --remerge-diff` on each merge: d5cd21ec0d, f161dfca4b and 384b43749e print only `LEDGER-MERGE: resolved tests/closures.json` and no hunk; 3d5d1a66b2 resolves one conflict, in `tools/ci/selftest_closures.json`.

## Evidence

- RESULT mutant M1 at the head, `tools/pr/app_approve.sh` line 303 `|| ours=0` to `|| ours=1`: `app_comment.sh` `70 checks, 3 failed` ("REFUSE: the same pin-only head when it is only refs/pull/7/head (a fork's)", "refused as a head that is not ours", "and nothing was minted or posted"); `review_carry.py` `32 checks, 2 failed` ("... answers FRESH-REVIEW", "it names the head as not ours"); `merge_train.py` `657 checks, 1 failed` ("a head on no branch of origin (a fork's) carrying an empty ci: commit past its verdict is refused ..."); `ledger.py` `103 checks, 0 failed`, as the body says it would be. Killed by three of four; logs `ev/M1.*.log`.
- RESULT mutant M2 at the head, the unreadable-origin refusal replaced by a listing that names the head as a branch tip (fail open): `ledger.py` `103 checks, 1 failed`, "with origin's branch heads unreadable the same carried head is owed (fail closed)". Killed; `ev/M2.ledger.log`. My replacement text differs from the body's (`heads=""`); the same check kills both.
- The body's first repair mutant (the fixtures put back to their pre-repair form) was not re-run here; round 1 measured those reds at 8e6e94427f86b0c15ecdbbe1ed639acc716737ee directly.
- RESULT `python3 -I tools/audit/check_scopes.py --self-test --repo .`: `SELF-TEST passed` at the head; also passed at the merge base, which lacks `docs/CONTRIBUTING.md`.
- RESULT `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `53 checks, 0 failed` at both ends, the form `governance.yml` runs; round 1 had left it uncounted.
- RESULT `bash tools/pr/app_approve.sh --self-test`: base `322 checks, 0 failed`, head `350 checks, 0 failed`.
- RESULT `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` at the head: `ALL 2709 ENTITY CHECKS PASSED`, rc 0.
- RESULT `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 115 HARNESS HEADER CHECKS PASSED`, rc 0, at the head and at the merge base. The recorded `rc` the diff moves 1 to 0 in `tests/closures.json` is the rc the script exits with; main's table records 1 while the script exits 0 on main's tree here.
- RESULT `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the head: `ALL 343 checks PASSED`, rc 0.
- `git diff origin/main 384b43749ef0014033f8002b3c7b3aa178ef9f73 -- tests/closures.json`: three changed lines, `docs/CONTRIBUTING.md` added to two closures and that `rc`. `git diff --quiet 4145f2852642fd0b5ccb8b7af60d41e896a5eea3 3d5d1a66b2 -- tests/closures.json`: rc 0, the body's claim taken against the main it merged.
- `tools/ci/selftest_closures.json`, the `steps` object at the head against origin/main key by key: one step only at the head (`outside-contract`), none only on main, twelve differing (`app-verdict-poster`, `ci-predictor`, `field-coverage`, `obligations-ledger`, `open-pr`, `policy-lint-mutants`, `pr-args`, `review-carry`, `self-tests-outside-seat`, `selftest-wiring`, `update-pr`, `verdict-bus`), no other top-level key differing. That is the body's thirteen.
- The INERT exception in `tests/closure.py` was not mutated by this seat: its judge is CI's `tests / closures`, the check that went red on the earlier head.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/policy_lint.mjs --budgets`, the fix-review.md row at the head: lines 140 of 140, tokens 2775 of 2775; rc 0.
- `python3 tools/audit/archscore/score.py --diff e59e21fee4629623f2f88ea83be76d527b7d0805`: `Architecture score: dS +0.0000 NULL`, the body's line.
- `python3 -I tools/ci/selftest_scope.py select --base origin/main` at the head: rc 0, log `ev/selftest_scope.head.log`.
- The raise is outside this round's delta and is unchanged since the reviewed head. I read the two paragraphs it buys and the four payments: both paragraphs bind a seat that reads this contract, and I found no fifth payment. That is a reading, with no archscore run per payment by this seat.
- The body's `## Head` names 384b43749ef0014033f8002b3c7b3aa178ef9f73, the head measured, and `refs/pull/3514/head` on origin still read that sha at the last poll. Its line "Merge base with `origin/main`: 4145f2852642fd0b5ccb8b7af60d41e896a5eea3" is the merge base of the code head 7e7accbe20; at the pull request's head it is e59e21fee4629623f2f88ea83be76d527b7d0805.
- `git merge-tree --write-tree origin/main 384b43749ef0014033f8002b3c7b3aa178ef9f73` with origin/main at e59e21fee4629623f2f88ea83be76d527b7d0805: rc 0. No conflict; the head contains main's tip.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`: empty by construction, the merge base is main's tip.
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are not in `git diff --name-status origin/main 384b43749ef0014033f8002b3c7b3aa178ef9f73` (28 paths).
- carry_audit at the head, from the packet: `5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`.
- The body's whole-set self-test run (114 steps, `verdict-bus` and `tick-loop` failing there) was not re-run here: it is CI's `governance / instrument-self-tests`.
- CI at the head: `python3 tools/audit/seat/merge_train.py classify 384b43749ef0014033f8002b3c7b3aa178ef9f73 --pr 3514` printed `WAIT 384b43749ef0014033f8002b3c7b3aa178ef9f73 pending: gate red: none` (rc 3) on every read from 22:55 to 23:27 UTC, 2026-11-12, at least 65 s apart; this verdict is returned with `pending-ci`.
- Check runs read once at 23:16 UTC (run 43323764289): `tests / typing`, `tests / mutation`, `tests / briefs`, `tests / closure-scope`, `governance / policy-docs`, `governance / wave-script`, `governance / delivery-status`, `hassfest / hassfest`, `validate / validate-hacs`, the three `codeql` analyses and `arch-score` concluded success; `governance / instrument-self-tests`, `governance / env-matrix`, `tests / coverage` and `tests / fast (3.14)` in progress; `tests / closures`, `tests / browser` and `tests / arch-instrument` queued. `governance / instrument-self-tests` and `tests / closures`, the two checks this round's repairs answer, had not concluded when I stopped, so neither is confirmed by CI in this verdict.
- `budget-raise-gate / budget-raise-gate` concluded failure at the head: the approval the body's `## Red checks` answers, which follows a verdict. `tests / nightly-status` concluded failure and is outside the set `merge_train.py owed-reds` prints. A second run at the head, 43323765194, shows `gate` concluded failure at 23:15 with `pr-contract` skipped; I did not read its log, and classify still printed `red: none` after it.
- `## Red checks` in the body names `budget-raise-gate`, `tests / closures`, `governance / instrument-self-tests` and `tests / nightly-status`, each with its detector answer; whether a `pr-contract` run at this head accepted the body is not known to this seat.

## Findings

None.
