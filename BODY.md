Render the figure block against the pull request's recorded `base.sha`, the base `pr-contract` verifies, not `origin/main`'s tip. Group R11-HOTFIX-FIGURE-BLOCK-BASE (triage `dev/programme/triage/r10-round-end.md#P774`; cause `dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`, state (c)).

## Head

`bd14236dfa7c842e8a96d8e6f072a18ae484a2cb` is this PR's head, measured at merge base b3831ff64e (origin/main moved on since; the tree merges clean, `git merge-tree --write-tree origin/main HEAD`, 2026-11-15).

## Mutation proof

`update_pr.sh` (`pr_recorded_base` line, `# mut:updbase`) and `open_pr.sh` (`# mut:opbase`) deleted line by line by `pr_args.sh --self-test`: it goes red-as-expected on "mutant mut:updbase" and "mutant mut:opbase" (each arm asserts the render falls back to `origin/main`); both arms pass, i.e. the mutants are killed.

## Null control

`pr_args.sh --self-test` at the merge base: 262 checks, 0 failed. With a recorded base equal to main's tip, "null control: equal bases render the one sha, as before" passes. An unreadable recorded base refuses and pushes nothing.

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at the head: 269 checks, 0 failed (7 added).
- Precondition asserted in the test: main has moved past the stub's recorded base before the differing-base case.
- Class seams, enumerated at this head by `grep -n 'figure_block.py" refresh' tools/audit/seat/*.sh | grep -v ':#'` (comment lines excluded; it returns exactly the three call sites, none of them a bare `refresh` without `--base`): `update_pr.sh` upd_figures: closed here; `open_pr.sh` op_figures p2: closed here; `body_push.sh` (the handoff body push, round-1 block): closed in this round. At `body_push.sh` a pull request is known to exist when origin holds `fix/<topic>`; the recorded `base.sha` of its open pull request is rendered against, and an unreadable one (pull-request list or base) refuses with the body kept and nothing pushed. Where no pull request exists, `origin/main` is the base, as the open will record it (`open_pr.sh` op_figures p1 runs before the PR exists, p2 re-renders). Head-move half: R11-PRE-SHARED-FILES.
- Round-2 arms in `bash tools/audit/seat/body_push.sh --self-test` (49 checks, 0 failed at the head; the same command at the merge base, extracted by `git archive origin/main tools tests`, prints 41 checks, 0 failed: 8 added): precondition that the stub's recorded base is not origin/main's tip; no `fix/t` renders `origin/main`; an open pull request renders its recorded base; null control with equal bases renders the one sha; "MUTANT mut:bpbase (its line deleted)" falls back to `origin/main`, killing the recorded-base arm (a mutant copy of the script, `# mut:bpbase`); an unreadable recorded base refuses before the refresh and pushes nothing; `fix/t` with no open pull request renders `origin/main`.
- Failing-first control: the same self-test with only ` --base "$FB"` deleted from the refresh call (stub `figure_block.py` takes the index of `--base`, so it fails) reads 26 failures, including the recorded-base, null-control and mutant arms; restored, 0 failed.

## Red checks

none

## Forward-carry

none

## Friction

none
