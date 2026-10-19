R10-FOLLOWER-DEBOUNCE: one effective run of the stale-contract follower per PR head. tvofi ordered it on 2026-10-19, ahead of R10-CI-LAYOUT.

`.github/workflows/pr-contract-rerun.yml` starts on every completion of the 8 workflows it watches. Each red completion ran `tools/pr/contract_rerun.py`, and every stale contract it found was re-run again. That happened once per red at a head, on the same Actions token quota that validate-hacs, arch-score and env-matrix ran out of.

What changes:

- A top-level `concurrency:` group, `pr-contract-rerun-${{ github.event.workflow_run.head_sha }}`, with `cancel-in-progress: true`. The newest completion at a head cancels every older follower of that head.
- A first step (`id: last`) runs before any checkout. It makes one API call, `repos/$REPO/actions/runs?head_sha=$HEAD_SHA`. While another watched run at the head is `queued`, `in_progress`, `requested` or `pending`, it prints `DEFER` and the job ends, because that run's own completion starts the follower again. `waiting` (an environment approval) is not counted, so a follower can never wait on a run that may never finish.
- To keep the freshness guarantee, the job now runs on every conclusion, not only on a red one. The last completion at a head may be green after an earlier red deferred to it. If the old red-only `if:` stayed, both the deferral and the concurrency group would drop that red. The concurrency group is the worse of the two: a skipped green run still enters the group and cancels an in-progress red follower.
- The program gets the newest red watched run at the head (`RUN_ID: ${{ steps.last.outputs.red }}`). Its finish time is the latest one a contract must start after, so `contract_rerun.py` and its stale rule are unchanged. With no red at the head, nothing is re-run.

Why the final completion still re-runs: the last watched run at a head to complete starts the newest follower in the group, so nothing later cancels it. When that follower lists the runs, every other watched run there has already completed, so it does not defer. It hands on the newest red, and `stale_contract` re-runs the contract if that contract started before the red finished. The re-run reads every check run live, so it also lists any older red whose follower was cancelled or deferred.

Risk:

- A cancelled run in a race is intended. A follower cancelled mid-run (including one inside `contract_rerun.py`'s 20-second wait loop) loses nothing, because the follower that cancelled it re-reads the head and either defers to a later completion or does the same work.
- One gap remains. The runs list could still show a sibling as unfinished after that sibling's completion event has fired (API lag). If that sibling's own follower had already run and deferred, the last follower would defer too, and that head's contract would not be re-run. No instrument here can measure that lag, and the effect is the pre-D13-s1-03 state for that one head, not a wrong verdict. R10-CI-LAYOUT inherits it (Forward-carry).

Cost, which is not a strict reduction:

- Program runs (and contract re-runs) per head drop from up to R, one per red, to at most 1.
- Every completion now starts a job that makes one list call. Before, a green completion was a skipped job with no calls.
- So in the worst case per head, calls go from R x 9 to 8 + 9: a saving at 2 or more reds per head, a cost at 0 or 1. The model and its rule are in `## Figures`.
- The newest 100 follower runs (2026-10-19T15:08Z) held 69 `skipped` and 31 that ran the program. Those 69 skipped runs are the ones that now cost a call each.
- If the quota is drained by heads with 0 or 1 reds, this change does not relieve it. R10-CI-LAYOUT should measure the per-head red count before keeping the follower (Forward-carry).

`tests/entities.py`'s follower pin changes accordingly:

- It refuses an `if:` on the job, a group not keyed on the head, a first step that is not the deferral or whose WATCHED copy differs from `on.workflow_run.workflows`, and any later step not gated on `steps.last.outputs.red` or not handed the red.
- A new null control applies each of those mutations to the file and requires a refusal for each.

`dev/audit/harnesses/follower_debounce.py` lifts the step's own script out of the workflow and drives it against fixture runs lists through a stub `gh`.

No issues close here.

## Head

f210e78b59ffa9b15993cb80eaea4dd496c2d3a8, measured against merge base 64b0ae6901b7e7484a1d46d3402b2aaf88da0d69 (origin/main at 2026-10-19T15:05Z).

## Mutation proof

Each mutant was applied to the committed tree and then restored, and a `cmp` against the head confirmed every mutant differs from it. The mutants ran at ec031e461ec2, whose tree differs from the head only by `tests/closures.json`'s INERT READS entry for the new harness.

- M1, the deferral predicate made unreachable (`"$busy" -gt 0` to `-gt 999`). `python3 dev/audit/harnesses/follower_debounce.py <mutant>` printed `FAIL another watched run in progress defers` and `9 cases, 1 failed`.
- M2, the oldest red handed on instead of the newest (`| last` to `| first`). It printed `FAIL the newest red is the one handed on` and `9 cases, 1 failed`.
- M3, the trigger no longer excluded from the busy set (`select(.id != $me and ` to `select(`). It printed `FAIL the trigger listed stale as in progress does not defer itself` and `9 cases, 1 failed`.
- M4, the old red-only `if:` put back on the job. `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `FAIL a red that lands after pr-contract ran re-runs it: ... (D13-s1-03, R10-FOLLOWER-DEBOUNCE)`. Its defect list names `if:`.

## Null control

- `python3 dev/audit/harnesses/follower_debounce.py <origin/main's pr-contract-rerun.yml>` prints `REFUSED: first step ... is None, not the deferral`, because the base file has no deferral step to drive.
- The harness's own null control, `no red at the head re-runs nothing (null control)`, passes at the head: an all-green head hands nothing on.
- In `tests/entities.py`, `and the follower with a per-run group, a red-only job, a watched copy missing a workflow, or the trigger's id handed on, is refused (null control)` passes at the head.

## Figures

- `python3 dev/audit/harnesses/follower_debounce.py` at the head printed `follower_debounce: 9 cases, 0 failed`. The cases include `a head with one watched run still re-runs` and `a green last completion after a deferred red hands that red on`.
- The per-head call model is printed by the same harness's `model()`. Its rule: before, each red completion costs GET + list + POST (3) plus one pr-contract re-run of at least 6 calls, by pr-contract.yml's own `gh api` lines; after, each completion costs 1 list call and the last one adds 3 + 6 when the head has a red. It printed program runs `8 -> 1` and calls `<= 72 -> <= 17` at N=8 R=8, and calls `<= 0 -> <= 8` at N=8 R=0.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head printed `ALL 2351 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at the head printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` predicted one closures red (an INERT READS entry for the new harness). `--apply-inert` wrote that entry and it is committed; a re-run printed `no closures or fast red predicted`.
- `bash tools/pr/prepr.sh <this body>` exited 0 at the head.
- The scope came from `python3 tests/closure.py select --diff 64b0ae6901b7e7484a1d46d3402b2aaf88da0d69`, which printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/harness_headers.py).
- The live run tally came from `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/pr-contract-rerun.yml/runs?per_page=100"`, grouped by `.conclusion`. This is a sliding window, stamped 2026-10-19T15:08Z.
- actionlint is not used by this repository: `git grep -ln actionlint -- .github tools tests` returns nothing.

## Red checks

nightly-status is main's: run 39218718759, record-autofix 403. It does not come from this diff (no file the nightly reads changes here), and its root cause is the token quota this PR addresses.

## Forward-carry

- R10-CI-LAYOUT replaces this follower. It must keep the debounce semantics or drop the follower, and it must measure the per-head red count before keeping it, since at 0 or 1 reds per head this design costs more calls than the old one.
- R10-CI-LAYOUT also inherits the API-lag gap named under Risk.
- Destination: `.github/workflows/pr-contract-rerun.yml`. Carry: R10-CI-LAYOUT (roster d1707a459)

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
