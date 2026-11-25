Fix review: blocked e04a759e943b5fcf01dfd39487d2454c47dd927b test-red: the diff turns the existing tests/entities.py check "the Pages workflow stages the round's plan page before it checks out the newest release" red: its scratch repository has no origin, so the new git ls-remote origin exits 128

bus-nonce: cb5d187ea7564332a3aabbcda897a3db

## Block

- The release step in `pages.yml` now reads its tag with `git ls-remote ... origin`. The existing check `_pg_plan_defects` (`tests/entities.py`, the `_PG_PLAN` block near line 42806 at this head) runs that step's own text under `bash -eo pipefail` in a scratch repository. The repository holds tags v1.9.0, v1.10.0 and x9 and has **no remote**. At this head the step exits 128 (`fatal: 'origin' does not appear to be a git repository`), and the check reports `the release checkout took 'x9' (rc=128), not v1.10.0`. At base bb6377b4 it reports `[]`. The red is caused by this diff, so it is not covered by the expedite's own-CI waiver. The mutation proof ran only the two new checks through an AST extraction, and missed it.
- Repair: make the scratch fixture match the new step, without loosening the version-order assertion. Give the scratch repository an `origin`: a bare clone holding the three tags, with the working repository a shallow `--no-tags` clone of it, as the runner's checkout now is. Keep asserting v1.10.0 over v1.9.0 and x9. Under that fixture the new step passes (rc 0, `docs from v1.10.0`) in my own reproduction. The workflow change itself is sound.

## Evidence

- Head reviewed: e04a759e943b5fcf01dfd39487d2454c47dd927b (ev/HEAD.txt). `git merge-tree --write-tree origin/main <head>` reports a clean merge with no conflict (ev/merge-tree.txt).
- I ran `_pg_plan_defects` alone at base and at head by AST extraction (ev/ast_run.py). The base gives `[]`. The head gives `["the release checkout took 'x9' (rc=128), not v1.10.0"]`. A direct reproduction of the same run (ev/repro.py) gives base PASS and head FAIL. With a bare origin and a depth-1 clone, the head step picks v1.10.0 at rc 0. All of it is in ev/pg_plan_repro.txt.
- The full `tests/entities.py` could not run in this container: the HA venv lacks paho. So the isolated extraction above is the evidence.
- U3 (`gate-sweep.yml` job-level `if:`): no check is lost. `ci.yml` pushes run on main alone. `sweep.py` `run()` returns SKIP at its first read whenever `pull_requests` is empty, which it always is for push and merge_group runs. `pull_request`, `pull_request_review` and `workflow_dispatch` completions still get a runner. The `if:` reads only `workflow_run.event`, which carries no PR-controlled string. The new plant is caught.
- U2 checkout depth: the rest of the build reads no history. The site stages from `git ls-files`. `build_docs.mjs` makes no git calls. `plan_public.py stage` reads `for-each-ref` over refs the stage step fetches itself. The tag-push path checks out the tag at depth 1. The unauthenticated `ls-remote` and `fetch` against origin match the unchanged plan-stage step's existing `git fetch origin`, which runs with the same `persist-credentials: false`.
- CI: `merge_train.py classify` printed `WAIT e04a759e943b5fcf01dfd39487d2454c47dd927b pending: gate red: none`. CI was not awaited, because the block rests on code.
- Body figures (139.8/181.8 min, 171 dispatches, 179 sweeps, 85.9 min, 6.7 min): not re-derived. They come from the audit's Actions window, which is not reproducible from the tree, and none of them is load-bearing for the change.

## Findings

none
