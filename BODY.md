Hotfix: main is red on governance / instrument-self-tests (run 43337393276, job 131599549208). The drift step's `selftest_scope.py check` printed `114 gated step(s), 20 refusal(s)`, because 16 entries of tools/ci/selftest_closures.json missed files, probes or dirs the run read. This round makes the re-recorded table the union, per step and dimension, of the merge-base table and the new recording; it changes only tools/ci/selftest_closures.json.

## Head

Orchestrator re-routed this carry from R10-NUDGE-RETIRE to R10-SELFTEST-SCOPE-UNION-GUARD (the table's record path is that group's).

b06e830153c7b9888cf4fccaae00f175690cb283, the reviewed head 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9 plus one commit; merge base with origin/main e4ca2d940efd1e87912d80cb3ebddf8240ba0729; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Block answered (dropped-entries)

Cause: `selftest_scope.py record` replaces a step's entry with the one recording it took, so a recording taken outside the push runner drops reads the runner measures (the same pattern as #3409, #3419, #3506). My first round replaced 16 entries and dropped 9 live path entries, 3 `git` markers and 2 objects flags. Fix: for every step, files, probes, dirs and git are the union of the merge-base entry and the head entry, index and objects are logical OR, and an entry leaves only when its path no longer exists in the tree (none did). No tool or step was edited.

Controls, each from a script comparing the merge-base table (`git show e4ca2d940:tools/ci/selftest_closures.json`) with the head table:
- (a) per step and dimension, entries present at the merge base and absent at the head: 0 (`dropped 0 steps 114`). Paths deleted from the tree: none. Restored: ci-predictor and verdict-bus rosters (file, probe, dir), prepr `.gitattributes`, `tests/env_drift.py`, `tools/merge/ledger_merge.py`, and the `?` git marker on dependency-graph-census, temp-or-machine-path, throwaway-git-helper.
- (b) objects/index flags that went true to false: 0 (dependency-graph-census and throwaway-git-helper objects restored to true).
- (c) `python3 -I tools/ci/selftest_scope.py --self-test`: `selftest_scope self-test: 117 checks, 0 failed`, unchanged. I did not re-trace the 16 steps this round (prepr alone took 771 s for the reviewer). The union is a superset of the round-1 table, which the additions answer the 20 refusals, and the reviewer measured 0 refusals for prepr, field-coverage and beatd against that table; covering more cannot create a refusal. The CI push run on main is the full fresh-trace check; it takes the entries the runner measures, which the union now retains.
- Null control: the 98 entries untouched by round 1 are still byte-identical to the merge base; this round's diff against round 1 touches only the entries listed above.

## Mutation proof

n/a: the change is a measured data file with no production line to delete. The check that goes red without it is the drift step itself.

## Figures

none

## Red checks

instrument-self-tests (drift step, run 43337393276). Merges that added the unrecorded reads, per the reviewer's `git log --diff-filter=A`: #3502 (e4ba9412b2) added tools/audit/seat/scorecard.py; #3461 (005eed2573) added docs/design/2026-11-10-duty-switch-restart-learning and tests/mutation_ledger/{killed_by,survivor_triage}/duty_switch.py; #3503 (4869f1656b) added dev/audit/rounds/round10/protection-census. My round-1 citation of 74fd1a9a49 was a merge of main into a fix branch, not main's merge; it is withdrawn. Could the pull-request lane have refused them: the scoped lane runs every step only when a diff adds a file under tools/; #3461 and #3503 added no tool file, and #3502 added one but the steps that read it were selected by closure, not by this table. Cheaper detector: none that stays cheap. Selecting every step on every diff is the cost R10-CI-SELFTEST-SCOPE removed; a per-PR strace of all 114 steps took about 30 minutes. Recorded as a standing cost of the design.

## Forward-carry

Carry 0: `record` replaces rather than unions, which is what dropped these entries here and in #3409, #3419 and #3506; making record union per step and dimension belongs to the group that owns the record path. Carry: R10-SELFTEST-SCOPE-UNION-GUARD

Carry 1: beatd and review-packet entries are unions of differing recordings, so a group that retires or moves a file they read (R10-NUDGE-RETIRE) re-records those two with `record --step` twice and unions, not once. Carry: R10-SELFTEST-SCOPE-UNION-GUARD

## Non-blocking findings

- `git` entry `?` dropped from three steps: not a path; restored by the union anyway. Carry: R10-SELFTEST-SCOPE-UNION-GUARD
- tests/entities.py not runnable on the reviewer's seat (missing homeassistant): an environment fault, no finding on the head. Carry: R10-SELFTEST-SCOPE-UNION-GUARD

## Friction

none
