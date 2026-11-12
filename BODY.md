Hotfix. On main (first seen at 6e100ef6) the push-only step "Refuse a self-test read set the committed table misses" of governance / instrument-self-tests is red: self-tests read files the committed table `tools/ci/selftest_closures.json` does not list. Re-recorded the 16 drifting steps by the rule `tools/ci/selftest_scope.py` states (`record`, Linux/strace). Only that one file changes. Main had moved once (#3501, 2b4515dc); the drift was re-derived at that head, so open-pr, pr-args and update-pr are in the set as well.

Which merge introduced each read (`git log f24eed01d7..2b4515dc52 -- <path>`, then the first PR merge containing the commit):
- `tools/audit/seat/r10_disinfection_setpoint_mutants.py` (selftest-wiring, hooks-setup, open-pr, pr-args, update-pr): #3497 (and #3452 before it).
- `tools/site/day_chart.mjs` (field-coverage, selftest-wiring, open-pr, pr-args, update-pr): #3458.
- `tools/pr/figure_block.py`, `tools/pr/figure_registry.json`: no commit in the range; added at 42e179c188 (#3355), read by steps from earlier callers, not by #3479 or #3497.
- `tools/audit/seat/gh_read.py`, `merge_train.py` (programme-pulse): #3462, #3471, #3476, #3470.
- `open_pr.sh`, `pr_args.sh` (open-pr, pr-args, update-pr): #3501; `tools/pr/prepr.sh` changes: #3488.
- #3479 touched no file any step reads.
- `cfr_exclusions.json`, `.gitattributes` probes, `.gitmodules`/`tools/.git` probes and index/objects reads (tick-loop) are fresh-clone reads the previous recording (from a session with drivers installed) missed.

## Head
f5a2c9cba6b6bab1242e381bed5b2960043eb45f on origin/main 2b4515dc52821ad721225090d329c224dbddafae (unmoved at 2026-11-12, `git fetch origin main` before the handoff; no second prepr run needed).

## Mutation proof
n/a: data-only change to a measured table; no production predicate. The check that refuses is `selftest_scope.py check`, red on main at these steps. The traces of the recording were removed by `record`, so the per-miss check below compares the quoted drift lines against the old and new table.

## Null control
Command: python3 over `git show origin/main:tools/ci/selftest_closures.json` and the new file, testing each drift line's missed path against the step's files/probes/dirs. Old table: every one of the checked misses (policy-lint-mutants probes, field-coverage files, verdict-bus probes, selftest-wiring files, programme-pulse files, open-pr files, prepr dirs, tick-loop probes) reads False; new table: all True; tick-loop index/objects False/False -> True/True. The old-table False column is the null control (a table that already covered them would have printed True).

## Figures
- `python3 -I tools/ci/selftest_scope.py record --step <16 steps>` in a fresh clone at 2b4515dc without merge drivers: 16 step(s), 0 failed, 0 broken trace(s).
- `tools/pr/prepr.sh` on the committed tree: PRE-PR rc=0, MODE: FULL. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks
instrument-self-tests "Refuse a self-test read set the committed table misses" (push-only, main). Cheaper detector: `selftest_scope.py check` needs a traced run (strace over every step, long), so prepr cannot run it; `prepr.sh` does not call `selftest_scope.py` at all (grep: 0 matches). A diff that adds a read cannot be predicted without that trace; standing cost of a prepr-side detector is a full traced run per push, so none is proposed here; the countermeasure remains main's push-only step plus this re-record. Third instance of the family (#3487, this): root-cause seat should price a cheap static approximation.

## Forward-carry
none

## Friction
none
