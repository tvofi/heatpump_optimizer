Root cause for the third recurrence of one red: #2065, #2066 and #2070 each added a harness under the retired `tools/audit/harnesses/` and each turned `fast (3.14)` red on `tests/layout.py` ("re-adds a moved path"), with "Red checks: none" in the body.

**Cause.** The instruction was obeyed and wrong. `CLAUDE.md` Instruments (per-group harnesses in `tools/audit/harnesses/`) and `fixer.md` step 18 (a harness in `tools/audit/harnesses/`) both named a directory that R9-RO-8 moved to `dev/audit/harnesses/` on 2026-10-07; nothing re-pointed them (`tests/layout.py --stale` lists 871 live lines citing a landed move, report-only). **Process state: (d)**, a sound process whose precondition moved underneath it; plus the detector was in no local path (`prepr.sh` never ran the layout guard), so nothing noticed before CI.

**Countermeasure.** (1) Re-point the two instructions to `dev/audit/harnesses/` and `dev/audit/rounds/round9/`. (2) `prepr.sh` step 6e (6d is `predict_line`) runs `tests/layout.py --guard` against the merge base, so the process notices its own changed precondition for any future move, not only this one. Not built: a `pre-edit.sh` hook (a Bash-created file bypasses it, and prepr covers every route at 0.4 to 2.1 s); the other stale lines (871, the move stage's report-only backlog).

**Cost test.** Cheaper detector: `layout.py --guard` run locally. Standing cost 0.44 s on a quiet box (my run, load not recorded) and 0.95 to 2.10 s over 11 runs at load average 46 to 58 on 8 cores (the reviewer's measurement); take 0.4 to 2.1 s. Defect cost, three samples of the fast job going red on this guard: #2065 30m28s (check-run 113574473913), #2066 30m48s (113577108665), #2070 29m50s (113595667988), so 29m50s to 30m48s each, three times in one evening. Verdict: passes by three orders of magnitude.

**Class search (root-cause.md section 3).** The same obeyed-and-wrong shape also sits in `.claude/workflows/audit-find.js` and `audit-verify.js`, which tell a seat to write under the retired round directory. Disposition: not re-pointed here (about twenty strings across two wave scripts, graded by the wave-script checks), carried to R9-RO-9 (#1922, the stage that retires canon) in `dev/programme/carries/carry-1922.json`. Caught meanwhile: a planted new file under a retired round directory is refused by the guard's zero-categories arm (rc 1), so round 10's first commit fails in prepr, not in CI.

CLAUDE.md is policy: it merges on the owner's approving review (orchestrator gives it under the mandate).

## Head

91b77d0cd3acbc1a5f13c400b6dd60a8910e86f4

## Mutation proof

Replacing the guard call in `moved_line` with `out=ok; r=0` turns three prepr self-test rows red: "a new file under a landed-retired directory is refused" (got 0, wanted 1), "and the refusal names the new path", "and the ok line is the guard's own, so it ran" (212 passed, 4 failed in round 0; the fourth is the mutant file not being the tracked prepr.sh).

## Null control

The unmodified tree: `python3 tests/layout.py --guard --base origin/main` prints `GUARD: 0 refusal(s)`. The self-test's clean row (same file at `dev/audit/harnesses/`) passes and prints the guard's own ok line; a tree with no `tests/layout.py` skips (rc 3), never refuses. With a planted `tools/audit/harnesses/draw_range_evidence.py` committed over origin/main, the guard prints `placement: ... re-adds a moved path; it lives at dev/audit/harnesses/`, rc 1, 0.44 s (the defect, reproduced). Full self-test: 218 passed, 0 failed.

## Figures

- 0.44 to 2.10 s guard wall time, 871 stale lines: `python3 tests/layout.py --guard`, `python3 tests/layout.py --stale`
- 218 passed, 0 failed: `bash tools/pr/prepr.sh --self-test`

## Red checks

none

## Forward-carry

`dev/programme/carries/carry-1922.json` (the new fifth entry): the round-runner workflows' retired round paths.

## Friction

none

## Approval

Pending, not yet given. This diff re-points one line each in `CLAUDE.md` and `dev/governance/roles/fixer.md` (two retired directory names to their current ones) and states no new obligation. It merges only on the owner's approving review at its head, which the orchestrator gives under the standing mandate; this section records that the approval is owed, not that it was granted.

