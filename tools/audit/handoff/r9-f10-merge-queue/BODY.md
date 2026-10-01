R9-F10.9c, stage 1 of 2 (process review items 2 and 3, adopted by tvofi 2026-10-01T16:51Z: "On 2, I want both").

Before: every push to a pull request leaves its older runs going, so a superseded head holds runners until it finishes. A verdicted pull request whose CI ran against an older `main` is merged only after `main` is merged in and the whole CI re-runs. The pinned-grader readers (`codeowners_gap.py`, `prepr.sh` step 3e) accept only the `pull_request.base.sha` forms of `PINNED`, so no workflow can name the merge queue's base without being refused.

After: a newer push to a pull request cancels that pull request's older run in each of the seven workflows that produce a required context. `main` pushes, schedules, dispatches and the autofix bot's own `ci:` pushes are never cancelled. `tools/audit/merge_fastpath.py --head <sha>` tells the orchestrator whether a verdicted pull request may merge on its existing CI, and refuses on any conflict, workflow or claim-file change, pinned grader, unmeasured budget file, FULL select, or overlap between the pull request's selected closures and what `main` changed (`orchestrator.md` §11). Both pin readers accept `pull_request.base.sha || merge_group.base_sha [|| github.sha]`.

Why two pull requests: the graders run pinned to the base, so the base's `codeowners_gap.py` would refuse a workflow that already used the new `PINNED` form. Stage 2 (`handoff/r9-f10-merge-queue-2`, cut from this head) adds `merge_group` to every required workflow and merges only after this one.

**What still runs where (no barrier lost).**
- Concurrency: a cancelled run is only one superseded by a newer run of the same workflow on the same pull request, and branch protection grades the current head, which still runs every required job. The group key is `run_id` for every other event, so each `main` push still runs FULL and unscoped to completion, and a red `main` is still reverted first. `tests/entities.py` checks each event × sender in every file carrying a top-level `concurrency:`.
- Fast path: `ELIGIBLE` means every script the pull request selects, and every `run_always` script in `tests/run.sh` (`harness_headers.py`, `env_drift.py --claims-only`, `closure.py selftest`, `layout.py`), ran on its head, and nothing `main` changed since then lies in any of their closures under either table. Any refusal sends the pull request back to the old route: merge `main` in and re-run CI, or, once stage 2 lands, the queue. The push the merge makes to `main` still runs FULL. The unscoped lanes (policy-docs, env-matrix, wave-script, briefs, typing, browser, mutation, CodeQL, hassfest, validate-hacs) are not modelled by closures; for those, the fast path relies on the FULL push and revert-first, as the docstring states.
- **Round 2 (#1823 review).** `harness_headers.py` is `run_always` and reads INERT docs through D6's `claims.py`, which no closure records. The reviewer's probe: the pull request adds a link to `tools/audit/README.md` in `DISCLAIMER.md`, and `main` deletes that file. Round 1 said `ELIGIBLE` on that pair, although the merged tree has a false claim. Now, a file on either side that no closure records refuses as `unrecorded` while any `run_always` script exists, and `run_always` scripts count as selected for `overlap`. **Cost, measured:** over the last 30 merges on `main` (`411368b6`), this conservative rule leaves 0 pairs eligible, against 5 without it. Nearly every merge adds a `docs/delivery/<N>.md` row, which no closure records. Narrowing it soundly needs the `run_always` scripts' unrecorded reads to be recorded, which is a `closure.py` recorder change. That is not done here; see Forward-carry.
- Main-moved rule: `orchestrator.md` §11 keeps PROC-1's "CI green at a head containing current `origin/main`" and names the fast path as its one exception, merged by the orchestrator as the queue's only bypass.
- Pin readers: they still refuse every form they refused before; the two new forms only add the queue's base ahead of `github.sha`.
- Residual: if `CLOSURES_PUSH_TOKEN` is set, the autofix pushes come from that token's user rather than `github-actions[bot]`, so they are not exempt and may cancel the run that will be overtaken anyway; the `ci:` loop guard still stops a second autofix.

_Requested by **tvofi**_

## Head

`ccc8c594963435bd8073bb79e47cf9e748cfe701` (code). It is round 1's `c5102ea7`, then `origin/main` at `411368b6` merged in as `aa42c991` (the `orchestrator.md` conflict with #1818), then the round-2 fix.

## Mutation proof

- `tests.yml` `cancel-in-progress: true` → `tests/entities.py`: `FAIL only a pull request's superseded run is cancelled (process review item 3)` naming seven event × sender cells, `1 of 2023 ENTITY CHECKS FAILED`. Before any workflow change the same check named all seven files `no top-level concurrency`.
- `merge_fastpath.py` overlap refusal disabled (`if hit:` → `if False:`) → `--self-test`: three `FAIL ... want ['overlap']`, rc 1 (round 1, 18 checks).
- The `unrecorded` class disabled → `--self-test`: `FAIL #1823's probe: ... got [], want ['unrecorded']` and `FAIL an unrecorded file on main's side alone refuses too`, `25 checks, 2 failed`.
- `run_always` scripts not counted as selected → `FAIL main changed what a run_always script reads, which the pull request never selected: overlap`, `25 checks, 1 failed`.
- The reviewer's probe as real commits on `origin/main`: round 1's script prints `FASTPATH ELIGIBLE`, and this head's prints `REFUSE unrecorded` for `DISCLAIMER.md` and for `tools/audit/README.md`.
- `codeowners_gap.py` `PINNED_OK` without the two queue forms → `--self-test`: `FAIL NULL  PINNED from the queue's base: grader not pinned` and its `else the push's` twin, `2 wrong`.
- `prepr.sh` awk regex without the optional queue clause → `--self-test`: `FAIL governance.yml perturbed (queue-base), with step 3e's run present, passes (null control)`, `130 passed, 1 failed`.
- Removing the `CODEOWNERS` line does not turn `codeowners_gap.py --check` red: the file falls to `NO-PR-JOB` (see Friction). The line takes it to `COVERED`, so the line is ownership, and nothing here claims it is a detector.

## Null control

On the unmodified tree, each instrument above passes: `tests/entities.py` (all), `merge_fastpath.py --self-test` (25 checks; each new case has a null control, the same pair with no `run_always` script, which must stay `ELIGIBLE`), `codeowners_gap.py --self-test`, `prepr.sh --self-test`. The concurrency check carries its own null (a `github.ref`-keyed, always-cancel block must yield six findings).

## Figures

- Eligible pairs over the last 30 merges on `main` at `411368b6`, with and without the `unrecorded` class: a replay outside this tree, with no command that resolves at the code head. It feeds each merged pull request and the merge before it to this head's `decide()`, using `main`'s closure table, the head's closure table, the restore pathspecs, and `run_always` scripts read from both ends' `tests/run.sh`. The replay script and both outputs are in `/mnt/project-files/audit-r9/fix/evidence/F10.9c-r2/` (`replay_pairs.py`, `fastpath_replay_r2.txt`, `fastpath_replay_r2_without_unrecorded.txt`).

## Red checks

none: CI has not run on this head. Unrun here: the full scoped gate (`MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself), typing and real-HA `ha_contract` (no Python 3.14.2 in the cloud seat); CI is their authority. Run: `tests/entities.py`, `tests/structure.py`, the four self-tests above, `codeowners_gap.py --check`, `policy_lint.mjs`, `brief_lint.mjs`, `rules_sync.mjs --check`.

## Forward-carry

`tools/audit/briefs/orchestrator.md` §11: the orchestrator runs the fast path before merging a pull request whose CI predates `main`. The fast path stays near-useless until the `run_always` scripts' unrecorded reads are recorded (a `closure.py` recorder change), because the `unrecorded` class refuses on every `docs/delivery` row. It is rostered as R9-F10.9d (roster `a670d510` on handoff/audit-r9-fixplan).

## Friction

fix-review: unclear: three non-blocking review notes, answered rather than fixed. (1) The env_drift integration belt is not modelled by closures. `env_drift.py --claims-only` is `run_always`, so its closure now counts toward `overlap`, but the belt as a whole is latent. (2) A re-run of an old head's run shares the pull request's concurrency group and can cancel the current head's in-progress run. That fails closed (a cancelled required context, re-run once). (3) Who bypasses the queue for an ELIGIBLE merge: §11 now says the orchestrator does.

codeowners_gap: unclear: `instrument-self-tests` has no job `if:` and runs on `pull_request`, yet `--check` lists `.claude/workflows/gh_comment.py` and `.claude/workflows/policy_lint_mutants.mjs` (both run there) as `NO-PR-JOB`, and `merge_fastpath.py` without its CODEOWNERS line lands there too.

## Approval

Awaiting the owner's approving review at the merge head. This changes what the orchestrator must do: `tools/audit/briefs/orchestrator.md` §11 gains the fast path as the one exception to PROC-1's current-main rule. To pay the file's token cap, §10b's tag-citation and `FIXTURE ok` sentences and §11's worktree_gc line are reworded without dropping an obligation. Under the programme mandate (tvofi, 2026-09-30T20:19Z and 2026-10-01T05:03Z) the orchestrator gives that review as tvofi after a merge verdict and green CI; the change itself is the adopted process review (2026-10-01T16:51Z).
