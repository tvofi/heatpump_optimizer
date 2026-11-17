Part of #3616 (phase 1 of the owner's three; the issue stays open for phases 2 and 3)

R11-OUTSIDE-ROOMS-P1. Its production code, tests, closures, ledger pins, docs and claim reached `main` through #3678 (R11-OUTSIDE-ROOMS-P2, merge `30991a6b0d`), which was built on this branch: `git log --oneline origin/main` holds `822ba6fcf2` through `71609de657`, this branch's commits. After merging `origin/main` at `8f39313a44a4baec18b239ba925f6e164eb26bd2`, the diff against main (`git diff --stat origin/main HEAD`) is two files:

- `tests/features.py`, +12: one check in the `#3616 R11-OUTSIDE-ROOMS-P1` section, `a degF sensor room converts by its own unit to degC (68 degF reads 20.0, no problem); null control, a degC sensor at 20.0 reads 20.0` (review round 1's survivor M6, `read_room`'s sensor branch). Main does not hold it.
- `dev/programme/delivery/3667.md`, the CI-written delivery row.

No production line differs from main: `git diff origin/main HEAD -- custom_components/` prints nothing. With #3678 merged, everything this PR delivers is on main except the degF check; whether that check lands here or the PR closes is the orchestrator's decision, and this diff does not make it.

The PR was `DIRTY` at `064b60f7b2`. Merge resolution (commit `8fbbe09acf`):
- `tests/mutation_ledger/killed_by/rooms.py/published.GUARD_OFF.cdba2f29.json` and `readings_of.RETURN_DEL.627b05e8.json` (add/add): main's side. Main re-recorded both after #3678; for `readings_of`, the killer is `tests/config_flow_steps.py` on main and `tests/features.py` on this branch.
- `tests/deployment_shape.py` (the pair-count history note): main's side. It records the same 167 pairs this branch's text did, with both rooms phases merged. `tests/entities.py` checks the note against the tree (below).
- `tests/features.py`: both sides added a staleness-clamp check at the same place. Main's `the staleness scale is clamped at both ends ...` (`_scaled` at 0.0, 0.5, 10.0 and 1e9 against `STALENESS_SCALE_MIN`/`STALENESS_SCALE_MAX`) is kept. This branch's `an out-of-range staleness scale is clamped ...` (through `max_age_for`) is dropped, because main's check covers both of its arms (`_scaled(...)` reads 180.0 below the floor and 3600.0 above the cap). The check above it, `... max_age_for("indoor_temp_entity", 1e9)`, already ties `max_age_for` to `_scaled`.
- `tests/mutation_ledger/killed_by/sensor.py/RoomSpreadSensor.extra_state_attributes.RETURN_DEL.c783d968.json` is deleted. Its `old` line (`return {key: block.get(key) for key in ("coldest_entity", "warmest_entity")}`) is not in main's `sensor.py` (`grep -n` prints nothing). Main pins the attribute under its own anchor, `RETURN_DEL.4b8933ea`.
- `tests/golden/claimed_drift.txt`: merged by the `claimnotes` driver with no conflict. `git diff origin/main HEAD -- tests/golden/` prints nothing.

## Head

`8fbbe09acf2ef222f1df41a9bcaf9f3e6ef0bbd6`. It merges `origin/main` at `8f39313a44a4baec18b239ba925f6e164eb26bd2` into the PR head `064b60f7b25d8e92aaa843915ef1cff9feb79da4`. Merge base `8f39313a44a4baec18b239ba925f6e164eb26bd2`. Measured 2026-11-17 UTC.

prepr: passed rc=0 at 8fbbe09acf2ef222f1df41a9bcaf9f3e6ef0bbd6

## Mutation proof

Against main, the diff adds one check and no production line. Its mutant, M6, was applied at this head by `sed` to `inputs.py`'s `read_room` sensor branch: `temperature_c(getattr(state, "state", None), state_unit(state))` became `..., None)`. Restored afterwards, and `git diff --quiet custom_components/` was clean.

The command is `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('P').read())" 'R.section("#3616 R11-OUTSIDE-ROOMS-P1'`, where P is what `features_block.py --emit-prelude P` writes from the tree:
- Unmutated: `ok   a degF sensor room converts by its own unit to degC ...`.
- M6: `FAIL a degF sensor room converts by its own unit to degC ... [{'°F': RoomReading(entity_id='sensor.u', temperature_c=None, ...`.

Both runs stop later in the section with `IndexError: list index out of range` at block line 595 (`_rl_on_m = _rl_c_on._rl_margins[0]`). That line is #3678's room-lift check, which needs solve-spy setup the isolated prelude does not carry. The degF check runs before it. The whole script, `PYTHONPATH=tests/hastub python3 tests/features.py`, prints `ALL 5828 FEATURE CHECKS PASSED` at this head.

Review round 2's clamp mutants (`inputs.py` `_scaled` `CLAMP_DROP`) are killed on main by main's two-ended check. Main pins them in `tests/mutation_ledger/killed_by/inputs.py/_scaled.CLAMP_DROP.8c7e424f.json`, which `git diff origin/main HEAD` does not touch.

## Null control

The unmutated run above (`ok`) against the M6 run (`FAIL`). In the failing line, the check's `°C` arm still reads `temperature_c=20.0, problem=None`, so only the unit conversion separates the runs.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=cc2a14d02e0011d801d990595e6d6a34d9862134 head=8fbbe09acf2ef222f1df41a9bcaf9f3e6ef0bbd6 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Scoped scripts, `PYTHONPATH=tests/hastub`: `python3 tests/features.py` and `python3 tests/entities.py`, the two that `scope.run` names: `ALL 5828 FEATURE CHECKS PASSED`, `ALL 2731 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Outside-seat self-tests: the 18 `--self-test` commands and `agreement_py.py --restore` of `.github/workflows/governance.yml`'s step `self-tests-outside-seat`, each run alone. Each exits 0 at this head, at `064b60f7b2`, and at CI's merge ref `00f6c8d7750fecf6f32f29b20b5f50207d02e04c` (script: one `timeout 300 <command>` per line, rc printed per line).
- `python3 -I tools/ci/selftest_scope.py select --base origin/main --head HEAD`: selects `self-tests-outside-seat`. Its `tools/ci/selftest_closures.json` entry sets `objects: true`, which selects it on every scoped diff.
- Architecture score: n/a, because no production line differs from main.

## Red checks

- `governance / instrument-self-tests`, step 48 `Show the self-tests outside tools/audit/seat/ refusing their own fixtures` (job 133782810463, run on merge ref `00f6c8d775`, which `merge_train.py classify` reads as `INTRODUCED`). Repaired by the merge with main:
  - Main's own run at `8f39313a44` (job 133921894551) concludes that step `success`.
  - This head differs from main by one test check and a delivery row, and neither is a file those commands take as input.
  - Locally, every command of the step exits 0 at this head, at `064b60f7b2` and at `00f6c8d775`, so the refusal does not reproduce outside CI.
  - The step's own log lines were not read: `failure_logs.sh` needs `gh`, whose token is refused in this container, and the job-log download URL is refused by the proxy (403). The CI-only cause is therefore unnamed.
  - Cheaper detector: none found. The local run of the same commands, the cheaper path, passes.
  - CI re-proves this head.
- `governance / instrument-self-tests`, step 129 `Refuse a self-test read set the committed table misses`: inherited. Main is red on the same step at `8f39313a44` (job 133921894551), because `tools/ci/selftest_closures.json` misses reads added by recent merges. A re-record hotfix is in flight. Not repaired here.
- `tests / mutation` and `gate`: red at `4fba42d085` (`gate` job 133716327240: `FAIL tests / mutation: failure (this run)`), because `inputs.py` `_scaled` `CLAMP_DROP` survived every driver, so `mutation-autofix` had nothing to pin.
  - Cause: the clamp sat untested in `max_age_for` at the merge base with no ledger row. This PR moved it into `_scaled`, which made it an added site, and the body then gave it to autofix instead of writing a killing check.
  - Repaired at `dcedcd330c` by a killing check and the pin `tests/mutation_ledger/killed_by/inputs.py/_scaled.CLAMP_DROP.8c7e424f.json`. Both are now on main, where main's two-ended clamp check kills the mutants (`## Mutation proof`).
  - Cheaper detector: `prepr.sh` step 6d, which already named the site `ADDED UNPINNED` before the handoff, at no standing cost beyond the prepr run. The gap was the body's disposition of the site, which `ci-autofix.md` already states (autofix pins killed mutants only). No new countermeasure is built.
- `governance / env-matrix` and `governance / policy-docs`: red at `4fba42d085` (jobs 133754597993 and 133754598174), each on `ERROR   [budgets] ... has a cap in dev/governance/config/policy_budgets.json's files_tokens but is matched by no POLICY_GLOBS pattern` for `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md`.
  - Cause, outside this diff: #3668 (`18eba6b397`) made main's `checkOrphanCaps` read `files_tokens` and deleted those two rows. CI graded the branch's older `policy_budgets.json` with main's newer grader.
  - Cleared by merging main: `git diff origin/main HEAD -- dev/governance/config/policy_budgets.json` prints nothing at this head.
  - Cheaper detector: none that this branch owns. A main grader that refuses data an older branch still carries is caught only by a run on the merged tree.
- `tests / replay` and `tests / nightly-status`: red at `064b60f7b2`. Neither is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints, so neither is answered.

## Forward-carry

none

## Friction

none
