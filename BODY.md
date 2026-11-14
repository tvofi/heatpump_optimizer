R10-CONFIG-FLOW-TEXT-VERIFY (production, user-facing text; the owner's instruction of 2026-11-13). Every config- and options-flow string that states behaviour was judged against the code that decides it, at merge base 154dbb4c61652135381ce66646d23f7109d1c142. The false and stale ones now say what the integration does, in strings.json and the same keys in en, sv and de. The figures the corrected sentences quote are pinned to their constants, and a "never writes" sentence on a slot the pump arbiter writes is refused.

**Enumerator.** `python3 dev/audit/rounds/round10/D6/flow_claims.py enumerate` walks the `config`, `options` and `selector` trees of strings.json and of every file under translations/, and prints one line per leaf (step titles, descriptions, field labels, data_description, errors, aborts, menu options and selector option labels), then a count line per catalogue. The flows render no other top-level key. `distinct` prints the claim set: distinct English texts of 40 characters or more. Each claim set row has one verdict in the record.

**Record.** `dev/audit/rounds/round10/D6/flow-claims.json`, rendered to `flow-claims.md` by `flow_claims.py render`. It uses the method of round 4's D6 record (`dev/audit/rounds/round4/D6/claims.md`, which #3513 re-truthed): key, claim, evidence `path:line` at the merge base, verdict (true, false, stale, unverifiable, no-claim), and the correction. Each row was judged twice: a first pass over six batches, then an adversarial re-check of every false and stale row that also re-checked the correction against the code. That re-check refuted two rows (`confidence_margins_enabled`, `silent_mode_power_fraction`). Before handoff I refuted a third, `curve_learning_enabled`: its "six tenths of a degree per week" is the measured worst case (D6-s2-03, b1024f9ef3), not `MAX_DOWN_PER_WEEK`. It stays as shipped and is now pinned to its derivation.

**What changed for a user, by kind.** These lines name the corrections. Every correction is in the record.
- What is written to the pump. `pump_duty_mode` now says: Off and Observe write no mode or set-point, but the heat pump on/off switch is still switched by the plan; a step that plans both duties is split, hot water only and then heating; Heating + DHW applies only while a boost or an anti-legionella cycle calls for both, or the plan is not in charge; on heating steps the flow set-point follows the planned level up to the Heating flow ceiling, not "the entity maximum"; Control also holds the Capacity limited (night mode) switch. `space_setpoint_unit` no longer says "this integration never recommends a space set-point". `options.step.entities.description` no longer says the page only holds entities the optimizer reads.
- Behaviour claims the code contradicts. The entry name; target, minimum and maximum temperature; emitter, thermal-mass and slab-transfer help; buffer-tank volume; hot water set-point; solar radiation sensor; quick setup; the wood tank probes; the device pre-fill page; valve settings in single-zone; the 15 K / 75 °C supply offset bound; compressor cycling cost; questionnaire size; two-zone fields; PV production sensor; away legionella timing; learning defaults; the heat pump energy meter; free disinfection; legionella minimum interval; the VVC pump; main fuse 0; DSO products; grid fee mode and fixed fee; open-window relaxation; the Modbus pre-fill page.
- Left alone: `space_setpoint_entity`'s "Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point." R10-HOTFIX-FLOW-SETPOINT-STUCK corrects that sentence and its translations (this group's brief). The record marks the row stale and names that owner.

sv and de are translations of the corrected English: unchanged sentences are kept verbatim, and UI labels are taken from the same catalogue's own label for that key. en.json stays a leaf-for-leaf copy of strings.json.

**Pinned against prose-only.** `check_flow_text_claims` in tests/doc_claims.py has two pin families.
1. 19 figure pins. Each pin is a sentence regex plus the production symbol, read by import:
   - pump_duty_mode: `LEASE_MINUTES`, `COLD_LEASE_MINUTES`, `COLD_RAIL_C`, `RETRY_MINUTES`, `SPLIT_MIN_MINUTES`, `FLOW_HEAT_C`, `FLOW_HOLD_C`, `FLOW_GATE_C`, `DHW_GATE_C` and `thermal_model.FLOW_MIN_LIFT_K`;
   - curve learning: `STEP_K * ceil(7 / DAYS_PER_STEP)`;
   - `CONFIDENCE_MARGIN_CAP_C`;
   - `FLOW_BIAS_CLAMP_K` and `FLOW_SUPPLY_MAX_C`;
   - `DHW_LEGIONELLA_HOLD_MINUTES`;
   - `ECONOMY_MIN_TEMP_WIDENING`, `OPEN_WINDOW_RELAX_C` (twice) and `ECONOMY_ABSOLUTE_FLOOR`.
2. Written slots. The written-slot set is derived from `pump_arbiter._entities`, not hand-listed: each `CONF_*_ENTITY` key is fed a value naming itself, and the check reads which key each slot took. Any data_description on a slot key, or on a key named after one, that says "never writes / never recommends / used only to notice / read only" must name Control.

Every other row is prose-only: physical advice, tariff facts, and behaviour with no single constant, such as the 0.5 K night floor literal in `get_temp_bounds` and the pre-fill register addresses.

Translations stay key-complete under tests/entities.py, "{sv,de,en}.json has exactly strings.json's keys" and "en.json equals strings.json leaf for leaf". Both are in the scoped run below.

**The hotfix's sentence.** `_OWNED_ELSEWHERE` exempts exactly that one shipped false sentence, keyed on its full text. When the hotfix changes the text, the exemption stops matching and the key is judged like every other. Neither merge order goes red, and the exemption can be deleted after the hotfix lands. A dedicated null control proves the sentence is still caught with the exemption removed. This is a design choice, recorded here so the reviewer can judge it under fixer.md step 14. The alternatives were a red head until the hotfix lands, or a BLOCKED stop; neither handoff ref existed at the time of this run (`git ls-remote origin` showed no `r10-hotfix-flow-setpoint-stuck` ref).

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

**Outside the flows.** False claims outside the two flows, found by a sweep of README.md, docs/, services.yaml, the non-flow catalogue sections, blueprints/ and code docstrings for each corrected claim. None misleads a user about what the integration writes to their pump: docs/configuration.md's pump-duty section already describes the split and the boost rows correctly. Each is listed under Forward-carry.

## Head

6ebbd4e56aea37f2ffd583e488f74adb6e8bb67a: the reviewed head 8c9dc2697a74ebb036f4dddb8557edd57664d8bd, plus a clean merge of origin/main and the pin repoint (59bb0506a003221fe2af38f30ab20fac46d1b73d), plus this round's merge of origin/main 50373173d486faf394b24637c177ab38b691b394 (pull request 3531 merged as 7aac3e7c). Measured 2026-11-13T23:59Z.

**Main-conflict merge, file by file.** `git merge-tree --write-tree origin/main 59bb0506` conflicted in four files: strings.json and translations/en.json, de.json and sv.json. In each one the conflict covered adjacent lines only. Main added `space_hysteresis_entity` and `dhw_hysteresis_entity` (label and data_description) under `options.step.entities_pump` and the `dhw_minimum_above_start` issue. The branch rewrote `pump_duty_mode` and the other corrected texts. Resolution: the branch's line is kept, and main's added keys are kept beside it. Main's copy of `pump_duty_mode` is the merge base's text, so it is dropped. Proof: a key-level three-way JSON merge (base, branch, main) found no leaf changed on both sides. The merged file parses equal to that merge, leaf for leaf and in key order, in all four files. `git diff --numstat 59bb0506 HEAD` adds 8 lines and removes 0 per file: main's new leaves. `git diff --numstat origin/main HEAD` gives +56/-56 for strings, en and de and +55/-55 for sv, the branch's own corrections unchanged. tests/closures.json merged automatically through the ledger merge driver. No other file conflicted.

**Main's new texts are outside this record.** The two hysteresis data_description texts are main's and were added after this group's merge base. They raise the claim set to 372 but have no row in flow-claims.json, whose record is judged at merge base 154dbb4c.

**Repair round.** Main's R10-DUTY-SWITCH-PLANNER-PRICE moved `SPLIT_MIN_MINUTES` from pump_arbiter to duty_legs, so `flow_number_pins` raised AttributeError; the one pin now reads `duty_legs.SPLIT_MIN_MINUTES` and no other claim changed. After the repoint `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 354 checks PASSED`; with `SPLIT_MIN_MINUTES = 6.0` in duty_legs it printed `FAIL every quoted figure in the flow help (19 pins) is its constant's value  [options.step.entities_pump.data_description.pump_duty_mode: quotes 5, the code holds 6.0]` and `1 of 354 checks FAILED`; restored, rc 0 (null control).

## Mutation proof

These mutations were run in a scratch worktree at the head, editing strings.json only, then running `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`.
- Restoring `space_setpoint_unit`'s pre-fix text (the merge base's) gives `FAIL no flow help says a slot the arbiter writes is never written, unless it names Control  [options.step.entities.sections.indoor.data_description.space_setpoint_unit]`.
- Changing "capped at 90 minutes" to 60 gives `FAIL every quoted figure in the flow help (19 pins) is its constant's value  [options.step.entities_pump.data_description.pump_duty_mode: quotes 60, the code holds 90.0]`.
- Total: `2 of 354 checks FAILED`. With the mutations restored, the run is green.

No production Python was added. `mutant_run.py --diff` draws only added `.py` lines outside `tests/` and `dev/`, and this diff has none.

## Null control

- **Merge base.** The same arm runs against the merge base's strings.json (`git checkout 154dbb4c -- custom_components/heatpump_optimizer/strings.json` in the scratch worktree). Both families go red: the figure pins with `no sentence matches 'a share under (\d+) minutes'` and the rest, and the written-slot arm listing `space_setpoint_entity` and `space_setpoint_unit`. The arm reads the defect at the base and not at the head.
- **Built-in controls.** The arm carries three of its own:
  1. a pump-duty text quoting 60 minutes is found;
  2. the pre-fix `space_setpoint_unit` sentence planted in a copy is found;
  3. the hotfix's sentence is found once the exemption is removed.
- **Method control (brief item 5).** A false sentence planted in a scratch copy, the pre-fix "The unit is a declaration: this integration never recommends a space set-point.", is flagged by name. The second-pass review refuted three first-pass verdicts, which shows the review procedure can return "true" as well as "false".

## Figures

- Flow strings per catalogue (1078 each for strings, en, sv and de at this head; the 4 above 1074 are main's two hysteresis keys' label and help): `python3 dev/audit/rounds/round10/D6/flow_claims.py enumerate | tail -4`.
- Claim set (369 distinct English texts of 40+ characters at the merge base; 370 at the reviewed head, because the config copy of `after_save` now differs from its options copies; 372 at this head, adding main's two hysteresis help texts): `python3 dev/audit/rounds/round10/D6/flow_claims.py distinct | tail -1`.
- Verdict counts (true 286, false 27, stale 12, unverifiable 4, no-claim 40): `python3 -c "import json; print(json.load(open('dev/audit/rounds/round10/D6/flow-claims.json'))['verdicts'])"`.
- Keys corrected per catalogue (56): `git diff --stat origin/main...HEAD -- custom_components/heatpump_optimizer/strings.json custom_components/heatpump_optimizer/translations/`. That prints 112 changed lines per catalogue, one removed and one added per key; sv prints 110, because sv's `grid_fee_mode` translation already used the label the corrected English names.
- Scoped gate, `MODE: SCOPED -- 11 script(s) run, 22 scoped out` from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` at this head. Each script `scope.run` names was run with `PYTHONPATH=tests/hastub` and exited 0. tests/doc_claims.py: `ALL 354 checks PASSED`. tests/entities.py: `ALL 2711 ENTITY CHECKS PASSED`. tests/config_flow_steps.py: `ALL 586 checks PASSED`. tests/features.py: `ALL 5571 FEATURE CHECKS PASSED`. tests/harness_headers.py: `ALL 115 HARNESS HEADER CHECKS PASSED`. `GOLDEN_MODE=drift python3 tests/golden.py`: `NO STALE FIXTURE`. `node tests/card.mjs`: `ALL CARD CHECKS PASSED`. env_drift, deployment_shape, plan_view and arch_score_head passed too.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `git merge-tree --write-tree origin/main HEAD` prints one tree.

## Red checks

- `tests / fast (3.14)`: red on this pull request's earlier head 67ab6ad0 (run 43505062003, job 132161223217; the log ends `1 TEST SCRIPT(S) FAILED`, and its wall-clock table lists `11s  python3 tests/doc_claims.py`). The log API's tail did not reach the traceback, so the cause below is the reproduction of that job's script at 67ab6ad0, not a line read from the log: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at that head dies in `check_flow_text_claims` -> `flow_number_pins` (tests/doc_claims.py:4739) with `AttributeError: module 'heatpump_optimizer.pump_arbiter' has no attribute 'SPLIT_MIN_MINUTES'`. `SPLIT_MIN_MINUTES` is defined at duty_legs.py:33 at that head; main's R10-DUTY-SWITCH-PLANNER-PRICE moved it from pump_arbiter, and the pin still read the old module. It is fixed at 59bb0506: the pin reads `duty_legs.SPLIT_MIN_MINUTES`, and the script prints `ALL 354 checks PASSED` (see Repair round).
- Root cause. The pin was written against a main that still held the constant in pump_arbiter, and the merge of the newer main carried a rename the pin could not see. Nothing in the branch changed, so no earlier gate in the seat's session could fire.
- Cheaper detector. It exists and costs almost nothing: the same script, `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`, run after merging origin/main into the branch. It took 17 s wall (12 s user) here at the failed head and printed the AttributeError above; the CI job logged 11 s for it. The `tests / fast (3.14)` job took 1525 s in total, so the local run is about 1% of it. Standing cost: one extra 17 s run after any merge of main on a branch that touches a pin file. The fixer's contract already runs `tools/pr/prepr.sh` at handoff, and the train re-proves the head on the current main; a merge by the orchestrator's script after that run is the gap this red fell through, and a detector run by the seat cannot close it. No new countermeasure is proposed for the one-off; the cause is recorded here.
- `pr-contract / pr-contract`: red at 67ab6ad0 (job 132175875810). Its body check printed ``check `tests / fast (3.14)` is red and `## Red checks` does not name it``. That body said `none` under Red checks. This body answers it in the item above. Cheaper detector: `tools/pr/prepr.sh` runs the same `policy_lint.mjs --pr-body` check offline at handoff, in seconds. It could not fire then, because the red came after the handoff, and nothing cheaper exists for a red that arrives later. No countermeasure.

## Forward-carry

- docs/configuration.md:530, docs/how-it-works.md:924 and the away.py module docstring say the anti-legionella cycle is timed to finish before the user returns. `AwayConfig.legionella_before_return` is never read. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1063 and docs/how-it-works.md:648 say the VVC loop pump runs only during the hot-water frames. With no frames, `pump_schedule.vvc_should_run` keeps it on. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1049 and docs/how-it-works.md:620 describe free disinfection as an opt-in credit. Any source is credited either way; the option adds the 20-minute hold. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1102 says the open-window option lowers the target. It lowers the coldest acceptable temperature. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1115 says main fuse 0 keeps the headroom sensor dormant. The sensor follows the capacity-tariff peak. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1079 says the PV forecast corrects itself. Only the current step is replaced. Carry: R11-INTAKE-R10-RESIDUE
- docs/setup.md:91 says the entry name is shown in front of every entity. Entities use the fixed device name. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:155 says valve settings work only in two-zone. Only a Flow temperature write target needs it. Carry: R11-INTAKE-R10-RESIDUE
- docs/how-it-works.md:822 says the planned start count is published. No sensor carries it. Carry: R11-INTAKE-R10-RESIDUE
- docs/configuration.md:1083 does not say the price estimate is on by default. Carry: R11-INTAKE-R10-RESIDUE
- custom_components/heatpump_optimizer/setpoint_check.py:6 has the docstring "Space set-point is never recommended.", stale under Control. Carry: R11-INTAKE-R10-RESIDUE
- custom_components/heatpump_optimizer/presets.py:11 has a docstring saying "three answerable" questions; the questionnaire has six. Carry: R11-INTAKE-R10-RESIDUE
- custom_components/heatpump_optimizer/config_flow.py, setup step `device_prefill`: the second form renders `after_save` and `self._data.update(saved)` probably stores it into entry data, a stray key. The help text now says the choice has no effect there. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
