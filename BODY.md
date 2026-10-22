## Unit

U9d, harness and CI readers (R10-CI-LAYOUT-P2, P2b). Code head `handoff/r10-ci-layout-p2-u9d`, one commit on `fef4a1351` (main; contains P2a's `a1633381a`). U0c had not handed off (`git ls-remote origin refs/heads/handoff/r10-ci-layout-p2-u0c` empty), so names come from `tools/ci/gate.py` `REQUIRED`.

`git diff --stat origin/main...HEAD`: 13 files, 424 insertions, 66 deletions (about 330 production lines, the rest self-tests).

Files: `tools/pr/ci_predict.py`, new `tools/pr/local_alerts.py`, `tools/pr/prepr.sh` (`REDS_JQ`, `alert_reds`, `predict_line` body arg, self-test rows), `tools/policy/fixtures/red-ancestry/{green,red}` (check names), `tools/audit/seat/ci_predict_replay.sh`, `failure_logs.sh`, `tools/audit/round4/D11/governance_cost.py`, `dev/audit/harnesses/ci_script_seconds.py`, `superseded_runs.py`, `tools/audit/merge_throughput.py`, `dev/audit/rounds/round4/D11/dora_keys.py`, mutants in `dev/audit/harnesses/r10_seat_selftests_mutants.py`.

## Interface

- `ci_predict.py`: PREDICT lines carry the check names `tests / closures`, `tests / fast (3.14)`, `tests / mutation` (map `JOB`, pinned against `gate.REQUIRED["pr"]` by its self-test); `ledger` stays (no check). New `--body FILE`: carry 6, calls `carry_audit.audit(body, [], carry_audit.load_dests(root))` imported from the checkout, never re-implemented; each unrouted or bad finding prints `PREDICT pr-contract / pr-contract CARRY UNROUTED|BAD ...` and sets rc 1. `--self-test` added.
- `prepr.sh`: `REDS_JQ` excludes `.name != "pr-contract / pr-contract" and .name != "gate"` (N4, both strings). `alert_reds` runs `tools/pr/local_alerts.py` (override `PREPR_LOCAL_ALERTS`, off with `PREPR_NO_ALERTS`), which finds the open PR, its newest `CI code` run at the head, the legs whose `codeql / Analyze (<leg>)` job succeeded, and calls `alert_list.reds` (bound through `alert_list.bind(ghapi.get, repo)`); alert lines join the red names, so the body check asks the body to name each. Unread alerts print a `[code-scanning alerts NOT READ: why]` prefix and never refuse. `predict_line` takes the body as third argument.
- `failure_logs.sh`, `ci_predict_replay.sh`: read `tests / <job>` (replay reads bare names too); log files `tests-closures-<job>.log`.
- `governance_cost.py`: `bare()` strips `<unit> / `; GOV drops `rerun-stale-contract`, `rerun-stale-verdict`, adds `gate-sweep`.
- `ci_script_seconds.py`: `Tests` and `CI` push runs, job via `is_fast` (`fast (3.14)` or `tests / fast (3.14)`).
- `merge_throughput.py`: `--from-runs` repeats (tests.yml and ci.yml series join).
- `dora_keys.py`: `cfr_tests` counts `Tests` and `CI`.
- `superseded_runs.py`: `--layout old|new|both`; runs compared per `run-name` kind via `prelude.parse_title`; `display_title` added to the fetch.

## P2a defect

none found.

## Static map

Not applicable: this unit edits no workflow file, so `unitcheck2.py static` has no callee to compare (rc n/a).

## Controls

- Carry 6 plant and null, `python3 -I tools/pr/ci_predict.py --self-test`: a carry to an open roster group predicted green, to `R10-NO-SUCH-GROUP` red, a finding with no carry red, every `JOB` value in `gate.REQUIRED`; `0 failed`. Through `prepr.sh --self-test` (throwaway clone, `predict_line` with a body): `ok 6d predicts pr-contract's carry refusal for a destination the roster lacks, and refuses (rc=1)` and `ok 6d stays quiet on a body with no finding to carry (null control)`.
- `REDS_JQ`/alerts, `prepr.sh --self-test`: `ok an open code-scanning alert the body does not name is refused`, `ok and the refusal names the alert`, `ok a listing with no alert passes (null control)`, `ok alerts that were not read leave the arm passing, never refusing`; the green fixture now holds a red `gate` and `pr-contract / pr-contract` and still passes (exclusion key). Whole run: 331 passed, 9 failed; main's copy run alongside: 324 passed, same 9 failed (all 6b / recorder-lane rows, "no interpreter that parses the tree", no seat venv in this container).
- `python3 -I tools/pr/local_alerts.py --self-test`: 6 rows (alert listed; dismissed not; no PR, no code run, failed scanning read each NOT READ; run with no succeeded leg lists none).
- Mutants (each reddens its self-test; baseline passes first): `r10_seat_selftests_mutants.py failure_logs-1` KILLED; `merge_throughput-1` KILLED; run by hand on copies (steps for them are owed, see Wiring): `ci_predict-1` (carry rows dropped) 2 failed, `ci_predict-2` (unprefixed name) 1 failed, `local_alerts-1` (no-PR guard) crashes rc 1, `local_alerts-2` (leg conclusion ignored) 1 failed.
- `superseded_runs.py`, both layouts over saved JSON (scratch cache: head `a` run twice, `c` once; `ci` adds a review run at `a`): `--layout old` prints `RESULT tests ... same_sha_dup_heads=1 same_sha_dup_min=10`; `--layout new` prints `RESULT ci ... same_sha_dup_heads=1 same_sha_dup_min=10` (the review run is another kind, so not a duplicate; head `c` with one run counts 0). NULLCONTROL lines all 0. `--selftest`: 13 ok, including a code and a review run at one head = 0 and a single run = 0.
- `governance_cost.py` replay over fixture check runs: old names and `<unit> / ` names both give `governance_seconds_median=90`, `gate_seconds_median=700`, `body_rounds_mean=1`; with `bare()` removed: `0`, `790`, `0`.
- `dora_keys.py` replay (4 push heads, `Tests` and `CI` failing 1 each): `cfr_tests=0.5`; with `TESTS_WORKFLOWS=("Tests",)`: `0.25`.
- `ci_script_seconds.py --selftest`: `is_fast` ok for bare and prefixed, false for `tests / browser`, `gate`. `failure_logs.sh --self-test`: passed=7 failed=0. `merge_throughput.py --self-test`: ok (two listings join to two merges, one to one).
- Gates: `python3 tests/structure.py` PASSED; `throwaway_git.py --check` and `tmp_paths.py --check` 0 refused; scoped gate `MODE: SCOPED -- 2 script(s) run` (`tests/entities.py`, `tests/harness_headers.py`): entities `1 of 2399 ENTITY CHECKS FAILED`, the one failure being the GOV pin ("GOV names only jobs the workflow files define"), which names `gate-sweep`; it clears when `gate-sweep.yml` lands with its job id (see Uncertainties).

## Live checks owed

- Run `local_alerts.py --repo tvofi/heatpump_optimizer --branch <a P2b probe PR head>` once a `ci.yml` code run with CodeQL legs exists: expect the alert lines `pr-contract` lists for that PR, or `NOT READ` with a reason.
- Run `superseded_runs.py --fetch --layout new` once `ci.yml` has PR runs, then `--layout old` over the pre-cut-over window (carry 1: measure `same_sha_dup_heads` before and after).
- Confirm `gate-sweep.yml`'s job id equals `gate-sweep`; confirm check names `codeql / Analyze (<leg>)` and `tests / fast (3.14)` as the live check runs print them.

## Wiring

- `.github/workflows/governance.yml` `instrument-self-tests`: add `python3 -I tools/pr/ci_predict.py --self-test` and `python3 -I tools/pr/local_alerts.py --self-test`; `selftest_wiring.py --check` reads `89 self-testing, 87 wired, 2 unwired` until then. The mutants `ci_predict-1/-2` and `local_alerts-1/-2` run once those steps exist.
- `tests/entities.py` (U9b/U0c): `_PC_EXCLUSION` also pins both strings in `prepr.sh` `REDS_JQ`; the GOV pin needs `gate-sweep.yml`'s job id in GOV.

## Red checks

none: at main's head `fef4a1351` the Hassfest, Validate, Governance, CodeQL, Nightly and merge-main push runs are success; the `Tests` push run was still in progress when read (one GitHub read).
