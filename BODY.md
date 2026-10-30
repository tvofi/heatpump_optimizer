R10-SAV-ACTUATION (#2492 carry 5, seam 2). The cycle wrote the pump's power switch once per optimization interval (30 min by default). A plan step's change therefore reached the pump only at the next cycle, as late as one interval past the step boundary, and a step's duty verdict in the arbiter's ledger depended on where the cycle fell against the 15-minute step grid. This PR writes the switch at the step boundary from a one-minute tick, and the ledger now reads the meter at each tick instead of the cycle's sample.

Refs #2492. Not closed here: one residue of the duty ledger is routed under Forward-carry to #2492.

## Re-cut

Round 4 under the three-round rule. The body is replaced. It carries the template's headings, the arms that fire, and only the figures re-taken in this pass. The block it answers is the fix review's `blocked` at `9fe3c4cf8`, `mutation-vacuous`. The reviewer's mutant R3 wires the step tick around `_write_supply`, the gate the cycle uses. It survived all 4617 checks of `tests/features.py`. This pass adds one case per gate arm. No production line changed: `git diff 9fe3c4cf81465123f5dc6b360a30df7631f75974 HEAD --stat` prints `tests/features.py | 74 +` and nothing else.

**Design (unchanged by this pass).**
- **Owning seam.** The switch's one writer stays `pump_arbiter.switch_supply`.
- **The gated write.** The coordinator's `_write_supply`, which both the cycle and the tick call, holds the gate. The gate has two arms: the early cut-off's `MIN_OFF` hold (`early_cutoff.allow_on`) and the blocked-mode OFF skip. The pure skip decision is `pump_arbiter.supply_write`.
- **The tick.** The tick is `pump_arbiter.supply_tick`. `pump_arbiter.note_supply` arms it once, from the cycle's write. It takes plain values, never the coordinator. `SupplyWiring` carries them: the `arbiter_inputs` builder, the boost record, and the gated write.
- **When the tick writes.** At a new step, the tick writes the step's command (`step_supply`) only where it differs from the last command.
- **The plan's switch rule.** `thermal_model.plan_step_runs` is its one owner.
- **The ledger's reading.** The ledger reads `pump_arbiter.live_power_kw` at each pass.

**The two cases this pass adds** are in `tests/features.py`, section "supply switch at step boundaries", in `_sa_gate_tick`. Each drives the REAL coordinator:
- 05:45: one `_apply_action` writes ON and arms the tick.
- 06:00: the armed tick fires at a step the plan turns off.
- 06:15: the armed tick fires at a step the plan turns on.
- Arm 1, the `MIN_OFF` hold. `early_cutoff.state_for(coord).cut_at` is set to 06:10, as `early_cutoff.on_room_event` records a cut. The check asserts the 06:15 tick writes no `turn_on`. Its null control is the same run with no cut on record, where the 06:15 tick writes `['turn_on']`.
- Arm 2, the blocked-mode OFF skip. `_pump_signals` is set to an observed mode with `space_heat=False, dhw=False`, so it blocks both channels. The check asserts the 06:00 tick writes nothing. Its null control is the same run in the default mode, which blocks nothing; there the 06:00 tick writes `['turn_off']`.

## Head

`343f2abcf7f5a4b0fc306591436496b4d04010fc`: the review's head `9fe3c4cf81465123f5dc6b360a30df7631f75974` plus one commit, which changes only `tests/features.py`. Merge base `89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6`. `origin/main` was at `507a9ec264eb373b132248d752259254d8a9fa4d` (`date -u`: Fri Oct 30 13:00:29 UTC 2026). No merge was made: the handoff freezes the branch, and this pass is test-only.

## Mutation proof

Mutant R3 is the reviewer's own. I took the driver from `ev/mutant_driver.py` on `probe/rev-2968-5f6e06db` and changed only `HEAD` (to `343f2abcf`) and the scratch output directory. In `coordinator.py`'s `_apply_action`, the tick's `SupplyWiring(..., boost.held_for(self), self._write_supply)` becomes `lambda on: pump_arbiter.switch_supply(self.hass, getattr(self, "_ctx", self)._config.heat_pump_switch_entity, on)`. The driver asserts that the `str.replace` matches exactly once and applies it in a fresh detached worktree. It then runs the whole of `PYTHONPATH=tests/hastub python3 tests/features.py` and removes the worktree.

- `python3 mutant_driver.py R3` prints `RESULT R3 rc=1 ['2 of 4621 FEATURE CHECKS FAILED']`:
  - `FAIL the step tick inside MIN_OFF of an early cut-off writes no turn_on at a step the plan turns on  [{'06:00': ['turn_off'], '06:15': ['turn_on']}]`
  - `FAIL the step tick writes nothing at a step the plan turns off while the pump's mode blocks both channels  [{'06:00': ['turn_off'], '06:15': ['turn_on']}]`
  - Both null controls stay `ok`. No other check fails.
- Green restored: `python3 mutant_driver.py BASE` (the same driver, no mutation, same head) prints `RESULT BASE rc=0 ['ALL 4621 FEATURE CHECKS PASSED']`.
- At the review's head `9fe3c4cf8`, the same mutant printed `ALL 4617 FEATURE CHECKS PASSED` (the reviewer's `ev/mutant_R3.res`). The four added checks make the difference.

No pin is owed. R3 is outside the mutation lane's operators (BOOLOP, GUARD_OFF, CMP_BOUND, RETURN_DEL), so `mutation_table.py` has no site to pin for it. The diff adds no production line. `ci_predict.py` (Unpinned sites) reports the result.

## Null control

Each new check has its null control in the same run with the gate inactive, both `ok` at the head:
- `null control: the same tick with no cut on record turns the switch on as the plan says`: the 06:15 tick writes `['turn_on']`. Arm 1's empty-`turn_on` result therefore comes from the cut-off hold, not from a tick that never fired.
- `null control: the same tick in a mode that blocks nothing writes the plan's OFF`: the 06:00 tick writes `['turn_off']`. Arm 2's empty write list therefore comes from the blocked-mode skip.

## Roster carries

- Carry 1, carry 5 seam 2's controls from #2745. The phase-0 and 14-minute installs book identical verdicts from step 1: `a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)`, which is `ok` in this pass's `ALL 4621` run. One mutant per seam turns that check red; this pass did not re-run those mutants, so the figures are not restated.
- Carry 2, D15 L5. `written/silent` and the GCHV night slots are declared in the `pump_duty` store domain: `every slot the pump arbiter persists is declared in the pump_duty store domain`, `ok` in the same run.
- Carry 3, actuate at step boundaries with the design note first. The design is under Re-cut. This pass adds the tick's gate checks, which mutant R3 turns red (Mutation proof). The tick's guard checks are `ok` in the same run.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py` at `343f2abcf`: `ALL 4621 FEATURE CHECKS PASSED` (rc=0), including the four new checks. The count rule is `R.check` calls run: `grep -c 'R.check(' tests/features.py` reads 4197 at `9fe3c4cf8` and 4201 at the head.
- R3 at `343f2abcf`: `2 of 4621 FEATURE CHECKS FAILED` (rc=1), red on exactly the two new gate checks. Unmutated: `ALL 4621 FEATURE CHECKS PASSED` (Mutation proof).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6 PYTHONPATH=tests/hastub ./tests/run.sh` at `343f2abcf` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`
  - Every script in its three parallel lanes and `arch_score_head.py` printed `ok`: env_drift `--claims-only` and `--all`, validate, closure selftest, features, edge, backtest, boost_drift_replay, arch_score, optimality, plan_view, card.mjs, card_drift.mjs, entities, block_duty, doc_claims, wood_advisor, config_flow_steps, structure, typing_ruler, manual_plan, solar_alignment, guard_pins, debug_collect, finite_boundary, layout, deployment_shape.
  - The run was stopped by the session's 30-minute background-task limit at the start of `tests/stress.py`, its last stage. `stress.py` was not run here and is left to CI (Friction).
  - `harness_headers.py` was run alone: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` (rc=0).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- CI prediction: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 89ccf73266a8 (a data-file read is not seen)` (rc=0), with no `ADDED UNPINNED` line.

## Architecture score

n/a: this pass changes only `tests/features.py`, which no production metric reads. `tests/arch_score.py` and `tests/arch_score_head.py` printed `ok` in the scoped gate above.

## Red checks

- `mutation-vacuous` (fix review `blocked` at `9fe3c4cf8`): this is a review verdict, not a CI check. It is answered by the two cases above, which R3 turns red.
- No CI check is red at `343f2abcf` as far as this seat can see: it was not pushed before this handoff, and no local script went red.
- `tests / mutation`, red on earlier heads of this branch, among them `4a049adf0`, `fd6103038` and `84aaba6ea`; green at `9fe3c4cf8`, where every check run concluded success.
  - The cause: unpinned sites the branch added, which no check killed when they were added. In round 2, four step-tick guards were turned into checks and pinned. In round 3, `pump_arbiter.py` `step_supply` CMP_BOUND and `note_supply` GUARD_OFF were turned into checks and pinned.
  - The cheaper detector already exists: `tools/pr/ci_predict.py` plus `tests/mutation_table.py --pin-killed`, run before the push. It costs one `features.py` run per site.
  - The gap was a body that sent a survivor to the autofix lane, which pins kills only. `ci-autofix.md` ("A survivor") already says so, so no new detector is owed.
  - This pass adds no production line and no site: `ci_predict.py` prints no `ADDED UNPINNED` line.
- `tests / nightly-status` and `governance / delivery-status`, red on earlier heads of this branch: both are main-graded, reporting main's nightly runs and the delivery record. This diff touches neither the workflows nor their reporters: `git diff --name-only 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6...HEAD -- .github/workflows/nightly.yml tests/nightly_status.py` prints nothing. Both are green at `9fe3c4cf8`.

## Forward-carry

- The duty ledger books the first reading of an OFF step after an ON step from the previous step's tail. `pump_arbiter._observe` folds a run at any tick reading at or above `on_threshold_kw`, and the arbiter's own tick and the supply tick fire in the same minute. The control holds: such a step is booked `space-instead` at both phases. A settle window on the ledger's run fold is still owed. That is the ledger's change, not the actuator's, so this PR says `Refs #2492`. #2492's group is held in `dev/programme/rosters/wave-r10-groups.json` (R10-SAV-ACTUATION, issues [2492]), and the orchestrator decides whether the residue keeps the issue open or moves it to a new group. Carry: #2492

## Friction

- gate-scoping: cost: in this cloud seat, `tests/run.sh`'s scoped gate outlives the 30-minute background-task limit, which stopped it at `tests/stress.py`. `arch_score.py` alone took 1407 s, and `features.py` and `entities.py` about 590 s each. `stress.py` was left to CI's required check, which a mutation-proof pass may do (`fixer.md` step 5). Carry: dismissed: environment-only, CI runs `stress.py`

## Unpinned sites

none: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `343f2abcf` prints no `ADDED UNPINNED` line. This pass adds no production line, so it adds no mutation site.
