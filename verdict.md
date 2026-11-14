Fix review: merge d4641ef37f41f4b0cd8216d6e7cdb37eb056aef8

bus-nonce: e993805bbd53919eacf16fc5e7d44c70
pending-ci: gate

## Round

Second round (delta) over the reviewed head d9677a53d55bcf114086b15ab97588b7fb429b22. Scope per the packet: `git diff d9677a53d5 d4641ef37f`, which is `594bb842f7` (one line added to `tests/closure.py`'s `INERT_EXCEPT`, `tests/closures.json` moving `tools/audit/seat/instruments/merge_train.py.md` from `inert_reads` into `tests/doc_claims.py`'s closure) and its merge commit. No production code (`custom_components/`) in the delta, so the review does not widen.

## Evidence

- RESULT head: measured d4641ef37f41f4b0cd8216d6e7cdb37eb056aef8, the PR head when read (`ev/HEAD.txt`); the body's `## Head` names it.
- RESULT merge-tree: `git merge-tree --write-tree origin/main d4641ef37f` exits 0, tree 5cd12e2c5b, stderr `LEDGER-MERGE: resolved tests/closures.json`; no conflict.
- RESULT role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- RESULT previous block (introduced instrument-self-tests red at d9677a53d5): the body's `## Red checks` attributes it to step "Show the supervised beat refusing its own fixtures" (beatd case 9, a thread-timing check), not to `selftest_scope`. Re-derived: `git diff --quiet e23124ff6e...HEAD -- tools/audit/seat/beatd.py tests/throwaway_git.py` exits 0 at this head, and `python3 -I tools/audit/seat/beatd.py --self-test` gives `157 checks, 0 failed` three times out of three; `python3 -I tools/ci/selftest_scope.py --self-test` gives `117 checks, 0 failed` (`ev/delta_checks.txt`, `ev/local_checks.txt`). Whether any instrument-self-tests step is red at this head is decided by classify below.
- RESULT closures repair: `./tests/derive_closures.sh --single tests/doc_claims.py` at this head rc 0, `tests/doc_claims.py 232 files`, and leaves the worktree clean, so the committed closure is the derived one (`ev/delta_checks.txt`).
- RESULT mutation proof (delta): the `INERT_EXCEPT` line for `merge_train.py.md` deleted, the same derive exits rc 1 naming `tools/audit/seat/instruments/merge_train.py.md` as an INERT file read by tests; restored (`ev/mutant_inert_except.txt`). Matches the body's control.
- RESULT earlier findings: the previous verdict found no defect beyond CI; its measurements (enumerator 42 -> 1, corpus_tokens earned, G1/P1/P2/P3b mutants, forward-carry in the tree on `handoff/audit-r10-roster`) concern files the delta does not touch, so they stand.
- RESULT red checks: the body answers each red at d9677a53d5 (`tests / closures`, `tests / closures-autofix`, `governance / instrument-self-tests`, `tests / fast (3.14)` inherited weekend clock owned by PR 3578, `pr-contract`, `gate`). Owed-reds set in `ev/owed_reds.txt`.
- RESULT VERSION, manifest, RELEASE_NOTES, claim files: untouched by the delta.
- RESULT policy: a policy change; merges only on the owner's approving review or under mandate 6715477401's policy scope. This verdict approves nothing.
- RESULT introduced: `merge_train.py introduced d4641ef37f` prints `introduced: 0 at d4641ef37f41f4b0cd8216d6e7cdb37eb056aef8 against -: head governance / instrument-self-tests: success`, rc 0 (`ev/introduced.txt`). The previous block is resolved.
- RESULT CI: `merge_train.py classify d4641ef37f --pr 3566` polled every ~60 s from 04:22Z to 04:52Z, every run rc 3 `WAIT d4641ef37f41f4b0cd8216d6e7cdb37eb056aef8 pending: gate red: none` (`ev/classify.log`); no red at this head when returned, hence `pending-ci: gate`.
