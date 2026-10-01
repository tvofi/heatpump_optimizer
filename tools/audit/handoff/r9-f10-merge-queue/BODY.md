R9-F10.9c, stage 1 of 2 (process review items 2 and 3, adopted by tvofi 2026-10-01T16:51Z: "On 2, I want both").

Before: every push to a pull request leaves its older runs going, so a superseded head holds runners until it finishes. A verdicted pull request whose CI ran against an older `main` is merged only after `main` is merged in and the whole CI re-runs. The pinned-grader readers (`codeowners_gap.py`, `prepr.sh` step 3e) accept only the `pull_request.base.sha` forms of `PINNED`, so no workflow can name the merge queue's base without being refused.

After: a newer push to a pull request cancels that pull request's older run in each of the seven workflows that produce a required context. `main` pushes, schedules, dispatches and the autofix bot's own `ci:` pushes are never cancelled. `tools/audit/merge_fastpath.py --head <sha>` tells the orchestrator whether a verdicted pull request may merge on its existing CI, and refuses on any conflict, workflow or claim-file change, pinned grader, unmeasured budget file, FULL select, or overlap between the pull request's selected closures and what `main` changed (`orchestrator.md` §11). Both pin readers accept `pull_request.base.sha || merge_group.base_sha [|| github.sha]`.

Why two pull requests: the graders run pinned to the base, so the base's `codeowners_gap.py` would refuse a workflow that already used the new `PINNED` form. Stage 2 (`handoff/r9-f10-merge-queue-2`, cut from this head) adds `merge_group` to every required workflow and merges only after this one.

**What still runs where (no barrier lost).**
- Concurrency: a cancelled run is only one superseded by a newer run of the same workflow on the same pull request, and branch protection grades the current head, which still runs every required job. The group key is `run_id` for every other event, so each `main` push still runs FULL and unscoped to completion, and a red `main` is still reverted first. `tests/entities.py` checks each event × sender in every file carrying a top-level `concurrency:`.
- Fast path: `ELIGIBLE` means every script the pull request selects ran on its head, and nothing `main` changed since lies in any of their closures under either table; the merge commit's push to `main` then runs FULL. Any doubt is a refusal, and a refusal is the old route (merge `main` in, CI re-runs; with stage 2, the queue). The unscoped lanes (policy-docs, env-matrix, wave-script, briefs, typing, browser, mutation, CodeQL, hassfest, validate-hacs) are not modelled by closures. For those, the fast path relies on the FULL `main` push and revert-first, which is what the docstring states. Measured on this branch's own probe merge with `0bfb8883`: `REFUSED` on `workflow`, `grader` and `full`.
- Pin readers: they still refuse every form they refused before; the two new forms only add the queue's base ahead of `github.sha`.
- Residual: if `CLOSURES_PUSH_TOKEN` is set, the autofix pushes come from that token's user rather than `github-actions[bot]`, so they are not exempt and may cancel the run that will be overtaken anyway; the `ci:` loop guard still stops a second autofix.

_Requested by **tvofi**_

## Head

`c5102ea715260c07fae83e36b3aa2bdba242d856` (code), merge base `90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0`. `main` has since moved to `0bfb8883` (#1815); `git merge-tree` merges it clean, and on that probe merge `tests/entities.py` and `merge_fastpath.py --self-test` both pass.

## Mutation proof

- `tests.yml` `cancel-in-progress: true` → `tests/entities.py`: `FAIL only a pull request's superseded run is cancelled (process review item 3)` naming seven event × sender cells, `1 of 2023 ENTITY CHECKS FAILED`. Before any workflow change the same check named all seven files `no top-level concurrency`.
- `merge_fastpath.py` overlap refusal disabled (`if hit:` → `if False:`) → `--self-test`: three `FAIL ... want ['overlap']`, `18 checks, 3 failed`, rc 1.
- `codeowners_gap.py` `PINNED_OK` without the two queue forms → `--self-test`: `FAIL NULL  PINNED from the queue's base: grader not pinned` and its `else the push's` twin, `2 wrong`.
- `prepr.sh` awk regex without the optional queue clause → `--self-test`: `FAIL governance.yml perturbed (queue-base), with step 3e's run present, passes (null control)`, `130 passed, 1 failed`.
- Removing the `CODEOWNERS` line does not turn `codeowners_gap.py --check` red: the file falls to `NO-PR-JOB` (see Friction). The line takes it to `COVERED`, so the line is ownership, and nothing here claims it is a detector.

## Null control

On the unmodified tree, each instrument above passes: `tests/entities.py` (all), `merge_fastpath.py --self-test` (it includes `ELIGIBLE` fixtures and a measured-budget case that must not refuse), `codeowners_gap.py --self-test`, `prepr.sh --self-test`. The concurrency check carries its own null (a `github.ref`-keyed, always-cancel block must yield six findings).

## Figures

none

## Red checks

none: CI has not run on this head. Unrun here: the full scoped gate (`MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself), typing and real-HA `ha_contract` (no Python 3.14.2 in the cloud seat); CI is their authority. Run: `tests/entities.py`, `tests/structure.py`, the four self-tests above, `codeowners_gap.py --check`, `policy_lint.mjs`, `brief_lint.mjs`, `rules_sync.mjs --check`.

## Forward-carry

`tools/audit/briefs/orchestrator.md` §11 (the orchestrator runs the fast path before merging a pull request whose CI predates `main`). Stage 2 is this group's own second pull request; it is not a carry.

## Friction

codeowners_gap: unclear: `instrument-self-tests` has no job `if:` and runs on `pull_request`, yet `--check` lists `.claude/workflows/gh_comment.py` and `.claude/workflows/policy_lint_mutants.mjs` (both run there) as `NO-PR-JOB`, and `merge_fastpath.py` without its CODEOWNERS line lands there too.

## Approval

Awaiting the owner's approving review at the merge head. This changes what the orchestrator must do: `tools/audit/briefs/orchestrator.md` §11 gains the fast-path step, and §12's lease sentence is shortened to pay its cap. Under the programme mandate (tvofi, 2026-09-30T20:19Z and 2026-10-01T05:03Z) the orchestrator gives that review as tvofi after a merge verdict and green CI; the change itself is the adopted process review (2026-10-01T16:51Z).
