R10-FLY-ROWONLY-BASE. `row_only_checks` in `tools/pr/app_push.sh` ran `policy_lint.mjs --pr-body ... --head <sha>` without `--base`. On a pull request whose diff touches a `*_budgets.json`, which every ratchet PR's does, the contract refused the body with "the diff touches tests/structure_budgets.json, and no `--base` and `--head` name it ... was not read". So `update_pr.sh <branch> - <body>` could never add a delivery row to a ratchet PR. That happened to #2913 (head `bd93599a58dacf2edf7a08decc41a12aefcd4d5d`) and #2912 on 2026-10-28.

The fix passes `--base "$base"`. `$base` is the `git merge-base origin/main HEAD` the function already derives for its path lists, which is how `prepr.sh` derives `BASE` and hands it to `body_check` (`args+=(--base "$BASE")`). It is the same base, not a second derivation. One production line changed, plus one comment sentence.

The self-test adds a real-contract arm. It extracts the production `row_only_checks` (the way the existing real-git block extracts `row_only_verdict`) and drives it on a throwaway repo. That repo carries `tools/policy/`, `tests/layout.py` and `tests/structure_budgets.json`, and its branch moves `max_cc`. Nothing new is wired in: `app_push.sh --self-test` already runs in CI. `app_push.sh` is code-owned, so this needs tvofi's review.

## Head

`92fc713e87523d0acc284b85e5a9d01749b68b4a`

## Mutation proof

Mutant: drop ` --base "$base"` from the `node "$lint" --pr-body` line in `row_only_checks` (this is the base's line). `bash tools/pr/app_push.sh --self-test` then reports `201 checks, 2 failed`:

- `FAIL real contract: a row-only push onto a pull request that lowers a budget cap passes (it was refused as "was not read": no --base) (got 'rc=11', want 'rc=00')`
- `FAIL null control: one that raises the cap is still refused, as a raise owing \`## Raise justification\` (got 'rc=101', want 'rc=110')`

The same two checks fail at the base before the fix, because the test was written first. With the fix restored the run reports `201 checks, 0 failed`.

## Null control

The raised-cap case (`max_cc` +1, no `## Raise justification`) is still refused on the row-only path, and with the fix it is refused *as a raise*: `budget_raise_gate.py refuses this body` appears once and `was not read` does not appear. A stricter-looking refusal therefore cannot pass as the fix. The lowered-cap case is the positive arm. Before the fix it fails on `was not read`; with the fix it passes.

## Figures

- `app_push self-test: 201 checks, 0 failed` at the head and `201 checks, 2 failed` under the mutant. Command: `bash tools/pr/app_push.sh --self-test`.
- The instance at both ends, #2913's head `bd93599a58dacf2edf7a08decc41a12aefcd4d5d` (merge base `eab04d0ebf8c45667099b668ab0d8bf976d5f99a`; its diff touches `tests/structure_budgets.json`). This drove the extracted `row_only_checks` from origin/main's `app_push.sh` and from this head's, in a detached worktree at that SHA, with `tools/policy/fixtures/policy-rot/prepr/good.md` as the body and its `## Head` set to that SHA. At the base the contract refused once on `was not read`. At this head it read `PR-BODY: 0 error(s)`. In both runs rc stayed 1 because of `carry_audit.py` on the fixture body's three unrouted Forward-carry/Friction items. That is the fixture's content, not this path, and the real PR body is what routes them.
- Class seams. The rule: `grep -rn -- "--pr-body" tools/ .github/`, keeping each caller that hands `policy_lint.mjs` a `--paths-file`. The dispositions:
  - `prepr.sh` `body_check` passes `--base "$BASE"`: already guarded.
  - `pr-contract.yml` passes `--base "$PR_BASE"`: already guarded.
  - `body_patch.sh` passes `--base "$base"`: already guarded.
  - `app_push.sh` `row_only_checks`: closed in this diff.
  - `record_row.py`'s self-test passes fixed fixture paths, three delivery rows and no `*_budgets.json`, so it reads no budget path. Not a seam.
  - The `--pr-body` calls in `review_packet.py`, the `hnamed` helper, the `prepr.sh`/`push.sh` self-tests and `figure_lint.mjs` pass no `--paths-file`. Not seams.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `tests/run.sh` run_always lines, `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh`. `tests/layout.py` passes at the head. A first draft of the new arm quoted a retired brief path, the layout guard refused it, and the arm now addresses the `## Forward-carry` section instead. `tests/harness_headers.py` fails the same way at origin/main `eab04d0e`, on `ModuleNotFoundError: No module named 'voluptuous'` in this seat's python. That is this seat's environment, not this diff, so it is left to CI.
- `bash tools/pr/prepr.sh <body>` at this head passed every step but one, `closures`. It printed `REFUSE closures no interpreter that parses the tree was found (tried the seat venv ... and the ambient python3)`. `tools/audit/seat/seat_venv.sh` exits 2 here on `No download found for request: cpython-3.14.7-linux-x86_64-gnu`. That is this seat's environment, reported and not worked around. `CI PREDICT` printed `no closures, fast, wave-script or instrument red predicted against eab04d0ebf8c`, and the diff is the one already-classified file `tools/pr/app_push.sh`.

## Red checks

none

## Forward-carry

none

## Friction

none
