R10-COMBI-TANK-STORE (R10-COMBI-TANK PR A, L; design `a605014bff4478f470853109060f4ff7ef605d4c`, approved by `design-verdict/r10-combi-tank` `56810263b`, Cost and Order section's PR A scope). Issue #3225 (outside user Bankaifan): a combi store, where one body of heating water serves the space circuit and hot water through an exchanger, cannot be modelled; entering the store as both tanks counts its heat twice. This PR lands the store physics. **No loader or option sets `dhw_combi_tank_enabled`**, so no install can reach combi, and with the option off every plan is byte-identical (golden drift, below). Refs #3225; PR B (R10-COMBI-TANK, topic `r10-combi-tank-b`) makes it reachable and closes it. This PR closes no issue.

What changes:
- **`thermal_model.py` owns the store.** `DhwStore` (frozen, module level) is the one view every hot-water recursion reads, through `ThermalParameters.dhw_store`. Off combi it is the separate tank's own values and both transforms return their argument itself. In combi it is the buffer store over `buffer_store_volume` (buffer plus potable litres), with the buffer's UA, the tighter of the DHW and buffer limits, and the exchanger effectiveness `combi_dhw_effectiveness` (floored at `COMBI_DHW_EFFECTIVENESS_FLOOR`, capped at 1). `combi_tank_active` is the design's predicate. The tank type is two numbers (`combi_dhw_effectiveness`, `combi_potable_volume_l`), never a code branch.
- **One step, both stores.** `store_step` is the hot-water step for the separate tank and the combi store alike; `simulate_dhw_step`'s body was a second copy of exactly this physics and now calls it, bitwise identical off combi. The draw is debited at the tap temperature (`tap_temp_for_store`), the rating clamp and inlet floor book what they refuse or inject, so `C·dT = (heat_in − draw − loss − refused + injected)·dt` per step.
- **The flux exchange (design, Solver).** The space steps (`_simulate_step_single`, `_simulate_step_two_zone`, `simulate_trajectory_batch`) take the hot-water side's net flux as `WeatherSeries.buffer_exo_kw`, joined to the tank's input behind the valve; every DHW recursion takes the space side's as `tank_exo_kw`. The published walk (`simulate_trajectory_with_dhw`) is one node: its DHW trajectory is its buffer trajectory.
- **Departure, raised: the exchange is a bounded repair, not a scored candidate.** The design's one extra iteration under the "adopt only if it scores better" gate never adopts: the replan buys more hot water, so it always scores worse on the space objective, and the space side drains the store below the DHW floor. `_combi_flux_exchange` re-plans hot water against the fixed space plan's net flux until the plan stops moving, at most `_COMBI_EXCHANGE_ROUNDS` DHW builds, and keeps the space plan it was computed against: a space re-solve would draw the repair straight back out.
- **Readers moved to the view** (census `combi_store_view`), **tap limits enter the store frame and the legionella target never does** (census `combi_tap_limit`), and **every DHW walk carries the space flux** (census `combi_flux_live`). `buffer_store_volume` keeps the `dhw_combi_tank_enabled` conjunct ahead of `combi_tank_active`: off the option its two per-step readers then evaluate no predicate, which `tests/stress.py`'s production-call channel reads.

## Re-cut

Fourth round (`fixer.md`, "Past three rounds"). Round 3 blocked `577c6974205926e7dbaa178b91af96a229ea02f3` on CI state alone (`verdict/3358` `36f106fd9`): no code change was owed. This head merges `origin/main` `b8f67a775137a8032d5c71b34ea64165c1d4613a` into it with no conflict and no resolution, so the reviewed patch is unchanged (`## Figures`, patch identity). Every figure below was re-taken at this head; round history is deleted.

**Disclosed self-correction, kept:** round 1 said the `and` in `buffer_store_volume` "carried two BOOLOP sites no input could separate"; the production-call count separates them, `tests/stress.py` read it red in round 2, and the conjunct was restored there.

## Head

Head 6254262796cdec57bec1dec5c0d038ba933a215a: `Merge origin/main into fix/r10-combi-tank-pr`, parents `577c6974205926e7dbaa178b91af96a229ea02f3` (the round-3 head) and `origin/main` `b8f67a775137a8032d5c71b34ea64165c1d4613a`, merged 2026-11-10 UTC. Every figure below was taken at this head.

## Mutation proof

Each mutant of `thermal_model.py:329` (`buffer_store_volume`'s guard) was applied in a detached worktree at this head and the whole of `PYTHONPATH=tests/hastub python3 tests/features.py` run:
- Unmutated: `ALL 5071 FEATURE CHECKS PASSED`, rc 0.
- **MA**, the conjunct dropped (`if self.combi_tank_active:`): `1 of 5071 FEATURE CHECKS FAILED`, rc 1: `off the combi option the buffer's store volume, capacity and UA evaluate no combi predicate; null control: with the option on the volume evaluates it and adds the coil` `[off: 3 predicate evaluation(s), ...; on: 1, 544.0]`.
- **MB**, the predicate dropped (`if self.dhw_combi_tank_enabled:`): `1 of 5071 FEATURE CHECKS FAILED`, rc 1, the same check by its null arm `[off: 0 ...; on: 0, 544.0]`.

The store physics, the flux exchange and the three censuses are killed by the `R10-COMBI-TANK-STORE` block of `tests/features.py` and the pinned and triaged sites in `tests/mutation_ledger/` the earlier rounds landed; this pass re-took none of those per-mutant runs, because the merge changed no line of this diff (`## Figures`, patch identity). Two of them, named M2 (the exo term dropped from the LP's free recursion) and M4 (dropped from the legionella run-up walk) in the round that ran them, fail only the `combi_flux_live` census, which `## Forward-carry` cites.

## Null control

- **Option off, the whole plan:** golden drift against the merge base (`## Figures`); no claim file is touched.
- **Option off, field for field:** harness `off_store_bitwise=1`.
- **The counting check:** off, zero predicate evaluations and the bare 504 l buffer; on, at least one evaluation and the 40 l coil added. MA fails the off arm, MB the on arm.
- **Separate tank and a space-flux series:** `lp_flux_separate_none_kwh=3.1405` equals `lp_flux_separate_draw_kwh=3.1405`, while combi moves `3.0285` to `6.7956`.
- **UA = 0:** `ua_zero_residual_kwh=3.553e-15`.
- **eps above the mixer:** `eps_0.6_end_c` = `eps_1.0_end_c` = `62.088350802154`.
- **No exchange:** `null_rounds=0` leaves the store short (`null_worst_shortfall_c=28.767`); the exchange arm does not (`exchange_rounds=3`, `exchange_worst_shortfall_c=-1.455`).
- **The equivalence triages:** each tie-only control moves every tie its grid holds and nothing else (`equiv_eps_tie_control_differ_on_ties=1`, `equiv_step_tie_control_differ_on_ties=3`, `equiv_floor_tie_control_differ_on_ties=3`, each `..._off_ties=0`), so the mutants' `differ=0` is read where they could differ.

## Unpinned sites

`python3 tools/pr/ci_predict.py` at this head prints `CI PREDICT: no closures, fast, governance or instrument red predicted against b8f67a775137 (a data-file read is not seen)`: no unpinned site this diff adds.

## Figures

At head `6254262796cdec57bec1dec5c0d038ba933a215a`, `origin/main` `b8f67a775137`:
- Patch identity: `git diff -U0 72a2acee55181f0e3da9df691657c905d3b2d119 577c6974205926e7dbaa178b91af96a229ea02f3` and `git diff -U0 origin/main HEAD`, each filtered to `+`/`-` lines without the file headers, give 2399 lines apiece and `diff` exits 0 on them; control: the two name lists (`git diff --name-only`) are the same 75 files.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` prints `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, its golden lane `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, and stress.py `production calls: 20 of 20 family members judged against origin/main (3aac11dfba2a)` with `re-planned: []`, then `ALL 114 STRESS CHECKS PASSED`. `origin/main` moved to `3aac11dfba2a` during the run (the gate's own fetch); `git merge-tree --write-tree origin/main HEAD` against it prints no CONFLICT, so it is not merged.
- `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 5071 FEATURE CHECKS PASSED`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; nothing re-recorded.
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- `tools/pr/prepr.sh` without a body: `PRE-PR: 6254262796cdec57bec1dec5c0d038ba933a215a ... rc=0`.
- Harness `dev/audit/harnesses/r10_combi_tank.py`, sha1 `e47dc605d1d95abd50b796d52730bd3394c36702`, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py`, rc 0: `workaround_tank_kwh_per_c=1.1693` (504 l counted twice, 2 components) against `combi_tank_kwh_per_c=0.6310` (one 544 l store, 1 component); `combi_store_ua_w_per_k=2.4667` (111/45); `balance_residual_kwh=-7.105e-15`; `legionella_eps_0.6` = `legionella_eps_1.0` = `(True,4,1.0)`; `exchange_dhw_kwh=22.135` against `null_dhw_kwh=5.327`; the `equiv` arm `equiv_eps_differ=0` of 11 cases, `equiv_step_differ=0` of 53, `equiv_floor_differ=0` of 56. Every RESULT equals round 3's reading at `577c69742` except the two wall-clock `*_solve_s` lines, which are this container's single-solve seconds and are not compared. The harness cannot run at the merge base: the combi fields do not exist there.

## Red checks

Every red on the branch's pushed commits:
- `gate` (129247913713 in run 42636985416; 129283823160 in run 42636336860, both at `577c69742`): each failed with `FAIL run(s) [...] at this head are still being judged; their gate decides`, deferring to run 42635950938, which a main move cancelled and whose re-attempt then concluded its gate `success` (129334713797). No unit job was red at that head. No cheaper detector exists in this branch: the red is the deferral gate standing after the run it deferred to resolved, a CI-state condition of the train, not of this diff; this head is the repair.
- `pr-contract / pr-contract` (129328706084 and 129342618295, run 42635950938 re-attempts, at `577c69742`): the step `Wait for code scanning and list its open alerts` failed closed (`this run's codeql jobs were not listed finished after 600 s`), so no body step graded the body. On a re-run attempt the carried-over `codeql / Analyze (...)` jobs are listed without `steps`, and `tools/ci/codescan_wait.py` `settled()` requires the `Perform CodeQL Analysis` step row. Cause outside this branch (`tools/ci/` on main); cheaper detector: a step-less job fixture in `codescan_wait.py --self-test`, carried to its owner below, not built here.
- `tests / fast (3.14)` (129011161134 at `64d4e7dbc`; 129053216077, 129053413468 at `77a57c37a`): `tests/stress.py`'s production-call channel over 1.05x on four valve scenarios, caused by round 1 dropping `buffer_store_volume`'s conjunct; fixed in round 2. Cheaper detector: the scoped gate's `tests/stress.py`, which `scope.run` names and `fixer.md` step 5 already requires before a handoff; process state (b), nothing built.
- `tests / mutation` (128902067136 at `d67725b0f`; 128944332674, 128949628098 at `74df96f1`) and `tests / mutation-autofix` (128944016780 at `d67725b0f`): unpinned sites this diff added, each since pinned or triaged. Cheaper detector: `prepr.sh` step 6d lists the sites; whether one survives is known only by driving it, which `--pin-killed` is, so none cheaper exists.
- `governance / delivery-status` (128949628159, 129010967839, 129052972430): `DELIVERY STATUS OVERDUE` on other pull requests' rows; it grades `main` and is not a required check.

## Forward-carry

- PR B must empty `unwired_combi` in `tests/features.py` (`the combi store's fields are reachable from no config key until PR B wires them`) when its loader wires the three fields; the check refuses itself the day a wired field stays in the set. Control: the check's own reading at this head (`probe` None for all three). Carry: R10-COMBI-TANK (item unwired-combi-set)
- The flux exchange is a feasibility repair adopted without a score, on the fixed space plan; in combi the hot-water channel buys the heat the space side draws from the store (harness `exchange_dhw_kwh=22.135` against `null_dhw_kwh=5.327` on the same day). PR B's display and accounting (the DHW kWh tile, savings attribution) must read the store's charge as one channel or say which split it shows; re-measure with the harness's `exchange` arm at PR B's merge base. Carry: R10-COMBI-TANK (item exchange-accounting)
- The exo term in the LP's free recursion and in the legionella run-up walk is killed only by the syntactic census `combi_flux_live` (mutants M2, M4): the later planner stages close what the seed under-buys. PR B, or any stage changing the planner's stages, keeps that census and does not read lp_flux as covering those two sites. Carry: R10-COMBI-TANK (item exo-seed-census-only)
- Carry 7, the `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` trailer: not landed here; PR B lands the setup an install reaches and carries it in one of its own commits. Carry: R10-COMBI-TANK (item bankaifan-trailer)
- `tools/ci/codescan_wait.py` `settled()` fails closed on every partial re-run of a code run that owns codeql. The jobs carried over from an earlier attempt are listed without `steps`, and `settled()` requires the `Perform CodeQL Analysis` step row. Measured from an `origin/main` `2f6d699e5` checkout by importing the production module: three `CODEQL` jobs listed `completed`/`success` with no `steps` key give `settled()` False and `legs_uploaded()` `[]`. Control: the same three jobs with that step row give `settled()` True and all three legs. Live instance: run 42635950938 attempt 4, whose `codeql / Analyze (...)` jobs (129342605703, 129342605813, 129342606740) are listed with no steps while `pr-contract` (129342618295) is listed with them. So re-running a red `pr-contract` on its code run cannot turn it green; an edit run is needed, which takes the other-run path. On that path the same step-less listing gives `legs_uploaded()` `[]`, so no leg's alerts are read: the fail-open half that R10-FLY-GH-READ-RETRY's own-run carry names, now measured on the other-run path as well. Re-measure on that group's merge base with the same two listings. Carry: R10-FLY-GH-READ-RETRY

## Friction

none
