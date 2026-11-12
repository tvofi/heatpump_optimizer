R10-SAV-VALUATION-RESIDUE, part 1 of 3 (Carry 0 to Carry 4). Behind a valve whose curve's top draw falls short of the setpoint's steady need, `_thermostat_held_state` set the zones to the target anyway. No thermostat behind that curve keeps that state, so every booked reference step drew its stores: -34.85 kWh_th over the valve arm, booked as reference heat nobody paid for. The held zones now sit at the temperature whose steady need equals the curve's top draw (`thermal_model.valve_top_draw`), found by bisection (`_VALVE_HELD_BISECTIONS`). That state is an equilibrium, so the booked steps draw no stored heat. A curve that can hold the target leaves the held state exactly as before. Unvalved installs are untouched: the function returns before the valve branch.

Alternatives and why each lost:
- (a) Settle the reference's store change per booked step in the ledger. That books a sag no thermostat behind this curve undergoes, and it moves stored-heat valuation, which Carry 4 rules out ("a fix there changes the reference ..., not stored-heat valuation").
- (b) Find the equilibrium by simulating the reference forward until it settles. That costs a horizon of steps per solve on a Pi-class target. The closed-form balance (need at level zones against the curve's top draw) is monotone in the zone temperature, so bisection reaches it in 40 evaluations of arithmetic.
- (c) Book `_compute_baseline_power`'s first simulated step in place of the apportioned one. The first step from a held 21 C is still the sag's transient, so it does not remove the cause.

The brief's carries:
- Carry 0 (the unattributed residual, -3.75 % / -8.12 % at its source): #3442 attributed it (Carry 4's text). This diff removes the attributed store term. The flat arm's residual moves from -3.90 % to +4.78 % (`## Figures`).
- Carry 1 (part-load refill pricing in `_terminal_cost` and `_deferred_energy_cost`): built by #3442 (`optimizer._refill_law`, one law for both twins). Re-measured at this head: terminal and deferred gaps read 0.000000 and `null rows not zero 0` (`## Figures`). This diff touches neither function. The hot-water LP's secant stays with Carry 5.
- Carry 2 (Carry 1's segment-or-rate decision and its zero-derate control): decided in #3442 as the stated rate. The control still reads `null rows not zero 0` at this head.
- Carry 3 (the residual at the merge base): re-measured at 14f227c5, -3.90 % flat and -8.02 % varying. At the head it is +4.78 % and +1.20 %.
- Carry 4 (the attribution and its fix): built in this diff. Its acceptance was that the store term reads 0 on a reference at equilibrium and that the flat arm's residual moves by the term's share. The store term goes from -34.85 to -0.30 kWh_th. The non-steady loss term goes from +12.52 to -0.30 kWh_th. In kWh_th the remaining residual is -0.60, so the +4.78 % left in kWh_e is the COP gap #3442 named (reference 1.820 against the plan's 1.92, a ratio of 1.055).
- Carry 6 and Carry 11 repeat Carry 3, and Carry 7 and Carry 12 repeat Carry 4. Each is answered by the carry it repeats, so nothing further is owed for them.
- Carry 5, Carry 8, Carry 10 and Carry 13 belong to parts 2 and 3 and are not answered here. Carry 8 and Carry 13 repeat Carry 5. Carry: dismissed: evidence, not a finding
- Carry 9 also belongs to a later part, and this diff moves its starting point. On a valve curve that cannot hold the setpoint, the reference's held state now starts at the curve's equilibrium below the target (single-zone at -10 C: 17.205 C), not at 21 C. Carry 9's "19.93 against 21.00" was read from a held 21 C start, so it is not comparable at this head.
  - A pass ending below 21 there is the curve's limit, not the controller's. A controller fix is legitimate only if the curve's top draw at the target exceeds the level-zone steady need (`valve_top_draw` against `_thermostat_demand_*` at level zones), measured on the install's own valve parameters.
  - Re-measure `r10_advisor_steady_seams.py fields` at that part's merge base. Carry: dismissed: Carry 9 is already this group's, and its later part reads this body

## Head

`11dc22c875d08470487f8f4baad8c8692bf2ac9d` is `mutation-autofix`'s commit `ci: pin killed mutants` on top of `00a7af72471a8a864b9830848cf4d948080d01a2`. It adds four `killed_by` rows and touches no other file (`git diff --stat 00a7af7247 11dc22c875`: 4 files, 24 insertions, all under `tests/mutation_ledger/killed_by/`). This repair adds no commit: the head is the autofix's.

`00a7af72471a8a864b9830848cf4d948080d01a2` merges origin/main `19baca7618` into the authored code head `2e5cad3b03888993a595dd5649a63ddaa05a196a` (an automatic merge by the orchestrator's script; no resolution was needed).

2e5cad3b03888993a595dd5649a63ddaa05a196a, cut from `origin/main` 14f227c5bd0eb80855b21055cc668857a5f820b4. The fix and its check are 8bd0eae9. a8d91109 orders the bisection span (`min()` dropped) and deletes the two moved pins. 4f4f3f1e adds the three triage rows. 2e5cad3b adds the check's 14 C and 16 C rows, which kill three of prepr's diff-mutant survivors (`## Unpinned sites`). No production figure below moves between 8bd0eae9 and this head: the span change is equivalent wherever the bisection runs. The block was re-run at 2e5cad3b (`ALL 5 FEATURES BLOCK PASSED`). Production figures measured 2026-11-12 (UTC); the repair's figures re-taken at 11dc22c8 against origin/main 8c10361e, 2026-11-12 (UTC). VERSION, the manifest and RELEASE_NOTES are untouched.

## Mutation proof

The group's blocks were run standalone at 8bd0eae9 in a detached worktree:
`PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- R10-SAV-VALUATION-RESIDUE: stored heat" "# --- R10-WATER-SETPOINT-FEEDBACK"`. Each production line was neutralised in turn, then restored.
- M1, `if short(held) > 0.0:` to `if False:`: FAIL `R10-SAV-VALUATION-RESIDUE: behind a valve whose curve cannot hold the setpoint, the thermostat reference starts where that curve holds the house ...`.
- M2, the bisection step `lo, hi = (lo, mid) if short(...) > 0.0 else (mid, hi)` to `lo, hi = (lo, mid)`: FAIL, the same check.
- M3, `valve_top_draw`'s `return _circuit_draw(circuits, model.params.buffer_max_temp)` to `return math.inf`: FAIL, the same check.
- M4, `if short(held) > 0.0:` to `if True:`: FAIL `R10-SAV-VALUATION-RESIDUE: null control -- a valve curve able to hold the setpoint leaves the held state's zones at the target`.
- NULL, a comment edited inside the change: `ALL 5 FEATURES BLOCK PASSED`.

At the base 14f227c5 the new check FAILs (`1 of 5 FEATURES BLOCK FAILED`). At the head all 5 pass.

## Null control

- A valve curve able to hold the setpoint (`mixing_valve_target` 40.0, two-zone and single-zone, -10 C): the held zones read exactly 21.0 at both ends, and the first step's store change is 0.0. The new null-control check asserts this, and M4 kills it.
- Unvalved installs return before the valve branch. The tank temperature reads the same `zoned(...)` call at a level target as before (`h.room_temperature` equals the target), so a curve that holds the target is bitwise unchanged.
- Flat-price null (mandatory): `valve-flat` is the flat-price arm. Its residual carries no price term, and the store term is price-independent (-34.85 on both arms at the base, -0.30 on both at the head).
- Zero-derate control for Carry 1 and Carry 2: `null rows not zero 0` from both companions at the head.
- Unpinned-site ratchet (the repair's figure): at 00a7af72 CI printed `2612 unpinned site(s) against 2608 at the ratchet base`, 4 added by this diff; at 11dc22c8 the same instrument prints `2608 unpinned site(s) of 7242 candidate sites, 2608 at the ratchet base 19baca76...`. The 00a7af72 reading is the control: the same command on the tree without the autofix's four rows reads the four sites unpinned.

## Figures

<!-- figure-block: scope-line mb=19baca76181cb019d9b1cfd93ee6bc0a08e20047 head=11dc22c875d08470487f8f4baad8c8692bf2ac9d -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

- **Held state and first-step store change.** The new check's `_svh_case` is driven over two-zone/single-zone at -10/-15 C, and at 14/16 C since 2e5cad3b (fixture: `profiles.house` with the valve arm's `manual` valve, target 21.0). Each reading is the store change of one reference step at `_compute_baseline_power`'s power on a one-step horizon, in kWh_th.
  - Base 14f227c5: held room 21.0 everywhere; dS -0.3870, -0.4658 (two-zone), -1.0875, -1.2750 (single-zone).
  - Head 8bd0eae9: held room 19.695, 19.430 (two-zone), 17.205, 16.510 (single-zone); dS 0.0000 in all four.
  - Head 2e5cad3b, the mild rows: two-zone 20.970 at 14 C and 21.0 at 16 C; single-zone 20.543 and 20.821; dS 0.0000 in all four.
- **Why the base is infeasible.** At -10 C on the valve arm's two-zone install, the level-zone steady need at 21 C is 5.612 kW against the curve's top draw of 4.357 kW. Probe in scratch, driving `_thermostat_demand_two_zone` and `_valve_draw_circuits` on the held state.
- **Residual and attribution**: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat` and `winter_typical` (sha1 4b214a9bc277...). Its harness residual line is `r10_sav_wood_reference.py`'s `valve-flat` / `valve-vary` closed loop. `plant steps seen 192 of 192` at both ends. Carry: dismissed: evidence, not a finding
  - Base 14f227c5: residual -3.90 % (flat), -8.02 % (varying); reference stored -34.85 kWh_th; non-steady +12.52 / +11.89.
  - Head 8bd0eae9: residual +4.78 % (flat), +1.20 % (varying); reference stored -0.30 kWh_th; non-steady -0.30 / -0.93.
- **Carried pricing figures** at the head: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py` (sha1 8b5cdfa93b3e...) prints `flat d=0.112: ... lp_err max 0.267290 (dhw cost max 7.0145)` and `null rows not zero 0`. `r10_sav_valuation_residue.py` (sha1 146c08d9faf2...) prints `flat d=0.112: cells 16 lp gap max 0.335995 terminal gap max 0.000000 deferred gap max 0.000000`, `null rows not zero 0` and `failures 0`. These are #3442's readings, unchanged.
- **Class sweep.** Rule: `git grep -n "_thermostat_held_state(" -- custom_components/` enumerates every reader of the held state. Each site and its disposition:
  - `_compute_baseline_power`'s first step: closed in this diff (the booked reference).
  - `_start_gap_cost`: closed in this diff. It reads the same function, so the start's stored-heat settlement now values the gap against the equilibrium the thermostat keeps.
  - The definition itself.
  - No other reader exists.
- **Unpinned-site ratchet** at 11dc22c8: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` (CI's `tests / mutation` command) prints `2608 unpinned site(s) of 7242 candidate sites, 2608 at the ratchet base 19baca76181cb019d9b1cfd93ee6bc0a08e20047; the ledger agrees with the deterministic inventory`, and no `ADDED UNPINNED` line. The local run's mutant draws were stopped at the 30-minute background bound after its baselines and null control (`NULL_COMMENT survived every driver`); the mutant verdicts are CI's at the same head (`## Red checks`).
- **Structure**: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` at 11dc22c8.
- **Gate**: the scope line is the generated block above (registry `scope-line`, rendered by `figure_block.py` at whichever head it names). `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at 8bd0eae9 prints `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN` (exit 0), including `ALL 5299 FEATURE CHECKS PASSED`, `ALL 2709 ENTITY CHECKS PASSED` and `ALL 116 STRESS CHECKS PASSED`.

## Red checks

- `tests / mutation` at 00a7af72 (job 131279233005, run 43245625153): `MUTATION TABLE REFUSED -- 2612 unpinned site(s) against 2608 at the ratchet base 19baca76..., 4 of them added by this diff`, the four `ADDED UNPINNED` sites optimizer.py:596 CLAMP_DROP, :639 GUARD_OFF, :649 CMP_BOUND and thermal_model.py:2302 RETURN_DEL. All four were killed and measured before the push and left to `mutation-autofix` (`## Unpinned sites`), which pinned all four in 11dc22c8. At 11dc22c8 the unpinned count equals the base (`## Figures`, Unpinned-site ratchet), and `tests / mutation` is green (job 131317100996, run 43256638000: `MUTATION TABLE PASSED`).
  - Survivors at 11dc22c8, from that job's table (`3 survivor(s) of 4 evaluated = 0.0% (3 triaged equivalent, raw 75.0%), cap 20.0%`), each with its disposition:
    - optimizer.py:602 CONST `_VALVE_HELD_BISECTIONS = 40`: triaged equivalent, `survivor_triage/optimizer.py/@module.CONST.b8c7cb71.json`.
    - optimizer.py:639 CMP_BOUND `if short(held) > 0.0:`: triaged equivalent, `survivor_triage/optimizer.py/_thermostat_held_state.CMP_BOUND.42081e68.json`.
    - optimizer.py:644 CMP_BOUND, the bisection step's `> 0.0`: triaged equivalent, `survivor_triage/optimizer.py/_thermostat_held_state.CMP_BOUND.745fa965.json`.
    - thermal_model.py:2302 RETURN_DEL: killed by `tests/features.py` (`PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced`).
  - The triages were written by hand in 4f4f3f1e with their reasons (`## Unpinned sites`), not by automation; no survivor is left without a disposition.
  - Root-cause answer: the cheaper detector exists and ran. `prepr.sh` step 6d (`tools/pr/ci_predict.py`) listed every site locally, at no added standing cost, and each had a disposition before the push. A red until the lane pins is the ratchet's intended route for a `custom_components/` kill (`ci-autofix.md`); nothing further to build.
- `gate` at 00a7af72 (job 131283135569, run 43245635284): `FAIL run(s) [43245625153] at this head are still being judged; their gate decides` -- `tools/ci/gate.py`'s `deferral()`, which defers to the lower-numbered run at the same head. That run's own verdict was red on `tests / mutation` (above) and on `arch-score / arch-score`, which failed on `gh: HTTP 503` fetching the pull request (job 131279233398), a GitHub API outage outside this repository, owner GitHub. The gate red carries no cause of its own: it is the deferral to those two reds. `arch-score / arch-score` at 11dc22c8 is green (job 131317102626).
  - Root-cause answer: no cheaper detector exists. The gate red is derived from the two reds above, each answered there; the 503 is an outside service, detectable only at the call it failed.
- `gate` at 11dc22c8 (job 131354606349, run 43256638000): `FAIL run(s) [43256618046] at this head are still being judged; their gate decides`, the same `deferral()`. Run 43256618046's open unit was `pr-contract / pr-contract`, red on the previous body (next item).
  - Root-cause answer: derived, as above; it carries no cause of its own.
- `pr-contract / pr-contract` at 11dc22c8 (job 131353666654): `PR-BODY: 3 error(s)` on the previous body, which `## Red checks` did not name `arch-score / arch-score` or `tests / mutation` in, and whose scope-line figure block named head 00a7af72 (`figure_block.py verify`: `1 refused`). This body names both reds. Its scope-line block is the registry's render, not typed text: `body_patch.sh` and `open_pr.sh` re-render it with `figure_block.py refresh` at the head they push, so the orchestrator's delivery-row commit leaves a block that refresh, not a seat, re-renders. `tools/pr/prepr.sh --body-check` on this body at 11dc22c8 prints `PR-BODY: 0 error(s)` and `figure_block verify: 1 block(s), 0 refused`.
  - Root-cause answer: the cheaper detector exists and is the one that cleared this body: `prepr.sh --body-check` (seconds, run before every body push). The previous body predates the autofix commit and the arch-score 503, so no local run could have seen them; a body re-written after the autofix lands is `ci-autofix.md`'s route. Nothing further to build.
- `tests / nightly-status` (job 131367041075) is red at 11dc22c8 and is outside the set `python3 tools/audit/seat/merge_train.py owed-reds` prints; it grades `main`, so it is neither answered here nor a block (`defect-root-cause.md`, Enforcement).

## Unpinned sites

Each site is on `custom_components/`, the lane `mutation-autofix` mutates. A kill marked "measured" was read with the group's block run standalone (`## Mutation proof`'s command).

- custom_components/heatpump_optimizer/optimizer.py:596 CLAMP_DROP: pinned by `mutation-autofix` in 11dc22c8 (`killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json`; measured: the held-state check and its null control FAIL)
- custom_components/heatpump_optimizer/optimizer.py:602 CONST: triage `survivor_triage/optimizer.py/@module.CONST.b8c7cb71.json` (equivalent; 80 measured, block passes)
- custom_components/heatpump_optimizer/optimizer.py:639 CMP_BOUND: triage `survivor_triage/optimizer.py/_thermostat_held_state.CMP_BOUND.42081e68.json` (equivalent; measured, block passes)
- custom_components/heatpump_optimizer/optimizer.py:639 GUARD_OFF: pinned by `mutation-autofix` in 11dc22c8 (`killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.42081e68.json`; measured, M1)
- custom_components/heatpump_optimizer/optimizer.py:644 CMP_BOUND: triage `survivor_triage/optimizer.py/_thermostat_held_state.CMP_BOUND.745fa965.json` (equivalent; measured, block passes)
- custom_components/heatpump_optimizer/optimizer.py:649 CMP_BOUND: pinned by `mutation-autofix` in 11dc22c8 (`killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.4aa37f7d.json`; measured: `PYTHONPATH=tests/hastub python3 tests/features.py` under the mutant prints `1 of 5299 FEATURE CHECKS FAILED`, FAIL `behind a valve at zero demand the held tank keeps its measured temperature, ...`, against `ALL 5299 FEATURE CHECKS PASSED` unmutated)
- custom_components/heatpump_optimizer/thermal_model.py:2302 RETURN_DEL: pinned by `mutation-autofix` in 11dc22c8 (`killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json`; measured: the block raises `TypeError`)

`prepr.sh`'s diff mutants (`MUTANT_CMD` = the block above) at 4f4f3f1e left 8 survivors. Each, with its disposition at this head:
- optimizer.py:596 CONST_SWAP `max(1.0, q_floor)`: killed by the 14/16 C rows (FAIL, dS -0.075 to -0.1875).
- optimizer.py:639 CONST_SWAP `short(held) > 1.0`: killed (the two-zone 14 C shortfall is under 1 kW; FAIL, single-zone 14 C dS -0.1438).
- optimizer.py:649 CONST_SWAP `held_need > 1.0`: killed (two-zone 16 C, FAIL, dS -0.1749).
- optimizer.py:602 CONST_SWAP `_VALVE_HELD_BISECTIONS = 41`: equivalent, as the CONST triage row argues (41 narrows the bracket by half of 2**-40).
- optimizer.py:634 CONST_SWAP `need`'s dt 0.25 to 0.5: equivalent. At level zones the demand's pull-back and slab-charge terms are zero, so dt multiplies nothing; measured: block passes.
- optimizer.py:639 and 644 CMP_BOUND: the triage rows above.
- optimizer.py:649 CMP_BOUND: killed by `tests/features.py`, as above.

The two `killed_by` rows whose lines this diff moved (`_thermostat_held_state.CLAMP_DROP.5c7d4c36`, `_thermostat_held_state.CMP_BOUND.76b8fad3`) are deleted, because no inventory site keys them any more. Their lines are the 596 and 649 sites above. The 640 `CLAMP_DROP` site left the tree: a shortfall needs heat, so the outdoor is below the target, and the span's `min()` is gone.

## Forward-carry

none

## Friction

none
