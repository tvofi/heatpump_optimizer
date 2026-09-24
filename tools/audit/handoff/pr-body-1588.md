<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Pump-duty arbiter (judge option O1, as tvofi chose it): the optimizer tells the pump which duty to serve on each plan step. It works over Tuya or Modbus entities.

**Before:** the plan's DHW-only steps never reached the pump. With both set-points fixed at 53 °C, a planned DHW step ran as space heating. If the integration had written DHW-only, the mode read-back would have set `space_blocked` for the whole next horizon (`pump_signals.py` `space_blocked`, `optimizer.py` power caps zeroed). Nothing would then have written Heating + DHW back.

**After:** a new option, `pump_duty_mode`, with the values off (the default), observe and control. In control it writes, per 15-min step:
- **Mode:** DHW only on hot-water-only steps, heating only on space-only steps (tvofi's revision: the cheapest space hours need not keep the tank ready for its next DHW window), Heating + DHW when both are planned or while the integration holds the disinfection switch on, no write on idle steps (the mode on the pump served the duty that just finished, whose thermostat the plan satisfied; Heating + DHW would arm both). Baseline is Heating + DHW.
- **DHW set-point:** the configured hot water set-point, not a literal; on Modbus space-only steps, the gate below.
- **Space set-point:** the weather-curve supply for a flow entity, or the step's planned room temperature for an indoor entity.

**How:**
- **Transport.** GCHV Modbus register 44 offers Off / Cool + DHW / Heat + DHW only, so where the select lists no single-duty option the other duty's set-point is the gate: space set-point to the entity minimum (floor 25 °C) on DHW steps, DHW set-point to the entity minimum (floor 30 °C) on space steps. The configured entities decide the transport.
- **Ownership.** The arbiter's own mode, DHW-only or heating-only, is marked `PumpSignals.mode_owned`. An owned mode blocks nothing, so neither lock-in exists and the legionella mode-block notice does not fire on it. `setpoint_check`'s disinfection-floor notice skips the arbiter's own DHW gate (`pump_arbiter.dhw_gated`). Capability and the learners still read the observed mode.
- **Unreadable mode.** An unavailable mode select is no reading (`_observed` returns `None` for a state `pump_mode.resolve` does not recognise). Before this, an `unavailable` select read more than 20 s after a write was a manual change and switched the optimizer off; found by the surviving `if observed is None` mutant, pinned by "an unavailable mode select is no reading…".
- **Ignored write vs manual change.** Each write records the reading just before it. A differing reading more than 20 s after the write (the fork's 8 s sent-value echo) that never showed our value and still equals the pre-write value is an ignored write: `pump_write_ignored` warning repair, the slot retried after 5 min, optimizer stays on, the first landed write clears it once no retry is pending; leaving control (observe, off, Optimizer active off) drops pending retries and the warning. Anything else — a third value, or any change after our value was read back — is a manual change: stop, Optimizer active off, `pump_manual_change` repair. Limits (in the module docstring and `docs/configuration.md`): a person restoring exactly the pre-write value before our value was read back, or a device reverting inside one reading interval, reads as ignored; after a restart the pre-write readings are gone and any difference is manual.
- **Rails.** A DHW-only lease lasts at most 90 min, or 30 min below −10 °C outdoors, idle steps after it included. The baseline is written on a stale plan, comfort, boost or off mode, sysid, or unload. A pump in a cooling mode is left alone.
- **Observe ledger** (observe and control): per 15-min step, planned duty against measured power (running), mode (DHW only) and tank rise ≥ 0.5 °C over the step; verdict delivered / space-instead / dhw-instead / idle-instead / unknown (no power entity, no tank rise) / baseline. Last 96 steps and counts under `pump_duty.ledger` in the diagnostics; not persisted. No running-mode or valve register is read: the integration has no slot for Modbus registers 45 or 210.
- **Timing.** A one-minute tick, active only when the option is not off, acts at step boundaries. The ownership record is persisted.

The tuya_heat_pump fork is unchanged.

## Head

198883e71db5fd1c27f9b82ff2ad9e1dbe7a2096. Every figure below was measured at this head, except the full-suite mutant runs, which ran at 362e669 (the kill tests before the main merge). The production code for `pump_arbiter.py`, `coordinator.py` and `diagnostics.py` is unchanged between the two. origin/main was 87cf56a when this head merged it.

## Mutation proof

The review's 113 mutants were re-run, using the reviewer's `mkspec.py` with the renames. The unmutated run passes. Each mutant edits one line, and the tree is restored after it.
- The arbiter section alone (features.py prelude + section; `ALL 72 FEATURE CHECKS PASSED` unmutated): 112 of 113 killed.
- The full `PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/features.py` (`ALL 3257 FEATURE CHECKS PASSED` unmutated), run on the review's 35 survivors: 34 killed, 1 survives (E5).
- Tests that do the killing:
  - The real coordinator's `_apply_action`, `_update_current_state` and `async_shutdown`, plus `diagnostics._coordinator_snapshot` (Y1–Y4).
  - A restart through the store: written, manual, and the no-prior manual rule (R6, U7–U9, O6).
  - Stand-down and resume, in memory and on disk (S1, S4).
  - Release while stood down, and release after leaving control (U3, U4, C1).
  - A rewrite's fresh landing (R4) and the set-point tolerance (M3).
  - The 25 °C and 5 °C gate floors (E2, F2, G9), and `dhw_gated` on both sides (I1, I2).
  - Comfort mode and a held-off disinfection switch (J1c, H1).
  - The boundaries: on_kw, lease and cold rail (B3, K2, L3, L5).
  - An unknown duty mode (A1).
  - The ledger's DHW-mode, small-drift, both and baseline verdicts (V4–V6, V8, V9).
- M2 is killed by the head's own `_differs` None check.
- E5 is equivalent. `_bounded` without its `state is None` guard returns a number where it returned `None`, but every caller passes the value to `_write`, and `_write` returns on `state is None` before it writes or records anything. It is not in the ledger, because the review's mutant set is finer than the ledger's operators.
- The ledger: `python3 tests/mutation_table.py --scope full --max 0` prints `3722 unpinned site(s) of 3916 candidate sites, 3725 at the ratchet base … the ledger agrees with the deterministic inventory`.

## Null control

- The unmutated tree passes both harnesses (above), so every kill comes from its mutant.
- The coordinator-wiring checks: under Y1, Y2 and Y3 the real coordinator writes no DHW, writes no baseline and does not mark the mode owned, and each of those fails its own check. The lock-in control ("a DHW-only mode nobody here wrote still blocks space heat") is kept.
- `dhw_gated`: the excuse holds for 40 (the gate as written) and does not hold for 42. The unmutated tree returns True and False.

## Figures

- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. The budget raise is unchanged: `coordinator_loc` and `max_class_loc` 9050→9052 (commit 6410d460).
- `HPO_TYPING_PYTHON=<py3.13 venv with the typing_ruler --print-requirements pins> python3 tests/typing_ruler.py`: `the pinned census passed`, `ALL 9 typing-ruler source checks PASSED`.
- Coverage: `COVERAGE_FILE=… python3 -m coverage run --include=…/pump_arbiter.py tests/features.py`, then `coverage report`, gives `pump_arbiter.py 361 0 100%`. That is features.py alone. CI's `coverage` job runs the fast lane under `coverage_tree.sh`, which I did not run.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`: `ALL 26 FINITE BOUNDARY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 91 HARNESS HEADER CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 1886 ENTITY CHECKS PASSED`, on a full, unshallowed clone.
- `PYTHONPATH=tests/hastub GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/env_drift.py --all`: `CLAIMED config_flow: 2 leaves moved`, then `NO UNCLAIMED DRIFT: 56 scenario(s)`, rc=0.
- `./tests/derive_closures.sh --single <s>` on Linux, for each of the 12 scripts CI listed. Each closure now contains `pump_arbiter.py` and `repairs.py`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL -- every test script runs` (reason: `tests/closures.json changes the gate itself`). The full suite was not run locally; it is CI's.

## Red checks

These went red at fef01b78:
- **typing** (2 × `no-any-return`): fixed at f842cfda. The cheaper detector is `typing_ruler.py` with `HPO_TYPING_PYTHON` set (gate-scoping.md). It costs one pinned venv and was not run before the push.
- **coverage** (`pump_arbiter.py` 94.46% < 95%): fixed at f842cfda, and now at 100% (Figures). The cheaper detector is `coverage run` on features.py, about 4 minutes.
- **closures** UNDER-SCOPED on 12 scripts, and **closures-autofix** `skip-failed-recording`: re-recorded here with `--single` on Linux. The recording failed because finite_boundary.py failed, which f842cfda fixed.
- **fast (3.14)** had three failing scripts:
  - finite_boundary: the loader, fixed at f842cfda.
  - harness_headers: the counts, fixed at f842cfda.
  - env_drift: config_flow was stale. It is re-recorded and claimed here.
  - The cheaper detector is running these three scripts locally; each takes seconds to minutes.
- **mutation** was INCONCLUSIVE, because its baseline was red. That baseline is now green locally.
- Not verified here: the full gate and `coverage_tree.sh fast`. CI's run on the pushed head decides those.

## Forward-carry

none

## Friction

- fixer: cost: the review's 35 survivors on the full features.py take about 3.4 minutes each, so about 2 hours serially. I ran them on three worktrees in parallel.
- gate-scoping: cost: any diff that touches `tests/closures.json` forces `MODE: FULL`, so a fix to closures can never be gated by scope.

## Approval

Budget raise: `coordinator_loc` and `max_class_loc` go from 9050 to 9052 (+2) for the arbiter's call sites in the coordinator (commit 6410d460). tvofi accepted budget raises for this feature on 2026-09-24T17:58Z. It still needs tvofi's own approving review before merge. No policy file changes. `tests/golden/claimed_drift.txt` carries one claim, config_flow. Under tvofi's mandate (to 2026-09-25T08:40Z), the recommended option was taken: re-record and claim the config_flow golden, rather than leave it flagged.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
