# CI waste audit before #3885 closes (first pass)

- Window: the 48 h from 2026-11-23T10:20Z to about 10:40Z on 2026-11-25. It covers 541 runs on every event. 530 of them had completed, and their jobs are measured.
- Workflows were read at origin/main 6a58ba5c.
- Source: the Actions REST API, one jobs listing per run with `filter=all`.
- Runner-minutes are the sum of each job's `completed_at - started_at`, deduplicated by (run, job name, start, end). A re-run attempt lists copies of the jobs it did not re-run, which would otherwise double-count 597 jobs.
- Total measured: 15,092 runner-minutes over 2,260 job executions.
- Instruments: `/Users/timmalmstrom/hpo-orch/r10s6/r11/proto/ci-audit/`, containing fetch_runs.py, fetch_one.sh, analyse.py, runs.json, jobs/*.json, analysis.txt and reruns.txt.

## Uncovered findings (no in-flight #3885 fix covers them)

| # | class | workflow / job / step | runner-min (48 h) | count | minimal fix |
|---|---|---|---|---|---|
| U1 | 1 | ci.yml `prelude`, step `Derive kind, PR, base, scope and legs`, on `pull_request_review` (the `wait_sources` poll) | 79.9 | 13 review runs; 3 held over 2 min account for 75.1 (max 27.6) | #3885's own ask: re-evaluate the review verdict when the source run completes (a `workflow_run` or the gate-sweep), not inside a held prelude. Interim: cap the in-runner wait at about 2 min and leave the verdict to gate-sweep. |
| U2 | 3 | pages.yml `pages-build` + `pages-deploy`, workflow_dispatch from `beat_jobs.py` plan-beat (`gh workflow run pages.yml` on every state-ref push) | 211.9 (201.2 on an already-deployed main sha) | 171 dispatches, 162 at a sha already published | Dispatch only when the page hash moved: plan-beat already computes `moved`, so gate the `gh workflow run` on it. In pages-build, a shallow and sparse checkout (139.8 of the 181.8 build minutes are `actions/checkout`). |
| U3 | 2 | gate-sweep.yml `sweep` (workflow_run on every CI completion) | 85.9 | 179 runs; a 24-run log sample: 14 SKIP + 7 `SWEEP-DONE reruns=0` = 87.5% did nothing (about 75 min) | Job-level `if:` on the event: skip when `github.event.workflow_run.pull_requests` is empty and the event is not a PR, which covers the 5/24 "no pull request / not live head" SKIPs without a runner. Replace the full checkout (22.6 min) with a sparse `tools/ci` checkout. |
| U4 | 2 | ci.yml `cancel-superseded` on `pull_request` `edited` (body edits) | 24.6 | 43 edit runs | A body edit cannot supersede a head. Add `&& github.event.action != 'edited'` to its `if:`. |
| U5 | 3 | ci.yml `refresh` (re-runs stale green gates), plus the gate re-runs it and gate-sweep cause | refresh 109.7 + gate re-run attempts 53.9 = 163.6 | 98 refresh jobs (code 42, edit 43, review 13); 58 bot re-run attempts | Fold `refresh` into gate-sweep, which already re-judges at completion: one re-judging path, not two per event. |
| U6 | 5 | tests.yml `tests / nightly-status` on pull requests | 9.5 | 37 | It reads the nightly's status, which no PR diff reaches. Run it on push and schedule only. Not required, so the gate does not change. |
| U7 | 1 (lead) | merge-main.yml step `Merge main where only a driver file conflicts`: the held-run approval loop sleeps 5 s up to 60 s per pushed branch | at most 37.7 (the whole step) | 14 | The sleep share is not separable from the API data, so this is a lead. Fix: approve from the held run's own `workflow_run`/`action_required` event, not by polling. |

## Totals per class (measured, 48 h)

| class | measured waste | of which uncovered |
|---|---|---|
| 1 held while waiting | 82.3 (U1 79.9; pr-contract `Wait for code scanning` 2.4) + lead U7 at most 37.7 | 79.9 + lead |
| 2 runner for a no-op | about 75 (gate-sweep no-ops) + 24.6 (U4) + 4.5 (8 prelude jobs with every work step skipped) = about 104 | about 100 |
| 3 duplicate/superseded | 201.2 (Pages) + 163.6 (re-judging) + 86.4 (superseded-head tails after a newer head, 17 runs, 15 then cancelled) = 451.2 | 364.8 (U2, U5) |
| 4 needs chains | 0 measured: `pr-contract` reads its needs' check results ("Last, so its red list is final") and `gate` reads `pr-contract`; a `needs:` wait holds no runner | 0 |
| 5 diff cannot reach | 1,763.6: five completed FULL push runs on non-production diffs (3210fcd7, 5594a34a, 7f7e0511, 8531d607, 0f63320c) | 9.5 (U6) |

## Covered by in-flight or landed #3885 fixes

- **#3888 (landed 6a58ba5c), light grading for non-production diffs:** covers class 5's 1,763.6 min. That is 73% of the 2,415.7 push-run minutes: 8 non-production pushes, 5 of which completed FULL at 281-400 min each.
- **stress.py off PRs (handoff/ci-3885-scope-long-scripts):** inside `tests / fast (3.14)` on PRs, 37 jobs and 1,236.6 min. The fix's own figure is 928.7 s per PR; it is not re-measured here.
- **Per-case selection (design/r11-ci-case-select 25fa1f76):** the long PR lanes: `tests / closures` 1,184.8, `tests / coverage` 1,078.0, `tests / mutation` 1,014.9, `governance / instrument-self-tests` 940.0, `tests / replay` 447.3, `tests / arch-instrument` 386.9, `governance / env-matrix` 333.2.
- **Duplicate held-run dispatch (fix/ci-3885-dup-dispatch, not on origin yet):** the lead is the double approval path. `Approve the runs the push left holding` runs in mutation-autofix (7) and closures-autofix (2), and merge-main's approval loop runs as well. No double run was measured in the window: every held run approved once ran once.

## Measured and not waste (recorded so the next pass does not re-open them)

- **Re-run attempts total 3,080 min:**
  - hpo-runs[bot]: 11 full re-runs, 2,914.8 min. These are `cancel_superseded.py`'s priority re-runs. Attempt 1 was cancelled while queued (0 runner-min), and all 13 attempts were at the PR's live head when re-run, so this is the only grading those heads got.
  - tvofi: 7 attempts, 111.4 min. The self-test cap re-runs, which #3887 retired.
  - github-actions[bot]: 58 attempts, 53.9 min (U5).
- **Body edits (`CI edit`, 43 runs, 298 min):** `arch-score` and `budget-raise-gate` read the body (arch-score.yml lines 4-9), so an edit reaches them. Only U4 and U5 are waste there.
- **Main push concurrency (`CI-main`, `cancel-in-progress: false`):** the push runs that show 0 min were replaced while pending, so they held no runner.

## Second pass

Re-run after the last #3885 fix lands:

    cd /Users/timmalmstrom/hpo-orch/r10s6/r11/proto/ci-audit && python3 fetch_runs.py runs && xargs -P 4 -n 1 ./fetch_one.sh < <(python3 -c "import json;[print(r['id']) for r in json.load(open('runs.json'))['runs'] if r['status']=='completed']") && python3 analyse.py

Delete jobs/ first for a fresh window.
