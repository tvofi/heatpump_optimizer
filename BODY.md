R10-COMBI-TANK PR B (M; design `a605014bff4478f470853109060f4ff7ef605d4c`, approved by `design-verdict/r10-combi-tank` `56810263b`, Cost and Order section's PR B scope). Stacked on PR A, #3358 head `577c6974205926e7dbaa178b91af96a229ea02f3` (workaround ruling: outside work may stack on an unmerged base). Issue #3225 (outside user Bankaifan): a combi store, one body of heating water serving the space circuit and hot water through an exchanger, could not be configured. PR A landed the store's physics behind fields only a test could set; this PR makes it reachable by an install and closes the issue.

Closes #3225

What changes:
- **The option.** The building page gains a `combi` section: the switch, the tank type, the exchanger effectiveness, the potable volume and the legionella force. The switch is refused (`combi_needs_store`) by the model's own `combi_tank_active` predicate over what would be stored, never a copy of it. The type is the flow's pre-fill of the two numbers the model reads (`_combi_preset_fill`: a changed type writes its preset, a kept type keeps edited numbers, `custom` writes nothing); `COMBI_TANK_PRESETS` in const.py is keyed by physical construction, never by product (design §T.4). Strings in every shipped language (en, sv, de), the configuration doc's building table, and the card's setup diagram (a combi caption and the hot water pipe leaving the buffer).
- **The loader.** `ThermalParameters._tabled_values` reads the four fields from their own keys; PR A's `unwired_combi` exemption is replaced by a check that each field is reached by its own key (carry 8).
- **The seed (carry 6).** `tank_levels` and `combi_tank_seed` (coordinator.py, module level beside `_seed_store`): a combi store is one node, so both levels carry the buffer probe, else the hot water probe, else the previous plan's buffer trajectory, which is `_seed_store` over the DHW reading. Off combi each tank seeds alone, as before.
- **The learners.** The separate tank's DHW learner takes no sample of a combi store. The buffer cooling learner needs no gate: combi implies a throttling valve, under which `_async_learn_buffer_cooling` already returns (pinned by a check over every valve mode).
- **The legionella default (design §L, as the folded web report item 6 corrects it).** `ThermalParameters.legionella_cycle_active` is the flag's one behaviour read: a combi store holding at most `COMBI_LEGIONELLA_POTABLE_LIMIT_L` (3 l) of potable water runs no cycle unless `dhw_combi_legionella_force` is on; off combi it is `dhw_legionella_enabled` itself. Its nine behaviour readers moved to it (dhw_planner, legionella, setpoint_check, the coordinator's elastic block, the rating's top); diagnostics publish `dhw_legionella_cycle_active` beside the raw flag. The W 551 exemption citation is gone; the default rests on physical grounds (no potable water stands to disinfect), and the help text states W 551's delivery temperatures.
- **Setup and advisor.** `describe_setup` gains `dhw_source` (`combi` / `tank`) and the hot water edge leaves `buffer_tank` in combi; `rank_sensor_gaps` prices no hot water probe over a combi store with a buffer probe.
- **Main's de gaps, disclosed.** `de.json` and the card's de strings lacked five keys main gained from PRs that crossed #3331; `tests/entities.py`, `tests/card.mjs` and `claims.py`'s C112 were red on main's own tree for them (null control below), so `82d5ba034` filled them. Main filled the same keys independently before the handoff; the merge `baac8a0a2` resolved each conflicting hunk to main's text, so this PR's diff against main carries none of them.

Departure, disclosed: `origin/main` was merged at the start (`fa38b58c2`) although `git merge-tree` reported no conflict, because the brief's de translations need the de catalogue and `SHIPPED_LANGS`, which exist only on main (`git ls-tree origin/main custom_components/heatpump_optimizer/translations/` lists de.json; PR A's head does not). It was merged again (`baac8a0a2`) when `git merge-tree --write-tree origin/main HEAD` reported CONFLICT in de.json and the card, the de-gap keys above, and a third time (`27fa6918c`) for the merge train's skip, `## Merge resolution only`.

## Head

`1d4aec21aa0828412077708a9e74453acaef12e2`: the merge `9f2f00266` of `origin/main` `5d09dedf69eb` into the previous head `c2ba62946a8ce4a63c6ad0df3ca022c6aa299886`, then one commit deleting a stale mutation-ledger pin (`## Repair round`); `e020a1d23d87c707f2a3070e0e77a724fff4b127` merged it into the PR head with no code change. The current head is named in `## Head note` below. The mutation runs and harness figures below were taken at the earlier heads they name.

## Head note

`a1b268838ee527fa669abcaba5c97ba542b03d3c` is this PR's head: the merge of `origin/main` `b37b85c18ec8d3a2987ea169891fdcc1019cb196` into `e020a1d23d87c707f2a3070e0e77a724fff4b127`, taken because `git merge-tree --write-tree origin/main e020a1d23` reported a conflict after #3297 (`d9bec09f`, R10-HOTFIX-COP-UNMEASURED), #3401 and the merges before them. `tools/pr/prepr.sh` at this head exits 0 (`PRE-PR: a1b268838ee5... rc=0`; `MODE: SCOPED`, `STRUCTURE RATCHET PASSED`, `CI PREDICT: no closures, fast, governance or instrument red predicted against b37b85c18ec8`, `claims register ... byte-identical`). The merge changed no production file by hand; every figure below that reads 213 / 247 / 48 is the figure at `27fa6918c` and is superseded by the Resolution section.

## Resolution

The merge conflicted in four files, not one (the brief named the first). Both parents' entries are present in each result.

**1. `dev/audit/rounds/round3/D5/option_doc_coverage.py`** (EXPECTED header). Parent HEAD (this branch) carried: `R10-MIN-POWER-FLOOR ... 204 -> 205 and 237 -> 238 ... R10-COMBI-TANK (#3225) moved them 205 -> 210 and 238 -> 244` and `RESULT option_fields_rendered=213 ... option_schema_keys_rendered=247`. Parent origin/main carried: `R10-HOTFIX-COP-UNMEASURED moved them once more, 204 -> 207 and 237 -> 240: the power and thermal power meter source selects and the hot-water coverage switch ... R10-MIN-POWER-FLOOR ... 207 -> 208 and 240 -> 241` and `RESULT option_fields_rendered=211 ... option_schema_keys_rendered=244`. Kept result: main's chain (204 -> 207 -> 208 for fields, 237 -> 240 -> 241 for keys, plus its 211 / 244 heat-curve step) followed by this branch's sentence re-based on it: `R10-COMBI-TANK (#3225) moved them 211 -> 216 and 244 -> 250: the building page's combi section (one section key, five fields), each with its row`, and `RESULT option_fields_rendered=216`, `option_fields_undocumented=0`, `option_schema_keys_rendered=250`. Check: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round3/D5/option_doc_coverage.py` prints `option_fields_rendered=216`, `option_fields_undocumented=0`, `option_schema_keys_rendered=250` (main's 211/244 + this branch's 5/6).

**2. `dev/audit/rounds/round4/D6/claims.json` and `claims.md`** (C125). HEAD: `(48 selects)`, `48 selects, untranslated=[]`. origin/main: `(49 selects)`, `49 selects, untranslated=[]`. Kept result: regenerated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`, not hand-merged: C125 reads `50 selects, untranslated=[]` (main's 49 + this branch's one), C30 `97 rows` (was 94 on main), C31 `104 rows` (was 102 on main). `claims.py`'s header counts moved to `config_defaults_compared=97` and `config_ranges_compared=104` in the same regeneration; prepr's `claims register` step confirms the script rewrites both files byte-identical.

**3. `tests/golden/claimed_drift.txt`.** HEAD side: the six `R10-COMBI-TANK (#3225)` lines (`config_flow`, `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone`; additive keys). origin/main side: six `R10-HOTFIX-COP-UNMEASURED` lines for the same scenarios (`cop_watch_learning -> cop_unmeasurable`; the metering page's three leaves). The claimnotes driver refused (`CONFLICTING CLAIMS`: both rewrote the same scenarios' claims). Kept result: both sets, 12 lines, since a scenario holds a list of claims (`_parse_claims`) and the two diffs move different leaves; no text of either was changed. `claims-for: 7.1.9` unchanged. `claims hygiene: ... ok` at this head.

**Auto-merged and not conflicting:** the `tests/golden/*.json` fixtures (main's string moves and this branch's additive keys), `custom_components/**` and the translations.


## Repair round

The previous head could not be applied: merged with main, `python3 tools/pr/ci_predict.py` printed `PREDICT ledger   STALE PIN custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.dhw_hard_max_temp GUARD_OFF 07409d20: disposition names no site the inventory generates (old pin '        if self.dhw_legionella_enabled:')`. Cause: this branch rewrote the site, `dhw_hard_max_temp` now guards on `self.legionella_cycle_active`, so the old line no longer exists. The current guard already carries its own pin (`...GUARD_OFF.f3c560aa.json`, killed by tests/guard_pins.py, `--pin-killed`). Repair as ci_predict prints it: the stale pin file `tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.dhw_hard_max_temp.GUARD_OFF.07409d20.json` was deleted (`git rm`), not edited. After it, `python3 tools/pr/ci_predict.py` prints `CI PREDICT: no closures, fast, governance or instrument red predicted against 5d09dedf69eb`. Cheaper detector for the red: `ci_predict.py` itself (this branch's prior bodies already name it); process state (d), main's merge changed nothing here, the earlier pin set was stale against this branch's own rewrite once re-checked on the merged tree.

## Merge resolution only

The merge train skipped #3398 (`SKIP #3398 recarry: main does not merge without a resolution`): `git merge-tree --write-tree origin/main 249d76dd6` reported CONFLICT in the paths below. R10-GENERIC-HEAT-CURVE had landed on main, adding to the same lists as this branch. Each path was resolved against both parents (figures in this section are those at `27fa6918c`; `## Resolution` above gives the current ones):
- `strings.json`, `translations/en.json`, `de.json`, `sv.json`: both sides appended an `options.error` key (this branch `combi_needs_store`; main `heat_curve_not_offset` and `heat_curve_entity_in_use`) and a `selector` block (this branch `dhw_combi_tank_type`; main `heat_curve_target_kind`). All kept, in each language; each file parses as JSON, and `strings.json` is byte-identical to `en.json`.
- `dev/audit/rounds/round3/D5/option_doc_coverage.py` (EXPECTED header): base 205/238; this branch +5/+6, main +3/+3, giving `option_fields_rendered=213` and `option_schema_keys_rendered=247` at that merge.
- `dev/audit/rounds/round4/D6/claims.py` (EXPECTED header): base 93/101; this branch +3/+2, main +1/+1, giving `config_defaults_compared=97` and `config_ranges_compared=104`; `claims.json` and `claims.md` regenerated by it, not hand-merged.
- `tests/golden/claimed_drift.txt`: the claimnotes driver refused (both sides claimed `config_flow` for 7.1.9); kept this branch's six R10-COMBI-TANK lines and dropped main's R10-GENERIC-HEAT-CURVE `config_flow` line.
- `tests/structure_budgets.json`: resolved by the ledger driver; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- **The census base, 2 -> 4 (`c2ba62946`, `tests/features.py` `_CB_VENDOR_BASE`).** R10-GENERIC-HEAT-CURVE added two comment mentions of Luxtronik on main; `git grep -ciE 'alpha.?innotec|mfs ?[0-9]|luxtronik'` over the package's Python sums to 4 on `origin/main` `b0762725` and on that head. The base is re-recorded at main's count, and the census still refuses growth past it.

## Mutation proof

Each mutant was applied in a detached worktree at `d1975b5b7` (this branch's production as it stands: no production file differs since), the PR B block run with `tools/audit/seat/features_block.py`, and the file restored. FAIL lines are check names:
- **M1** the loader row `("dhw_combi_tank_enabled", "DHW_COMBI_TANK_ENABLED")` dropped: 11 FAIL, among them `combi loader: the option reaches the store, 504 l plus the 40 l coil, eps from the entry; null control: ...`.
- **M2** `tank_levels`' combi branch dropped: 3 FAIL (`combi seed: ...`).
- **M3** `combi_tank_seed` skips the hot water probe: FAIL `combi seed: with only the hot water probe, ...`.
- **M4** the DHW learner gate dropped: FAIL `combi: the separate tank's DHW learner takes no sample of the shared store; ...`.
- **M5** `>` to `>=`, **M6** the force term dropped, **M7** the combi condition dropped: each FAIL `legionella_potable: ...`.
- **M8** `dhw_hard_max_temp` reads the raw flag: FAIL `legionella_potable: the rating follows the gate: ...`.
- **M9** legionella.py's first reader back on the raw flag: FAIL `combi_legionella_gate census: ...`.
- **M10**, **M11**: each FAIL `combi setup: ...`. **M12** the advisor's combi zero dropped: FAIL `combi advisor: ...`. **M13** the pre-fill on a kept type: FAIL `combi pre-fill: ...`. **M14** a preset slug literal planted in dhw_planner.py: FAIL `combi_type_branch census: ...`.
- **M15** the `combi_needs_store` refusal dropped, `tests/config_flow_steps.py`: `1 of 551 checks FAILED`; restored, `ALL 551 checks PASSED`.

Failing first: this head's `tests/features.py` against the production of `fa38b58c2`: rc 1, `AttributeError: module 'heatpump_optimizer.const' has no attribute 'CONF_DHW_COMBI_TANK_ENABLED'`.

## Null control

- **Option off, every plan:** `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`, every claim additive; no plan, schedule or trajectory leaf moves. `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. At the merge head `a1b268838`: the same two lines against `b37b85c18ec8`.
- **Option off, the loader:** `ThermalParameters.from_config` of the issue's mapping without the switch equals the same mapping with the switch False, field for field.
- **Off combi, every feature:** the seed, the learner (two samples, 48.0 each), `legionella_cycle_active` off combi at 0 l (True), the setup (`tank`), the advisor each keep their prior reading.
- **The census reaches:** `combi_legionella_gate` sees the one diagnostics read in `_dhw_view`; `combi_type_branch` sees the table's own slugs in const.py.
- **Main's de gaps:** at `fa38b58c2` `tests/entities.py` printed `3 of 2707 ENTITY CHECKS FAILED`; at `baac8a0a2` `ALL 2707 ENTITY CHECKS PASSED`.
- **Exchange accounting (carry 9):** `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327` at this PR as at PR A.

## Unpinned sites

`python3 tools/pr/ci_predict.py` at `8b3e7051c` listed 19 sites this diff adds and 10 STALE PINs; the ten pin files were deleted as it instructs (`cd301a215`). Three `tests/mutation_table.py --pin-killed --base origin/main` runs pinned all 19; each is **pinned**: `config_flow.py` (8 sites) killed by tests/config_flow_steps.py; `coordinator.py` (4), `legionella.py` (3), `setpoint_check.py:119`, `thermal_model.py:329` killed by tests/features.py; `thermal_model.py:906 GUARD_OFF` killed by tests/guard_pins.py. `legionella.py:523 BOOLOP` survived the second run; `927975fcc` adds the input (`...but a combi store with no potable water runs no cycle and gets no card`) and the third run pinned it, killed by tests/features.py.

## Figures

- Scope at `a1b268838` (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`): `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`
- Gate at `a1b268838`, Linux x86_64 (`GATE_SCOPE=auto GATE_SCOPE_BASE=$(git merge-base origin/main HEAD) GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub bash tests/run.sh`): `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN`, with `ALL 116 STRESS CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED`, `ALL CARD CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against b37b85c18ec8`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- `tools/pr/prepr.sh` at `a1b268838`: exit 0, `CI PREDICT: no closures, fast, governance or instrument red predicted against b37b85c18ec8`, `STRUCTURE RATCHET PASSED`.
- Harness headers at `a1b268838`: `option_doc_coverage.py` prints `option_fields_rendered=216`, `option_fields_undocumented=0`, `option_schema_keys_rendered=250`; `claims.py` regenerates `claims.json`/`claims.md` byte-identical.
- Architecture score, at `27fa6918c`: `Architecture score: dS +0.0006 IMPROVES`.
- Typing, at `27fa6918c`: mypy --strict exits 0.
- Harness `dev/audit/harnesses/r10_combi_tank.py`, sha1 `e47dc605d1d95abd50b796d52730bd3394c36702`, `exchange` arm at `d1975b5b7`: `exchange_dhw_kwh=22.135`, `null_dhw_kwh=5.327`.
- Vendor names: `git grep -ciE 'alpha.?innotec|mfs ?[0-9]|luxtronik' origin/main -- 'custom_components/heatpump_optimizer/*.py'` sums to 4, the base the `combi_type_branch` census refuses growth past.

## Red checks

INHERITED from PR A (#3358), whose commits this branch stacks on: `tests / fast (3.14)` stress over 1.05x on four valve scenarios (fixed on #3358, green here: `ALL 116 STRESS CHECKS PASSED`); `tests / mutation` unpinned sites PR A added (pinned or triaged there; cheaper detector `prepr.sh` step 6d / `ci_predict.py`). No CI check has run on a commit this branch adds. At `a1b268838` the scoped gate on Linux passed every script; the five host reds recorded at `27fa6918c` (arm64 optimality reading, node OOM, mypy pin, entities timing, features census fixed by `c2ba62946`) do not reproduce.

## Forward-carry

- Carry 4 (web verification before PR B): applied as the folded report states. Carry: dismissed: built in this pull request
- Carries 7 and 11, the `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` trailer: landed on `c2cb6262d`. Carry: dismissed: landed in this pull request
- Carry 8 (unwired-combi-set): `unwired_combi` is gone, replaced by a per-field reachability check. Carry: dismissed: built in this pull request
- Carry 9 (exchange-accounting): docs/configuration.md says the hot water energy sensor includes heat the heating later draws from the shared tank. Carry: dismissed: built in this pull request
- Carry 10 (exo-seed-census-only): no planner stage changes here. Carry: dismissed: nothing in this diff touches the planner's stages
- The advisor's hot water probe price for a combi store without a buffer probe still sizes its band from `dhw_tank_volume`. Carry: dismissed: an order-of-magnitude advisor estimate whose only effect is the rank of one probe suggestion

## Friction

none
