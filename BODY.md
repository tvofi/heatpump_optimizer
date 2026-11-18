R11-SEAM-tests (round 11; findings D10-s1-05, D10-s1-06, D9-s3-01, D9-s3-02; classes I1, I5), built to the approved design at 2d01f6d379cce723f4427314307b74912c9f0e81 (`design.md`, decision 0014). No production file changes; `tests/golden/` and both claim files are byte-identical to the merge base. The round's class issues are unfiled (`ISSUES.json` `number: null` for I1 and I5), so this body closes no issue number.

- **A, D10-s1-05.** `tests/config_flow_steps.py` gains a tracker owned by `Ledger` (`install_tracker`). It is installed once on the two production flow classes, so every flow the script builds registers, the seven construction sites and `async_get_options_flow` alike (the design's tracker, placed at class level rather than at each site, so a new construction site cannot miss it). Each error check is now followed by `recover()` on the instance that rendered the error, walked to `create_entry` (options pages save with `after_save=close`) or to a success abort. The script's last check refuses any rendered `(kind, step, error)` triple that no rendering instance finished.
- **B, D10-s1-06.** No edit, as the design rules. `tests/coverage_ratchet.py` grades the register's floors against a fresh `coverage.json`; its detection is shown under Mutation proof.
- **C, D9-s3-01.** Not in this PR. This is the design's own cut (§7, "cut C into its own pull request, so the owner step blocks only C"), because probing every recorded row is expected to need a CI-platform re-record. See Forward-carry.
- **D, D9-s3-02.** A new lane, `tests/cycle_lane.py`, wired into `run.sh`'s units lane. It drives `_async_update_data` on five sweep scenarios: inline worker, stubbed fetchers, one warm-up cycle and four measured cycles. It checks solves, payload bytes (encoded), retained bytes per cycle, optimizer yields and loop-side `coordinator.py` calls against the new `tests/cycle_budgets.json`. `tools/policy/budget_raise_gate.py` gains that file's schema: four ceilings, and the yields as a floor.
  - Yields count `time.sleep` from `optimizer.py` frames, which covers the function-local `import time` site the design's notes name.
  - Retained bytes are read in a second pass under `tracemalloc` that replays the first pass's solve results, because `tracemalloc` slowed one scenario's real solves about 13x (52 s). That channel therefore covers the coordinator's own retention, not the solver's allocations.
  - `percycle.py` gives every label the same coordinator config. The lane maps each label's season, DHW and zone fields onto the config, so `winter/2z/dhw` and `winter/cycle` share a record.
- **Carry 0 (the roster's carry 0 for this group: the #3195 review's savings test gaps), built.** Each mutant was planted at the merge base and driven through the `tests/features.py` R10-SAV-COMFORT block (`tools/audit/seat/features_block.py`). M13 (`step["baseline_kw"] = baseline[i]` -> `pass`) is already killed by `R10-SAV-COMFORT: the baseline is booked on the steps it covers and no further`. M3 (the midpoint `delivered = 0.5 * (zone[i] + zone[j])` -> `zone[i]`) is already killed by the four `the comfort shortfall floors each demand at zero` and `two-zone, the comfort shortfall is the lower floor's` checks. M9 (the meter `scale` dropped from `stored_sek`) and M10 (dropped from `comfort_sek`) survived, 21 of 21 passing. They are now killed by `R11-SEAM-tests (carry 0, M9): a calibrated month scales the stored-heat line as it scales the thermostat` (stored -2.0 against -3.0) and `R11-SEAM-tests (carry 0, M10): ... comfort line ...` (1.0 against 1.5). Each check compares two ledger months that differ only in meter calibration (1.0 and 1.5), so it does not re-implement the production formula.
- **Same seam, found while measuring.** `config_flow_steps.py --self-check` exited 1 on main (`MISSED reconfigure guard runs on own identity`). Its mutation wrapped `async_step_user`, while the guard has lived in `async_step_user_sensors` since the #198 split. The mutation now wraps the sensors step, and all six mutations are caught.

## Head

fc544a6739bb9d721cc2b7313dbb81eef552ee98

Measured against `origin/main` as of 2026-11-18 (`date -u`), which is also the merge base (`git merge-base origin/main HEAD`).

## Mutation proof

- **A, finished predicate.** Both tracker sites were set to never mark a flow done. The closing check FAILS with `RESULT unrecovered_flow_error_triples=54`; restored, it is green.
- **A, one recovery deleted.** Deleting `recover(flow4, "rooms", ...)` FAILS the closing check with exactly one residual, `UNRECOVERED options/rooms/too_many_rooms`; restored, it is green.
  - Not every deletion reddens: the `entities_metering` triple is recovered both at its own site and by the `PAGE_REJECTIONS` loop, and the metric counts a triple once any instance finishes.
- **A, failing test first.** Commit `94125c37ed` (tracker and closing check, no recoveries) fails `config_flow_steps.py`: `RESULT unrecovered_flow_error_triples=52`, `1 of 600 checks FAILED`.
- **D, each injected arm.** `tests/cycle_lane.py --arm <arm>` reddens only its own channel, 5 of 25 checks each:
  - `solves2x`: solves 2/4/2/4/2 against records 1/2/1/2/1.
  - `payload2x`: about 173-179 kB against a limit of about 130-134 kB.
  - `retain`: about 187-193 kB/cycle against 16384.
  - `noyield`: yields 0 against limits of 175.3-344.7.
  - `--self-check` runs all four arms and the clean arm, and ends `SELF-CHECK PASSED`.
- **Gate schema.** Changing `(("*", "yields"), MIN)` to `MAX` fails two self-test checks: `cycle: fewer solves, more yields is routine` and `cycle: the yields floor down is a raise`. Restored, the result is `300 checks, 0 failed`.
- **B, the existing detector.**
  - Coverage file: a local `coverage.json` (sha1 `5960296b5a`) from `tools/coverage/coverage_tree.sh fast` at the merge base. CI's venv has no `coverage`, so it ran in a scratch venv with coverage 7.17.3.
  - The same file with `config_flow.py` trimmed to 917 of 1020 executed lines (sha1 `55c9deda89`) makes `tests/coverage_ratchet.py --coverage` print `FAIL every module >= 95.0 %  (1 below)` and `1 module(s) below the 95.0 % per-module floor: config_flow.py 89.90 %`, and exit 1.
- **`MUTANT_CMD`.** `python3 -I tools/policy/budget_raise_gate.py --self-test`, over the gate's added lines.

## Null control

- **A.** At the merge base, the finder's harness reads 54 rendered triples, 52 unrecovered. The two reauth triples are already finished at both ends.
- **B.** The untrimmed `coverage.json` prints `COVERAGE RATCHET PASSED`, `every module >= 95.0 %  (0 below)`, and exits 0.
- **D, clean arm.** Five clean check runs stay inside every threshold. Their retained readings were 1184-2995 B/cycle, with the record run's 3393 the largest clean reading. `RETAIN_FLOOR_B` 16384 sits above that, and below the `retain` arm's ~187 kB.
- **D, lane reach.** The reach companion reads `coordinator_functions_started=0` on `tests/structure.py` (null) and 246 on `tests/cycle_lane.py`. The finder's `reach.py` read `coordinator.py executed=0` for the stress gate.
- **Gate.** The self-test's `cycle: null control` holds an unchanged document to no raise.

## Figures

- Finder's recovery harness at the base: `unrecovered_triples=52`, `error_triples=54`. At the head: `unrecovered_triples=0`, `error_triples=54`. The script line is `exit=0 last=['ALL 672 checks PASSED']`. Command: `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D10/s1/cfg_recovery.py`, with `$EXPORT` = `plan/r11` at `50a932de3b`, sha1 `677301f5b8d3e957c24e9f36d23b8a98cf80a68c`.
- The suite's own reading: `RESULT flow_error_triples=54` and `RESULT unrecovered_flow_error_triples=0`, from `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`. That command ends `ALL 672 checks PASSED`, and its `--self-check` ends `all six mutations caught by their named checks`.
- `coordinator_functions_started=246` (`tests/cycle_lane.py`) and `0` (`tests/structure.py`, null), from `PYTHONPATH=tests/hastub python3 lane_reach.py <script>`. `lane_reach.py` is a scratch companion to `reach.py`, sha1 `1134980e27012bbddbce8e0cc29ff69fedd58364`: `sys.monitoring` PY_START over code objects whose file is `coordinator.py`.
- Cycle-lane records: `tests/cycle_budgets.json`, written by `PYTHONPATH=tests/hastub python3 tests/cycle_lane.py --record` at the merge base's production tree. One check run took 51-60 s of wall time on a 4-vCPU box.
- `script_runs_per_push`, the every-script-once count `tests/entities.py` derives (closures test scripts plus `coverage_tree.sh fast` scripts): 54 at the base, 56 at the head. `tests/entities.py` ends `ALL 2732 ENTITY CHECKS PASSED`.
- `Architecture score: dS +0.0000 NULL`, from `python3 tools/audit/archscore/score.py --diff 8751943e17ef4d3ec699e7859ae829b4528d8ce7`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 5903 FEATURE CHECKS PASSED` on the restored tree.
- Scope: `tests/run.sh` changed, so `python3 tests/closure.py select --diff 8751943e17ef4d3ec699e7859ae829b4528d8ce7` reads `MODE: FULL`. Run locally (each exit 0): `config_flow_steps.py`, `cycle_lane.py`, `entities.py`, `structure.py`, `closure.py selftest`, `layout.py`, `harness_headers.py`, `env_drift.py --claims-only`. The rest is left to CI.

<!-- figure-block: scope-line mb=8751943e17ef4d3ec699e7859ae829b4528d8ce7 head=fc544a6739bb9d721cc2b7313dbb81eef552ee98 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Raise justification

`tests/ci_budgets.json` `script_runs_per_push` 54 -> 56. The new lane is one new script, which the closures instrument and the coverage fast stage each measure once (34+20 -> 35+21). The reason is in commit `e2e48474c8`'s message. This raise is under mandate 6893738184 (scope all).

- Payments tried: folding the lane into `tests/stress.py`, refused by the approved design §4 because it would add the lane's cost to the serial alone-on-the-box tail. Folding it into `tests/features.py`, refused by design §4 because it would put a ratchet with a record mode inside a behaviour script. Excluding `cycle_lane.py` from the coverage fast stage, refused because it moves code to an unmeasured path (`fixer.md` step 17). No deletion or share pays a new script's runs.
- Architecture score: dS +0.0000 NULL

## Unpinned sites

- `tools/policy/budget_raise_gate.py` self-test lines `cycle:` (10 survivors from `prepr.sh`'s diff mutants: CONST_SWAP, CALL_DEL and STMT_DEL on the five new checks and their `y0` fixture). These are the self-test's own fixtures and assertions, not the gate's logic. A swapped fixture constant still reads the same side of each threshold, and a deleted check removes an assertion; neither is a gate behaviour a check could pin. The schema lines they exercise are killed: flipping `yields` from MIN to MAX fails two of these checks (Mutation proof).

## Red checks

- `budget-raise-gate`: red by design until the raise is approved. The base's copy of the gate reads 27 raises. One is `script_runs_per_push` 54 -> 56. The other 26 are the leaves of the new `tests/cycle_budgets.json`, which the base's schema does not know and so reads as frozen; the head's copy, with this PR's schema, reads only the one. Answered under `## Raise justification`. Cheaper detector: none is owed, since this is a raise and not a defect. The tree check that measures the count, `tests/entities.py`'s every-script-once count, is the one that found it locally before any push.

## Forward-carry

- C (D9-s3-01, the memory pass probing every recorded row) is the split part the approved design names (§7). It lands in its own pull request, after a CI-platform clean all-row run decides which rows the owner must confirm re-recording. The base reading is the design's: the finder's memory harness (round 11, D9/s3, `--jobs 2`) reads `blind_confined` 48, and the null flags 9 unprobed rows on a clean tree. Carry: dismissed: the approved design's own split part (§7), dispatched by the orchestrator as its own pull request; `carry_audit.py` reads no lower-case group token, so `R11-SEAM-tests` cannot be named as a destination
- `script_runs_full_case_pr` (68) is derived only from CI's `ci-metrics` artifacts, not from the tree. The new lane is expected to add up to two runs to a full-case pull-request run, so the ci-ratchet on `main` may read it above 68 after this merges. Re-record it from that run's measurement; this branch cannot measure it. Carry: dismissed: a CI-measured row, re-recorded from main's own run, which no branch can measure

## Friction

none
