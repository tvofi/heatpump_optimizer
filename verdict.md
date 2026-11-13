Fix review: merge ef7e3373e763942a38982c679541c5aa750b3935

bus-nonce: a13a694bcd2efeba65e0dbb9b8fb5b92
pending-ci: governance / instrument-self-tests

Round: second review (round 2), a delta over the reviewed head 552638f8dc3a1c7f270448163d44df992c62dac2, measured at ef7e3373e763942a38982c679541c5aa750b3935 in a detached worktree. Scope: `git diff 552638f8dc ef7e3373e7`, which touches two files (tools/ci/selftest_scope.py and tools/ci/selftest_scope_mutants.sh). It contains no production (custom_components/) code, so nothing widens the scope.

## Findings

- Residual: a new mutant of the prune CLI's unreadable-table branch survives the self-test: `if table is None: ... return 1` with `return 0` substituted (`prune-table-none-pass`, ev/own_mutants.txt, 141 checks, 0 failed). That line is in round 1's diff, not in this delta, so it is outside a round-2 review's scope (fix-review.md step 12). Its effect is that prune exits 0 and writes nothing. The table is unchanged, so the shrink guard still holds. Carry: dismissed: outside the round-2 delta scope (fix-review step 12); fail-safe for the table, since the mutant writes nothing and `static`'s shrink guard is unaffected

## Evidence

- ev/HEAD.txt: ef7e3373e763942a38982c679541c5aa750b3935. The PR body's `## Head` names this head and its code head 6a1966196c (step 7 ok).
- Round-1 items, each resolved:
  - Survivor "prune CLI writes nothing": KILLED (prune-cli-no-write, 141 checks, 1 failed).
  - Survivor "prune CLI accepts unknown drops": KILLED (prune-cli-ignores-unknown, 1 failed; also prune-unknown-rc0, 1 failed).
  - Survivor "probe kept by listed directory": KILLED (probe-dir-ancestor-removed, 1 failed; also probe-dir-any-dir, 4 failed).
  - Fail-open on an unresolvable named base: fixed. `table_base` returns (None, "UNRESOLVED base ...") and `static` prints it as a problem line. Mutants unresolved-empty (2 failed), unresolved-dropped-in-static (1 failed) and unresolved-falls-through (2 failed) are all KILLED.
  - Driver: ev/run.sh (round-1's driver, unchanged), with results in ev/own_mutants.txt.
- RESULT own mutants at head: 10 run, 8 killed, 2 survived.
  - table-untouched-skip-removed survives. It is equivalent, as round 1 recorded: an untouched table compares equal to itself.
  - prune-table-none-pass survives. It is outside this round's scope (see Findings).
- RESULT selftest_scope --self-test at head: 141 checks, 0 failed (matches the body).
- RESULT static at head (ev/cheap_checks.txt), each matching the body:
  - SELFTEST_BASE=origin/main: 114 gated step(s), 0 problem(s), rc 0.
  - SELFTEST_BASE=refs/heads/no-such-base: one UNRESOLVED line, 1 problem(s), rc 1.
  - No base named: 0 problem(s).
- RESULT tools/ci/selftest_scope_mutants.sh at head: 25 mutants (rule: its `== ` lines), ending "SELFTEST-SCOPE MUTANTS: every mutant refused", rc 0, no NOT REFUSED line (ev/selftest_scope_mutants_out.txt). This matches the body's 25.
- tests/structure.py: STRUCTURE RATCHET PASSED. VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff (step 5 ok). The delta touches no claim file, golden fixture or budget (step 14: nothing moved).
- `git merge-tree --write-tree origin/main ef7e3373e7`: rc 0, merges cleanly (ev/mergetree.txt).
- Null control: the shrink-guard history figures (#3409 3, #3419 5, #3506 8, the other 13 passing) are round 1's. `shrink_gaps` and `shrink_drops`' exemption code are unchanged in this delta, so I carry them, not re-take them.
- Forward-carry (step 10): unchanged from round 1. It is on handoff/audit-r10-roster for group R10-NUDGE-RETIRE, with its precondition. The packet's carry_audit reports 1 routed, 0 unrouted.
- CI at the head: unreadable. `merge_train.py classify ef7e3373e7 --pr 3551` exits 2 at all 6 polls, 13:24 to 13:32 UTC (ev/classify.log). This is a condition of the merge base that waiting does not change. Each poll read: "REFUSE selftests: the base's governance / instrument-self-tests job 131833357705 is cancelled, which reads no step: an introduced red cannot be ruled out (fail closed)" (ev/classify.log).
  - In the packet's digest, the head's own `governance / instrument-self-tests` is in_progress. I therefore cannot verify CI green, and I name that context under pending-ci so the relay posts this verdict only once CI is green at this head.
  - The packet digest shows `gate` as failure while classify had read "gate red: none". Classify decides, and I did not read the gate's log (API quota).
  - The body's `## Red checks: none` is the fixer's account. I made no per-commit check reads, so I have not re-derived it.
- Finder's harness: none named in the packet. ev/run.sh is my own driver, disclosed as such.
