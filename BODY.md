Closes #3289

R10-MIN-POWER-FLOOR, built to the approved design (`design/r10-min-power-floor` 23fbff36b, `Design review: approve 23fbff36` at e3568092b). A non-modulating pump planned steps below `heat_pump_min_power`, because nothing could declare it on/off when its surface is not switch plus setpoint; and a clamped switch-plus-setpoint install with DHW shipped space plus DHW above `p_max` (5.30 kW on a 3.5 kW pump), because `optimizer._realize_draw` projected the two channels separately while one compressor serves both.

- `compressor_modulation` (auto / on_off / modulating) on the `thermal_model` options page. `thermal_model.declared_modulation` is the only reader of it and of the legacy `clamp_planned_levels` (true -> on/off, false -> modulating, read only under auto or absent). `probe_install` sets `InstallCapability.on_off`, and `can_duty_cycle` returns False first when it is set, so `levels_clamped`, `learner_unmetered` and `draw_range.planned_range` follow without changes of their own.
- `thermal_model.project_space_against`: space projected against the DHW the step already carries, clipped to `[0, p_max - d]`, with a running level below `p_min - d` raised to it. The total is 0 or in `[p_min, p_max]`, and DHW keeps what its planner booked. `_realize_draw` reaches it through `optimizer._realize_joint` when clamped with DHW, in `objective`, `objective_batch` and the publish.
- Departures from the design note, both behaviour-identical:
  - The publish calls `_realize_joint`, the typed DHW-present arm `_realize_draw` delegates to, and not `_realize_draw`. `_realize_draw`'s optional DHW failed mypy against the publish's non-optional `optimal_dhw`.
  - The note's floors at 0 (`max(0, p_max - d)`, `max(0, p_min - d)`, `min(lo, hi)`) are dropped. A cap below 0 already clips to 0 and a raise below 0 matches no running level, so they changed no output except under `p_min > p_max`, where `project_planned_levels` raises to `p_min`. Without them `d = 0` is that function exactly, and their CLAMP_DROP mutants, all equivalent, are gone.
- It shares `_onto_band` with `project_planned_levels`; a second copy would have raised `duplication_copies`. The space-only path is unchanged.
- Behaviour that changes, by install: a probed switch-plus-setpoint install with DHW (space capped at `p_max - d`), and a declared `on_off` on any surface (newly clamped). Clamped without DHW, and every unclamped install, are unchanged: the harness's clamp=False arm is byte-identical at both ends.
- Alternatives that lost (the design's): a shared scale on the total writes into the DHW plan the space solve treats as fixed and makes the batch's DHW a matrix; an integer on/off solve needs a second backend on a Pi-class target; flipping the probe default clamps modulating installs no finding names; a boolean UI key cannot store "absent".
- Space below `p_min` is counted only on space-only steps (DHW <= `MIN_RUNNING_DRAW_KW`): in a mixed step space is a diverter share of a compressor running at >= `p_min` (carry a1c0f3d2). The harness's older `space_steps_below_min` (from `channel_heating_steps`) reads 3, 1, 3 in the DHW cells at the head for exactly that reason, and `space_only_below_min` reads 0.
- Roster: the queued edits (files `config_flow.py`, `const.py`, strings x3, `draw_range.py`, `tests/features.py`, `tests/config_flow_steps.py`, `tests/golden/claimed_drift.txt`; size L; `after` R10-HOTFIX-COP-UNMEASURED, R10-GENERIC-HEAT-CURVE) are still in the drain queue, so the roster row lists fewer files than this diff touches. Per the brief this group goes first (issue 3289 is outside); the `after` edges are textual, rebase at merge. `draw_range.py`, `plan_slots.py` and `tests/config_flow_steps.py` needed no edit. The diff also touches `tests/golden/config_flow.json` and `dev/audit/rounds/round3/D5/option_doc_coverage.py`, which design verdict e3568092b (i) asks the orchestrator to add.

## Head

f60b4d8c0f5c219e6b8c6d506f4874ce4c8f2a0a

origin/main moved to 48af0864a after this branch was cut. `git merge-tree --write-tree origin/main HEAD` reports no conflict (the ledger driver resolves `structure_budgets.json` and `closures.json`), so per the owner ruling of 2026-11-07 main is not merged; the merge train recarries the head.

## Mutation proof

Each mutant applied to the head's production file, the block run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- #3289 a declared on/off" "# --- R10-SETPOINT-POWER"`, then restored (`git status` clean after each):

| mutant (production edit) | checks that went red |
|---|---|
| M1 `if self.on_off: return False` deleted from `InstallCapability.can_duty_cycle` | 4: declared on/off clamps on every surface; null control (auto/absent/legacy); unmetered on/off freezes the learner; per step, declared on/off (7 steps below 2.5) |
| M2 `duty_cycle_realizable`: `declared_modulation(cfg) is True` -> `is not None` | 3: declared on/off clamps; null control; per step, declared |
| M3 `learner_unmetered`: `is True` -> `is not None` | 1: unmetered on/off freezes the learner |
| M4 `project_space_against` cap ignores DHW (`p_max - 0 * dhw`) | 4: space projects against DHW; clamped realization; per step, declared (max 4.x); per step, probed (max 4.34) |
| M5 the `(0, p_min - dhw)` raise dropped (lower bound `0 * dhw`) | 4: same four |
| M13 raise ignores DHW (`p_min - 0 * dhw`) | 4: same four |
| M6 `_realize_joint` returns the per-channel space projection | 3: clamped realization; per step, declared (max 5.x); per step, probed (max 5.30) |
| M10 the publish reverted to two `_published_levels` calls | 2: per step, declared; per step, probed (max 5.30) |
| M11 `_realize_joint`'s `if not clamp` guard always true | 3: clamped realization; both per-step checks |
| M12 `_realize_draw`'s DHW-less arm ships space unprojected | 1: clamped realization |
| M7 `probe_install`: `on_off=False` | 4: as M1 |
| M8 `declared_modulation` ignores the legacy key under auto | 2: null control; declared_modulation's reading order |
| M9 the select's `on_off` read returns None | 4: declared on/off clamps; reading order; learner freeze; per step, declared |

The draw_range consequence (carry f850a2a5) is pinned in the `draw_range` block beside S4. Under M1, "S4 on a setpoint-only install declared on/off: the metered floor raises the min end" goes red; "S4 a declared on/off install whose plan writes the frequency still reads None" pins the `plan_writes_power` arm.

## Null control

- Harness clamp=False arm (the duty-cycle reading, which this fix leaves alone): all 8 lines byte-identical at base and head (`diff` printed nothing and the `&& echo` fired).
- Harness clamp=True DHW-off lines (4): byte-identical at base and head. The clamped DHW cells move, as the design says they must.
- Flat-price cells beside every cost figure: the objective moves both ways at spread (38.844 -> 39.056, 20.652 -> 20.601) and at flat prices (67.571 -> 67.364, 39.167 -> 39.167). These are objective values and not a savings claim: base's objective scored draws the pump could not deliver.
- `auto` and an absent key give base's `clamp_planned_levels` on five surfaces (`_MPF_UNMETERED` True; `_MPF_METERED`, `{}`, setpoint-only and frequency-sensor-only False), checked by the block's null-control check against the head's own `from_mapping` with no key.
- `option_fields_undocumented=0` reads 1 with the new docs row removed. That is the docs row's own control.
- Failing tests first: at base the block cannot import `CONF_COMPRESSOR_MODULATION`, `declared_modulation` or `project_space_against`. The per-step values its two solve checks see at base are the harness's base lines: declared arm 7 running steps below 2.5 kW, probed arm max total 5.30 kW.

## Figures

- Harness, base vs head (`dev/audit/harnesses/r10_min_power_floor.py`, sha1 a93b48e6096e, landed here, extended from the finder's e21d29905d30): `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_min_power_floor.py`, run in a detached worktree at dee8b413f with the head's harness copied in, and at the head. clamp=True with DHW: `max_total` 5.30 / 5.00 / 5.00 / 3.50 at base, and 3.50 in all four at the head; `total_below_min` 0 at both ends. Declared arm `clamp=on_off` (a metered map with `compressor_modulation: on_off`): at base it equals the clamp=False lines (7 / 5 / 62 / 27 / 55 / 39 running steps below 2.5 kW); at the head `total_below_min=0`, `space_only_below_min=0` and `max_total <= 3.50` in all 8 cells.
- Harness null control: `diff` of the 8 clamp=False lines base vs head printed nothing (`&& echo` fired); the 4 clamp=True DHW-off lines are byte-identical.
- Objective values (not savings), spread / flat: spread DHW -4 C 38.844 -> 39.056, spread DHW 5 C 20.652 -> 20.601, flat DHW -4 C 67.571 -> 67.364, flat DHW 5 C 39.167 -> 39.167. Same harness lines.
- The #3289 block: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- #3289 a declared on/off" "# --- R10-SETPOINT-POWER"` prints `ALL 9 FEATURES BLOCK PASSED` at the head.
- Mutation proof, 13 hand mutants: each replaces one production line and runs the block command above. All 13 exit 1 (table above).
- Diff mutants (owner ruling): `MUTANT_CMD='env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# --- #3289 a declared on/off" "# --- R10-SETPOINT-POWER"'`; `python3 -I tools/audit/seat/mutant_run.py --diff dee8b413fd7da7b07f13e28a93d7d49b4a9e978a...HEAD --cmd "$MUTANT_CMD" --max-mutants 0 --report-only` mutates every added production line (18 mutants, `--list` counts them). 0 SURVIVED, wall 32.2 s. Instrument control: the same run with `--cmd true` prints 18 SURVIVED. Before the block gained its undeclared-default check, it printed one: `thermal_model.py` `on_off: bool = True`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=dee8b413f PYTHONPATH=tests/hastub bash tests/run.sh` at 29018cb29: `GATE EXIT 0`, "32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN". The one later commit is test-only (`tests/features.py`); `closure.py select --diff 29018cb29` names `tests/entities.py` and `tests/features.py`, re-run at the head with `env -u BASH_ENV PYTHONPATH=tests/hastub`: `ALL 2655 ENTITY CHECKS PASSED` and `ALL 4923 FEATURE CHECKS PASSED`.
- Golden drift (item 6e2b19c4 / ed1d276b): `tests/env_drift.py --all dee8b413f…` in that gate run passed. No solver fixture moves; `config_flow.json` moves ADD-ONLY (`git diff --numstat` 20 insertions, 0 deletions) and is claimed. `card_claimed_drift.txt` is byte-identical.
- `RUNNER_TEMP` in this container: `/etc/profile.d/hpo-toolchain.sh`, which `tools/audit/seat/cloud-setup.sh` writes and `BASH_ENV` names, exports `RUNNER_TEMP` to a directory that does not exist. Every nested `bash` re-sources it and overwrites a caller's value: `env RUNNER_TEMP=$T bash --noprofile --norc -c 'echo $RUNNER_TEMP'` prints the profile's path. With `BASH_ENV` set, `tests/entities.py` fails 3 checks at base and at the head with the same failing set (release ZIP, Pages workflow, coverage-job cache); `diff` of the sorted FAIL names was empty. With `env -u BASH_ENV` it prints `ALL 2655 ENTITY CHECKS PASSED`. The gate and `prepr.sh` ran with `BASH_ENV` unset for that reason; venv-ci's python3 stays first on PATH (`command -v python3`).
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `class_excess_loc` 17561 -> 17559 was recorded in its own commit, because the publish's two projections became one call inside `HeatPumpOptimizer`. `duplication_copies` stayed at its budget because `_onto_band` is shared.
- Architecture score: `python3 tools/audit/archscore/score.py --diff dee8b413f` prints `Architecture score: dS +0.0000 NULL`.
- Typing: `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py` prints `ALL 9 typing-ruler checks PASSED`. The first cut's `assignment` error (+1, publish's `optimal_dhw`) is why `_realize_joint` exists.
- D5 option coverage: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round3/D5/option_doc_coverage.py` prints `option_fields_rendered=205`, `option_schema_keys_rendered=238` and `option_fields_undocumented=0` (base 204 / 237). With the new docs row removed it prints `option_fields_undocumented=1`. EXPECTED was moved in the same commit.
- D6 claims register C125: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` reads `46 selects, untranslated=[]` (base 45). Regenerated and committed.
- `option_doc_coverage` re-measure after R10-GENERIC-HEAT-CURVE: owed at merge (Forward-carry).
- Sibling seams (step 8): the enumerator is the design's grep, re-run at the head: `grep -rn "can_duty_cycle()\|fully_metered()\|CONF_CLAMP_PLANNED_LEVELS\|levels_clamped(\|_published_levels(\|project_planned_levels(\|_realize_draw(\|clamp_planned_levels=True" custom_components tests/*.py`. Production seams and their dispositions:
  - `thermal_model` `can_duty_cycle`, `fully_metered`, `duty_cycle_realizable` and `learner_unmetered`: closed here, through `declared_modulation` and `on_off`.
  - `optimizer` `_realize_draw` in `objective` and `objective_batch`, and the publish: closed.
  - the space-only solve's `_published_levels`: unchanged, because DHW is absent there.
  - `optimizer` `_duty_floor`, `_scores_rounded` and `_relaxed_starts`: read the flag and do not project; unchanged.
  - `draw_range.planned_range`: follows `can_duty_cycle`, pinned in S4.
  - `diagnostics.py`: passes the probe to `draw_range.diagnostics_view`; follows.
  - `config_flow`: writes the key only.
  Test seams: `_sp_solve`'s DHW cells move and their predicates still hold, which the gate's `features.py` run checks. `_r10s_solve` (`dhw=False`) and `_sp_clamped`/`_sp_free` (quadratic objective) do not reach the joint arm.

## Unpinned sites

Each is a `custom_components/` site that `mutation-autofix` pins once CI's mutation lane records it. Each is already killed by the #3289 block (0 survivors in the diff-mutant run):
- custom_components/heatpump_optimizer/optimizer.py:158 GUARD_OFF (`_realize_draw` `if dhw is None:`): killed. `_realize_joint(None)` raises, and the block's DHW-less realization check goes red. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:160 RETURN_DEL (`_realize_draw` `return _realize_joint(...)`): killed by the clamped-realization check. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:176 GUARD_OFF (`_realize_joint` `if not clamp:`): killed (M11). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:179 RETURN_DEL (`_realize_joint` `return project_space_against(...)`): killed (M6 shape) by the clamped-realization and both per-step checks. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/thermal_model.py:1297 GUARD_OFF (`can_duty_cycle` `if self.on_off:`): killed (M1). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/thermal_model.py:1604 RETURN_DEL (`project_planned_levels` `return _onto_band(...)`): killed by the #1955 block's projection check and this block's `d = 0` identity row. Pinned by mutation-autofix.

## Red checks

- `mutation` (predicted, `ci_predict.py`): red on the 6 unpinned sites above until `mutation-autofix` commits their pins (`ci-autofix.md`); each is already killed locally. Cheaper detector: none is owed, because `prepr.sh` step 6d already predicts it in seconds before the push, and the repair is the bot's by design.

## Forward-carry

- The new option's German label: no German translation file exists at base. Owed to R10-I18N-DE's roster brief (item 9980b124), which the orchestrator writes, since a fixer seat writes no roster. Carry: R10-I18N-DE
- The docs row "Compressor runs below min power" in `docs/configuration.md` is a claim that `tests/doc_claims.py` may pin. Owed to R10-USER-DOCS-VERIFY's roster brief (item df23e57c). Carry: R10-USER-DOCS-VERIFY
- The reply on 3289 names the option: the reporter picks `on_off` unless their surface is switch plus setpoint, where the probe already clamps and only the DHW projection moves (item 052fa8fb). The orchestrator answers the issue. Carry: R10-MIN-POWER-FLOOR
- Re-read #3297's `probe_install` and `InstallCapability` at its merge. If it changes `can_duty_cycle` or `fully_metered`, revalidate the `on_off` early return and the block's checks before this merges (item df5196cc). Carry: R10-MIN-POWER-FLOOR
- After R10-GENERIC-HEAT-CURVE merges, re-measure the `option_doc_coverage.py` EXPECTED counts at the merge (+1 field from each side). `option_fields_undocumented` must stay 0 (item 3c867235). Carry: R10-MIN-POWER-FLOOR
- Per-step power beside `avg_power_kw` on the plan sensor: not built. Once steps are projected, the slot average is honest. Carry: dismissed: steps correct once projected (item f3c0e349)

## Friction

- fixer.md-step5: cost: `tools/audit/seat/cloud-setup.sh` writes `export RUNNER_TEMP=` into the `BASH_ENV` profile. Every nested `bash` therefore overwrites a caller's `RUNNER_TEMP` with a directory the host never creates. `tests/entities.py` then fails 3 workflow checks on any cloud seat, at base too, and `prepr.sh`'s closures step refuses: "failed while being recorded: tests/entities.py". Evidence: `env RUNNER_TEMP=$T bash --noprofile --norc -c 'echo $RUNNER_TEMP'` prints the profile's path; `env -u BASH_ENV` gives `ALL 2655 ENTITY CHECKS PASSED`. The fix is outside this group's files, and no live roster group owns `cloud-setup.sh` (R10-FLY-CLOUD-SETUP-TOOLCHAIN is done). The orchestrator routes it. Carry: #201
