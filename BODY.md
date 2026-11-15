Render the figure block against the pull request's recorded `base.sha`, the base `pr-contract` verifies, not `origin/main`'s tip. Group R11-HOTFIX-FIGURE-BLOCK-BASE (triage `dev/programme/triage/r10-round-end.md#P774`; cause `dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`, state (c)).

## Head

`3dfddc96b58be0dc7f8ba36cd7b6caf7e8750a18` is this PR's head, measured at merge base b3831ff64e (origin/main moved on since; the tree merges clean, `git merge-tree --write-tree origin/main HEAD`, 2026-11-15).

## Mutation proof

`update_pr.sh` (`pr_recorded_base` line, `# mut:updbase`) and `open_pr.sh` (`# mut:opbase`) deleted line by line by `pr_args.sh --self-test`: it goes red-as-expected on "mutant mut:updbase" and "mutant mut:opbase" (each arm asserts the render falls back to `origin/main`); both arms pass, i.e. the mutants are killed.

## Null control

`pr_args.sh --self-test` at the merge base: 262 checks, 0 failed. With a recorded base equal to main's tip, "null control: equal bases render the one sha, as before" passes. An unreadable recorded base refuses and pushes nothing.

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at the head: 269 checks, 0 failed (7 added).
- Precondition asserted in the test: main has moved past the stub's recorded base before the differing-base case.
- Class seams, enumerated at this head by `grep -n 'figure_block.py" refresh' tools/audit/seat/*.sh | grep -v ':#'` (comment lines excluded; it returns exactly the three call sites, none of them a bare `refresh` without `--base`): `update_pr.sh` upd_figures: closed here; `open_pr.sh` op_figures p2: closed here; `body_push.sh` (the handoff body push, round-1 block): closed in this round. At `body_push.sh` a pull request is known to exist when origin holds `fix/<topic>`; the recorded `base.sha` of its open pull request is rendered against, and an unreadable one (pull-request list or base, read by the REST API: `gh pr list` is GraphQL, refused in cloud sessions) refuses with the body kept and nothing pushed. Where no pull request exists, `origin/main` is the base, as the open will record it (`open_pr.sh` op_figures p1 runs before the PR exists, p2 re-renders). Head-move half: R11-PRE-SHARED-FILES.
- Round-2 arms in `bash tools/audit/seat/body_push.sh --self-test` (49 checks, 0 failed at the head; the same command at the merge base, extracted by `git archive origin/main tools tests`, prints 41 checks, 0 failed: 8 added): precondition that the stub's recorded base is not origin/main's tip; no `fix/t` renders `origin/main`; an open pull request renders its recorded base; null control with equal bases renders the one sha; "MUTANT mut:bpbase (its line deleted)" falls back to `origin/main`, killing the recorded-base arm (a mutant copy of the script, `# mut:bpbase`); an unreadable recorded base refuses before the refresh and pushes nothing; `fix/t` with no open pull request renders `origin/main`.
- Failing-first control: the same self-test with only ` --base "$FB"` deleted from the refresh call (stub `figure_block.py` takes the index of `--base`, so it fails) reads 26 failures, including the recorded-base, null-control and mutant arms; restored, 0 failed.

## Red checks

`instrument-self-tests` (step "Show the body PATCH refusing its own fixtures"), red at d24189bd, green at base b3831ff64e. Cause: my round-2 `body_push.sh --self-test` arm built its stand-in base with `git commit-tree` outside `throwaway_git_env`, so it needed a global git identity that the runner lacks; the hosts the seat ran on had one, so it passed there. Reproduced with `env -i PATH=/usr/bin:/bin HOME=/tmp/h bash tools/audit/seat/body_push.sh --self-test`: 49 checks, 1 failed (`unable to auto-detect email address`). Fix is in the script's own self-test arm (the call now runs inside `throwaway_git_env`); the expectations are unchanged. Same command at the head: 49 checks, 0 failed. `body_patch.sh --self-test` (109) and `pr_args.sh --self-test` (269), both under `env -i`, 0 failed. Process state (c): the step ran and passed on the seat's host while the runner differs. Cheaper detector: running the self-test under `env -i` (about 7 s for body_push), which the instrument has no standing path for; recorded, not built, as the same arm class has not recurred.

## Forward-carry

none

## Friction

none
