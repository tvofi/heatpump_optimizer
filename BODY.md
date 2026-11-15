Render the figure block against the pull request's recorded `base.sha`, the base `pr-contract` verifies, not `origin/main`'s tip. Group R11-HOTFIX-FIGURE-BLOCK-BASE (triage `dev/programme/triage/r10-round-end.md#P774`; cause `dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`, state (c)).

## Head

`86d87374e525672014f4bae25dcef396fe0c82f5` is this PR's head, measured at merge base b3831ff64e (origin/main, 2026-11-15).

## Mutation proof

`update_pr.sh` (`pr_recorded_base` line, `# mut:updbase`) and `open_pr.sh` (`# mut:opbase`) deleted line by line by `pr_args.sh --self-test`: it goes red-as-expected on "mutant mut:updbase" and "mutant mut:opbase" (each arm asserts the render falls back to `origin/main`); both arms pass, i.e. the mutants are killed.

## Null control

`pr_args.sh --self-test` at the merge base: 262 checks, 0 failed. With a recorded base equal to main's tip, "null control: equal bases render the one sha, as before" passes. An unreadable recorded base refuses and pushes nothing.

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at the head: 269 checks, 0 failed (7 added).
- Precondition asserted in the test: main has moved past the stub's recorded base before the differing-base case.
- Class seams (the two `figure_block.py refresh` call sites, found with `grep -n "figure_block.py\" refresh" tools/audit/seat/*.sh`): `update_pr.sh` upd_figures: closed here; `open_pr.sh` op_figures p2: closed here; op_figures p1 runs before the PR exists, so no recorded base exists and `origin/main` is the base the open will record (p2 re-renders anyway). Head-move half: R11-PRE-SHARED-FILES.

## Red checks

none

## Forward-carry

none

## Friction

none
