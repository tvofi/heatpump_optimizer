R11-CI-3885-QUEUE lever L1 (#3885): cancel a superseded `synchronize` run when the newer one is created. Design: `design/r11-ci-3885-queue` at 43ff5ae6c1, §3 L1, approved in `design-verdict/r11-ci-3885-queue` adbd80a468.

A `pull_request` `synchronize` run on its first attempt, sent by anyone but `github-actions[bot]`, now joins `CI-pr-<number>` with `cancel-in-progress` true. The older such run is then cancelled at creation, pending or in progress. Before, it waited until the `cancel-superseded` job got its own runner.
- Every other run keeps its run-id group: opened, reopened, edited, labeled, review, dispatch, merge-queue, any re-run (attempt 2+), and any bot-sent run. `cancel_superseded.py` remains the fallback for those.
- Push runs keep their groups byte-identical. The `CI-main` arm of the `group:` expression is unchanged, and `cancel-in-progress` is false for every push.
- The bot exemption is the same as `cancel_superseded.py` `BOT = "github-actions[bot]"`, read from `github.event.sender.login`, as the `cancel-superseded` job's own `if:` reads it.
- The ci.yml comment that said "Supersession is cancel-superseded's alone" is rewritten (carry l1-comment). The `tests/entities.py` umbrella pin is rewritten with it: it used to refuse any `cancel-in-progress` that was not false. It now renders `group` and `cancel-in-progress` for every modelled event × attempt (1, 2) × sender (`hpo-author[bot]`, `tvofi`, `github-actions[bot]`). It wants `CI-main` for a push's first attempt, `CI-pr-7` plus cancel for a non-bot synchronize's first attempt, and `CI-99` with no cancel everywhere else.
- `_ci_ctx` now models `github.event.sender.login` (the actor by default).
- The design's harness `dev/audit/harnesses/ci3885_queue.py` lands here, as the design note says it lands with the first PR. It is classified, like `ci3885_light.py`, as an inert read of `tests/harness_headers.py` in `tests/closures.json`. Its usage line named a `--json` flag the parser does not have (`report` always prints JSON), so the line now names the real `--keep-copies`.

**Handoff.** The code head went to `handoff/r11-ci-3885-queue-l1` and this body to `handoff-body/r11-ci-3885-queue-l1` (`body_push.sh`, fixer.md step 6). No pull request was opened.

**Merge order.** This merges after `handoff/r11-ci-3885-ci5-drop`. Both edit the ci.yml `concurrency` block and the entities umbrella pin, and `git merge-tree` reports content conflicts in `.github/workflows/ci.yml` and `tests/entities.py`. Resolve the conflict by keeping both changes. Take ci5-drop's push arm, which removes `CI-main`, and keep this PR's `CI-pr-<number>` arm and its `cancel-in-progress` expression. In the pin, drop the `CI-main` want and its three CI-main plants, as ci5-drop does, and keep the per-sender rows and the six L1 plants. Until that merge, this branch keeps the `CI-main` row (verdict carry l1-ci-main-order).

## Head

Measured at code head `7a3c37dafe62217a9d8fe6400e171cc194aeac7d`. Base `origin/main` d9100de781. `origin/main` was dbdc520e86 at 2026-11-26T02:14Z, and `git merge-tree --write-tree origin/main HEAD` reported no conflict.

## Mutation proof

The pin is a reader with planted mutants, and each plant must be named as a defect (`_CI_PLANT_MISSED` must be empty). L1 adds six plants to `_CI_PLANTS`:
- `the PR group on every pull_request action`: `synchronize` is dropped from both arms, which is the design's named mutant.
- `the PR group's cancel on every pull_request action`
- `PR re-runs in the PR group`
- `bot-sent pushes in the PR group`
- `the PR group cancelling nothing`
- `no PR group`

`the main group cancelling in progress` is re-cut to set the `cancel-in-progress:` line to `true`.

At the head, `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ok   the CI umbrella: ...`. Every plant was named, so the check would print FAIL with `plants the reader missed=[...]` had any been missed.

Failing first: the new pin ran against the unchanged ci.yml and printed `FAIL the CI umbrella`. It reported 4 defects: synchronize attempt 1, for senders `hpo-author[bot]` and `tvofi`, rendered `'CI-99', want 'CI-pr-7'`, and `cancel-in-progress reads False, want True`. It also named all six new plants as missed, since none of their target text existed in the old file.

No new `.py` lines are added outside `tests/` and `dev/`, so `prepr.sh` draws no production mutants.

## Null control

The new pin on the unmodified ci.yml fails with the defects listed above. The new pin on the new ci.yml passes, with no other row changed: every non-synchronize event, every attempt-2 row and every bot-sent row still renders `CI-99` with no cancel, and push attempt 1 still renders `CI-main` with no cancel.

`tests/entities.py` has one other red at both ends: `a measured script's late-writing descendant is waited for, not recorded as nodata`. That is a timing check, and it failed the same way on the run before ci.yml changed. In one of the two runs, the gate-lease timing check also failed.

The harness null arm is `supersede_null_same_head_code` (same-head code twins, never superseded). It reads 1 run / 1 runner-min on 2026-11-25 and 0 on the quiet null day 2026-11-24, which matches the design's 0-1 bound.

## Figures

- supersede on 2026-11-25 (busy day, pre-merge baseline): 66 runs, 664 runner-min after a newer head's run existed, 124 jobs started after it. `python3 dev/audit/harnesses/ci3885_queue.py report 2026-11-25 --cache DIR` after `fetch 2026-11-25 --cache DIR`.
- supersede on 2026-11-24 (null day): 1 run, 1 runner-min, 0 jobs. `python3 dev/audit/harnesses/ci3885_queue.py report 2026-11-24 --cache DIR`.

These are pre-merge. The post-merge reading, the supersede arm on the first busy day after merge, should drop to about 0 for synchronize pairs. That reading is the design note's own post-merge test (`design/r11-ci-3885-queue` §3 L1, Test).

## Red checks

none

## Forward-carry

none

## Friction

none
