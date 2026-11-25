The #3885 closeout audit (wip-sync/ci-3885-closeout-audit, REPORT.md) measured 48 h of Actions runs to 2026-11-25T10:20Z: 541 runs and 15,092 runner-min, jobs deduplicated across re-run attempts. This change removes the two pieces of waste that a workflow edit can remove on its own.

- U2, `pages.yml`: the build's full-history checkout took 139.8 of its 181.8 runner-min across 171 plan-page dispatches, about 49 s each. The build reads no history: the site lists `git ls-files`, and the release step needs only its own tag. The checkout is now `fetch-depth: 1` with no tags. The release step picks the newest `v*` tag with `git ls-remote --sort=-v:refname` and fetches only that tag at depth 1. Locally that picks the same tag `git tag -l --sort=-v:refname` picks (v10.1.3), and `docs/index.html` is present after checkout. The saving is most of the 139.8 min, but it is an estimate until CI shows the new checkout time.
- U3, `gate-sweep.yml`: `sweep.py` SKIPs every `workflow_run` with no `pull_requests` at its first read, and a main push or merge-queue run never has one. A job-level `if:` now makes that decision before a runner is held. In the window that covers 14 CI push completions (no merge_group runs) at about 0.48 min per sweep, so about 6.7 runner-min per 48 h. The check that no PR-controlled string appears after `jobs:` still holds: the `if:` reads only `github.event.workflow_run.event`.

Refs #3885; leaves #3885 open for the audit's second pass.

## Head

92d719ab7f746bd985b8a139fe169e8dbed9d1bd: e04a759e plus one commit that repairs the `_PG_PLAN` fixture for the review's block.

## Mutation proof

`tests/entities.py` pins both changes, each with a plant the check must catch. Both checks were run alone through an AST extraction, because Home Assistant is not installed locally:
- gate-sweep: removing the `if:` line turns the check red with `want the job-level if ...`. The plant `a runner for a push completion` is caught.
- pages: restoring `fetch-depth: 0` / `fetch-tags: true` turns the check red with `checkout [...] (want fetch-depth 1, no tags)`, and a release step without `ls-remote --tags` / `--depth 1` turns it red too. The plant is caught.

- `_PG_PLAN`, the plan-page check, was run as its whole block, not as single extracted checks: lines 42806-42883 of `tests/entities.py` run verbatim with only their dependencies lifted (`_pg_run`, `_PG_WF`, `_PG_STAGE`, `_PG_GUARD`). Five mutants of the release step's version-order line were each run through the whole block, and the block killed all five: `--sort=-refname` (took v1.9.0), `--sort=v:refname` (took v1.9.0), no `refs/tags/v*` glob (took x9), `tail` for `head` (took v1.9.0), and no tag fetch (took x9, rc 1). The first of them is also in the tree as a null control.
- Every block in `tests/entities.py` that parses either changed workflow was run whole, each section verbatim with its dependencies lifted. No other script parses either file. The pages section (lines 42572-42948): 7/7 checks green at 92d719ab, and 5/6 at e04a759e, where `_PG_PLAN` is the red one. The gate-sweep section with the U2 pin (lines 21590-21700): 2/2 green.

## Null control

At origin/main 6a58ba5c's workflows, both new checks are red: the gate-sweep check reports the missing `if:`, and the pages check reports both defects. With this head's workflows both are green, and the existing gate-sweep plants (PR-controlled strings, trigger, permissions) are still caught.

## Figures

none

## Red checks

- `tests/entities.py` at e04a759e (review/3894, blocked test-red). Its check "the Pages workflow stages the round's plan page before it checks out the newest release" ran the new release step in a scratch repository with no remote. `git ls-remote origin` exited 128 and the step took x9. Repaired at 92d719ab: the fixture is now a bare `origin` holding v1.9.0, v1.10.0 and x9, and the step runs in a `--depth 1 --no-tags` clone of it, as on the runner. The v1.10.0 assertion is unchanged. The whole block is red at e04a759e (`took 'x9' (rc=128)`) and green at 92d719ab. The cheaper detector was running that block before the handoff. The first mutation proof ran only the two new checks, through an AST extraction, because Home Assistant is not installed locally, so it never reached `_PG_PLAN`. The countermeasure is to run every block that reads a changed workflow file, whole. The rehearsal script that does it is outside the tree.

## Forward-carry

- U1, review runs waiting on code runs (prelude): covered by #3888 c0dcc352, whose SOURCE_READERS means a review no longer waits. Carry: dismissed: covered by #3888 c0dcc352
- U4, edit-kind `cancel-superseded`: 20 of 91 edit jobs in the window cancelled 1-2 superseded runs, so the job is not a no-op. Carry: dismissed: measured, it cancels superseded runs in 22% of edit events
- U5, skipping prelude for an unchanged head: as shaped, it leaves a stale-green window. The sound form needs prelude to cancel runs itself. Carry: dismissed: needs a token widening (actions: write on prelude); owner's call
- U6, the PR-only nightly visibility check (`tests.yml`): it is PR-only by design, and the comment in `tests.yml` records why. Carry: dismissed: by design
- U7, small residual steps: 13.3 + 5.3 + 12.0 = 30.6 s in 48 h, under the 5 min bar for a build. Carry: dismissed: measured at 30.6 s per 48 h
- U2, dispatch half (send `pages.yml` only when the page moved): 165 of 165 state-ref pushes in the window changed `PLAN.html` (snapshot time, ETA and charts), so gating the dispatch would remove nothing. Throttling the dispatch instead would conflict with the 11-06 ruling that every sweep updates the plan artifact. Carry: #3885

## Friction

none
