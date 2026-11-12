main's instrument-self-tests refused `UNDER-SCOPED step prepr`: prepr.sh has run mutant_run.py since #3455 without the closure being re-recorded. Re-recorded the prepr entry in tools/ci/selftest_closures.json with `python3 -I tools/ci/selftest_scope.py record --step prepr` (Linux, strace, 861 s, 0 failed, 0 broken traces) and merged it through the tool's own write_table. Root-cause trigger: #3455 changed what prepr.sh runs without re-recording; cheaper detector: run `selftest_scope.py check` in prepr/ci_predict when a gated step's script changes (not built here; prepr.sh belongs to R10-HOTFIX-PREPR-WC-PAD).

## Head

361040baf232104dd3e842ff06015760d1de61c5 (base origin/main b737e88eee4f)

## Mutation proof

Revert tools/ci/selftest_closures.json to origin/main: `selftest_scope.drift` over the recorded prepr measurement returns `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py', 'tools/audit/seat/mutant_run.py', 'tools/pr/figure_block.py']`; with the fix it returns no prepr refusal.

## Null control

The old table against the same measurement prints the UNDER-SCOPED line above. Entry diff: gains mutant_guard.py, mutant_run.py, figure_block.py; loses .gitattributes, tests/env_drift.py, tools/merge/ledger_merge.py; probes, dirs, git unchanged. The three removals are measured, not a trace gap: the re-record had 0 broken traces, and these are reads the current prepr no longer makes (the first seat's independent run gave the identical diff). Limit stated: I could not run the full `check --traces` (needs CI's whole-job traces), so the 0-refusal line is proven for prepr only; the cloud-dispatcher over-scope is a note, not a refusal, and was left untouched.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
