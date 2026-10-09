Fix review: blocked f74924e09c63bebdfca1ef2ff17a2c1dfef3845f architecture-unsound: early_cutoff reads raw config keys outside the #1745 typed entry config (entities.py red: UNCLASSIFIED early_cutoff.py), re-spells _on_off_service as a second switch writer, and archscore WORSENS coord_footprint 2587->2594 unreported

bus-nonce: fe54a4e8ddfd09391376a04a6310b4c3
seat: review-2070, round 1. Contract fix-review.md read from origin/main bd59a4af (roles/ diff against the head: empty, so the copy is current).
Measured at 007d44db34206df59e62b97d373b2369c5a64d94. The head moved to f74924e09c63bebdfca1ef2ff17a2c1dfef3845f. That move is record-only: one added line in dev/programme/delivery/2070.md and nothing else (git diff --stat 007d44db..f74924e09). Every number below holds at f74924e09, and the local runs at the live head were taken in a worktree at it. The mutation-autofix bot commit had not landed at posting. It cannot change this verdict, because the three red fast scripts below need a fixer commit.

## Blocking (step 15, fixer.md step 17, judged on added lines)

1. **A concept is duplicated, and the switch has a second writer.** `early_cutoff._switch_off` (early_cutoff.py:302-309) calls `switch.split(".", 1)[0], "turn_off"`. That is the #1526 domain routing that `coordinator._on_off_service` (coordinator.py:2390) already owns, written out a second time. Step 17 says "no concept duplicated" and "the existing mechanism, never a parallel one". It also says actuator writes come "from the coordinator or `pump_arbiter.py`", and this module adds a third writer for the same entity. The body names no alternative placement. Sound shape: move `_on_off_service` to a module that takes values (for example `pump_arbiter.py`, which already owns pump writes) and import it from both callers, or put the write behind a `pump_arbiter` function. Either way the body names the alternatives and why each lost. The design note (rule A) asks for value-taking logic; it does not bless a parallel writer.
2. **The architecture score regressed, and the body does not say so.** `score.py --diff origin/main` prints `dS -0.0039 WORSENS (inadmissible: coord_footprint 2587->2594)`. My attribution with the metric's own `coord_footprint` (evidence/footprint-{main,head}.txt) gives +7 in total:
   - `early_cutoff.state_for` +3 (design rule A allows this one);
   - the class +2 (the two arm statements in `_apply_action`: the `CutoffInputs(...)` build and the lambda delegation);
   - `_tail_freeze` +1 (A2);
   - `diagnostics._coordinator_snapshot` +1 (S7).
   Each item is defensible under the design note. But step 17 requires the score "not regressed, or the raise path", and the body lists the command as "report-only" and gives no figure. Owed: either cut the class's +2 (for example, build the `CutoffInputs` inside `early_cutoff` from the `arbiter_inputs` callable, so the class adds a single delegation), or state the WORSENS in the body with this attribution and the design-note clause that admits each item.

## Red checks the body does not answer (step 11): `fast (3.14)` at f74924e (check-run 113595667988), MODE: SCOPED, 22 run

The body says "Red checks: none". This diff causes all three of these reds; none is main's (main's layout passes at bd59a4af):
- **tests/entities.py**: 1 of 2227 failed, "no migrated module reads a key off a mapping outside a dispositioned site", `UNCLASSIFIED ['early_cutoff.py']`. The module reads `inp.config.get(CONF_...)` at lines 162, 166, 167, 206, 241 and 292 instead of the typed entry configuration (#1745, `entry_config.py`). That is also a fixer.md step 17 departure ("the existing mechanism, never a parallel one"). Reproduced locally (evidence/entities-f74924e.txt).
- **tests/harness_headers.py**: 4 of 109 failed. `dev/audit/rounds/round4/D6/claims.py` records 73 modules and 27 HA importers in its headers; it now prints 74 and 28, and its committed claims.json and claims.md are no longer byte-identical. The diff updated docs/architecture.md's counts but not this harness's recorded output.
- **tests/layout.py**: "reintroduces moved path tools/audit/harnesses/early_cutoff_closed_loop.py; it lives at dev/audit/harnesses/". The harness belongs under dev/audit/harnesses/ (evidence/layout-{main,f74924e}.txt).
`mutation` is also red: the 42 ADDED UNPINNED sites, all listed in the body, pending autofix. `nightly-status` is red and is not this PR's.

## Must also be fixed in this round (not class-blocking alone)

3. **The UTC minimum-run and minimum-stop guards are not pinned.** I mutated `_cycle_guard` to wall-clock arithmetic (`as_local` in place of `as_utc` on `now` and `since`, commit 512f9b33e, local only). Results:
   - `tests/dst_checks.py`: 131/131 passed at the head and 131/131 passed on the mutant (evidence/dst-{head,mut}.txt).
   - Features run under the UTC-identity stub, where this mutant is equivalent.
   - My probe moves under it. P1, spring-forward with a 7-minute true run (67 minutes on the wall clock): the head holds `min_on`, the mutant cuts (evidence/probe-head.txt, probe-mutant-wallclock.txt).
   The body's "UTC arithmetic (the DST suite caught a wall-clock version)" covers `arm`'s cycle end only. Owed: a DST check that drives `on_room_event` across a transition.
4. **A cut can still lead to a short off period.** `MIN_OFF` is measured against `cycle_end`, which is the scheduled cycle. Any off-schedule refresh (`async_set_mode`, `async_update_thermal_params`, `async_apply_manual_plan`, `async_set_away`, the diagnose and sysid buttons, `entity.py:217`) runs `_apply_action`. That re-arms the cut-off and writes the plan's action. Probe P2: cut at 12:12, refresh at 12:13 switches the pump back on, second cut at 12:24. The off period was 1 minute. Every trigger is user-initiated, and the refresh's own re-solve usually says off, so this is narrow. It also matches the existing exposure of any refresh-time switch write. Owed: either qualify "none with under 10 min to the next cycle" in the body as the scheduled cycle, or keep the cut latch and cycle end across an early re-arm.

## Verified (the orchestrator's checks)

- **Inert on the null control, and passes it.** Re-run with synthetic numbers, harness sha as in the body (evidence/loop-*.txt). Plan-aware: NULL 0 cuts, 2.0 kWh, room 20.11-21.02, identical to no cut-off. 0 cuts on LIGHT, OWNMIN, HOT, SUN and COLDSUN, every figure identical to cut-off off. Literal: NULL 2 cuts, 1.4 kWh, 19.99-21.00 (fails the null control); LIGHT 5 cuts, 24.0 kWh, max 21.11. Middle: 0 cuts everywhere. Every number in the body's table reproduced to the digit.
- **The body is honest about inertness.** "It was inert in every measured case and ships as a guard", and the module docstring says the same. This matches decision 6070543876's fallback branch.
- **Minimum run and stop are in UTC in the code.** `cycle_end` is `as_utc(now)+interval`, and `_cycle_guard` compares in UTC. Probe P1 (spring-forward) holds `min_on`; P1b (fall-back, 2 minutes to cycle end) holds `min_off`. Not pinned: see item 3.
- **It writes only the power switch.** The only `services.async_call` in the module is `_switch_off(turn_off)`. The exemptions (mode, plan_off, duty != space, boost on either channel, disinfecting, defrost, tank_cold, zone_cold, stale, no switch or thermometer) each have a features check; M3 and M6 are named in the body. The arbiter-writes-nothing check has its positive control.
- **The measured-start-room bug stays fixed.** `_planned_room` reads `trajectory[i+1]`. Probe P3 (measured 22.5, predicted end 21.0): threshold 21.50, cut. Mutant `trajectory[i]`: threshold 23.00, no cut.
- **A2 order.** `_tail_freeze` returns `FREEZE_CUT` before `learner_unmetered`. 7a (#2065) reads `_learning_frozen(CONF_POWER_ENTITY)` for DrawRange, so the cut reaches S2 through the single reason with no carry needed. Accuracy samples skip it (`_accuracy_freeze_allows_sample`).
- **No coordinator taken outside `state_for`**, apart from `_tail_freeze` and the diagnostics row, which A2 and S7 require.
- **Other checks.** closures passes at the live head. structure.py passes, every row unchanged. merge-tree is clean against origin/main. VERSION, manifest, notes and claim files are untouched.
- **CI, mutation.** `mutation` is red with 45 ADDED UNPINNED entries, which dedupe to 42 sites, exactly the body's list (evidence/mutation-job.log, ci-sites.txt). Autofix is pending, per ci-autofix.md. `nightly-status` is red and is not this PR's.
- **Harness.** `early_cutoff_closed_loop.py` is the fixer's own companion to the finder's `closed_loop_overshoot.py`; its docstring says so. The probe is mine (evidence/probe.py).

RESULT plan_aware NULL cuts=0 kWh=2.0 (no-cutoff 2.0); LIGHT cuts=0; all variants unchanged
RESULT literal NULL cuts=2 kWh=1.4 (fails null); middle cuts=0 everywhere
RESULT archscore coord_footprint 2587->2594 WORSENS
RESULT mutant wallclock-guard: dst_checks 131/131 pass (survives); probe P1 offs 0->1
RESULT mutant trajectory-start: probe P3 threshold 21.50->23.00
RESULT short-cycle via off-schedule re-arm: off period 1 min
RESULT fast(3.14) red: entities UNCLASSIFIED early_cutoff.py; harness_headers D6 73/27 vs 74/28; layout retired tools/audit/harnesses path
