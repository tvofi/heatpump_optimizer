Fix review: blocked b0ef8f54964a832950dce1ddd02423f3cfb60aa8 mutation-vacuous: M6 len(superseded)==len(bad) to any-superseded survives the new check, so a second genuinely failed lane can be graded green unpinned

bus-nonce: b8f3204a2c9ce3c3e788b2ee3f4426b8

Round 1, first-round adversarial fix review. Reviewed from a detached worktree at b0ef8f54964a832950dce1ddd02423f3cfb60aa8, three-dot against merge base 28482eceeb6b9809e44b12d80fc994282cc21645. The group names no finder's harness, so my harness is the PR's entity check copied verbatim plus reviewer probes, and a replay of the real API runs on the production grader (`ev/ns_check.py`, `ev/replay.py`).

## Block

The production predicate in `verdict` is correct, and the fix is real: the replay of the cited runs flips red to green, and the null controls stay red. But four of the changed grading lines can each be mutated into a version that grades a genuinely red lane green, and the PR's only new check still passes. The check does not pin the property its own name states ("a failed lane is superseded only by a NEWER in-flight run that concluded the same job green").

- M6 `if len(superseded) == len(bad):` to `if superseded:` SURVIVES. Probe B1: `slow` and `mutation-ledger` both failed, the newer run has `slow` green, and the probe reads PASSED. A real `mutation-ledger` failure is hidden.
- M8 `superseded = [j for j in bad if j.get("name") in greens]` to `superseded = list(bad) if greens else []` SURVIVES. Probe B1 again reads PASSED: any green job supersedes any failure, matched by no name.
- M4 `== "success"` to `in OK_CONCLUSIONS` SURVIVES. Probes B2 and B5: when the newer run has `slow` skipped or neutral, the stale failure reads PASSED.
- M2 `> started` to `>= started` SURVIVES. Probe B3: an in-flight run with the same `created_at` as the failed run supersedes it.

The cure is a check, not a code change: add arms for two failed jobs with one superseded, a newer `skipped` job, and an equal `created_at`, all expected FAILED. Each arm kills one mutant in `ev/mutants.txt`. The fixer re-runs the mutation proof on every changed grading line, not only on the one predicate the body mutated.

## Findings

- Surviving mutants M2, M4, M6 and M8 on the changed grading lines of `tests/nightly_status.py` `verdict` (claim: each changed line is mutation-proof). Evidence: `ev/mutants.txt`. Harness: `ev/ns_check.py` arms A, which are the PR's check verbatim. Metric: PR-CHECK rc. Perturbation: each mutant, with rc 0 (survived) while probes B1, B2, B3 and B5 flip to PASSED. The harness moves under its own perturbation: M1, M3, M5 and M7 each give rc 1. Carry: R10-HOTFIX-NIGHTLY-STATUS
- M10 SURVIVES: in `main`, `fly_jobs = _jobs(...)` changed to `None and _jobs(...)`. No test reaches the `main()` wiring that fetches the in-flight run's jobs. With M10 the production check grades red exactly as at the base, and every test stays green. The fix's effect on the real check is therefore unpinned. A check is owed that drives `main` (or `collect` plus the fetch) with a stubbed `_jobs` and asserts that the in-flight run's jobs reach `verdict`. Harness: `ev/mutants.txt`, line M10. Carry: R10-HOTFIX-NIGHTLY-STATUS
- The figure "this check stayed red on every pull request for hours" (code comment in `verdict`) does not re-derive. At the API, 42235215315 concluded at 18:06:31Z and 42242870295 concluded green at 19:17:32Z. The window in which the newest concluded run was the failed one is about 71 minutes. Evidence: `ev/runs-api.txt`. Correct the comment to the measured window. Carry: R10-HOTFIX-NIGHTLY-STATUS
- `## Red checks` says "none", but at this head `gate` (check run 128206881487) concluded failure at 23:05:41Z with "FAIL run(s) [42309258015] at this head are still being judged; their gate decides". The packet refuses with `red-unanswered` and `required-red`. The body owes an answer for every concluded red, including this ordering red. Carry: R10-HOTFIX-NIGHTLY-STATUS

## Evidence

- RESULT: setup: `cloud-setup.sh --check` printed OK.
- RESULT: packet: rendered with refusals `red-unanswered` and `required-red` (gate). Copy in `ev/review-packet.md`.
- RESULT: merge: `git merge-tree --write-tree origin/main b0ef8f54` gives rc 0 (`ev/merge-tree.txt`).
- RESULT: diff scope (three-dot): 3 files, `dev/programme/delivery/3263.md` (+1), `tests/entities.py` (+38), `tests/nightly_status.py` (+35/-1). VERSION, manifest, RELEASE_NOTES.md, `tests/golden`, `*_budgets.json` and `.github` are untouched (empty diff). `nightly.yml` is untouched, so the nightly's strength on production code is not weakened.
- RESULT: the delivery row is in the diff. `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, so the new file does not force FULL. `tests/structure.py` prints STRUCTURE RATCHET PASSED.
- RESULT: the body's line "three-dot 2 files, +73/-1" describes the authored head 99556a1e. At this head the diff is 3 files, +74/-1, with the row commit that `## Head` explains. `## Head` is current.
- RESULT: the cited runs, re-read from the API (`ev/runs-api.txt`):
  - 42235215315 (dispatch, main, 14:35:02Z): failure; `slow` failure at 15:11:00Z; run concluded at 18:06:31Z.
  - 42242870295 (dispatch, 15:25:13Z): `slow` success at 15:52:47Z; run success at 19:17:32Z.
  - 42247578523 (dispatch, 15:55:42Z): `slow` success at 16:24:19Z; run success at 19:34:05Z.
  - 41555367389, 41749544997 and 41943946464 (schedule): each failure on `slow`.
  - 42139479636 (schedule, 11-06): success.
  - The body's cause holds: `pick_runs` takes the newest completed run as `concluded`, and 42235215315 read failed while newer runs had already passed `slow`.
- RESULT: production-grader replay (`ev/replay.txt`):
  - At 18:30Z and 19:00Z: FAILED exit 1 at the base, PASSED exit 0 at the head (concluded 42235215315, in_flight 42247578523).
  - Null control at 2026-11-04T01:00Z, with the newer run's `slow` pending: FAILED at both.
  - Null control at 06:00Z, with the newer run's `slow` failed: FAILED at both.
- RESULT: the PR check at the base cannot pass: `ev/check-base.txt` gives rc 1 (no `in_flight_jobs` parameter). At the head: PR-CHECK PASS, PROBES PASS (`ev/check-head.txt`).
- RESULT: mutants (`ev/mutants.txt`):
  - Killed: M1, M3, M5, M7.
  - Survived: M2, M4, M6, M8, M10.
  - M9, which drops the `in_flight_jobs and` guard, is equivalent: an empty list gives `len(superseded)` 0, which is never equal to `len(bad)` of at least 1.
- RESULT: the full `tests/entities.py` could not be run locally. venv-ci lacks homeassistant, and venv-ha plus the CI requirements fails on `FakeConfig.config_dir`. The mutants were run against the PR's check copied verbatim. No other check in `tests/entities.py` passes `in_flight_jobs` (grep), so no other check can kill them. The body's figure of 2638 entity checks is not re-derived here.
- RESULT: CI: `merge_train.py classify` printed `RED b0ef8f54964a832950dce1ddd02423f3cfb60aa8 pending: none red: gate` with rc 1, twice (`ev/classify-1.txt`, `ev/classify-2.txt`). At 23:14Z tests run 42309258015 was still in progress (closures, fast, coverage), as was `governance / instrument-self-tests`, the owner's standing line (#3245). `tests / nightly-status` is success at this head.
