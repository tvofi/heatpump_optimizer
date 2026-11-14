R10-DOCS-STRINGS-RESIDUE part 2 of 2: carries 5 to 13 (user-facing strings and docs sentences), built on part 1's head c79e44e2e6. Each sentence is corrected to the code line that decides the behaviour (never a comment or docstring), and each correction is pinned by the new `check_docs_strings_residue` arm of `tests/doc_claims.py`, which takes the fact from the producing code, requires the corrected sentence to state it, and refuses the old wording in the reader corpus and in all four string files (strings.json, en, de, sv).

Carry 0, Carry 1, Carry 2, Carry 3 and Carry 4 are part 1's, handed off at handoff/r10-docs-strings-residue c79e44e2e6 (in review; its body carries their evidence). This part is built on that head and changes none of their text: `git diff c79e44e2e6 HEAD` touches no line part 1 changed.

Carry 5 (4ab03548): docs/configuration.md (the open-window row) and the `open_window_relax_enabled` description in strings.json, en, de and sv said the option lowers the target. They now say it lowers the coldest temperature the plan accepts by 1 °C, never below 15 °C. Evidence: `Coordinator._floor_widening` adds `OPEN_WINDOW_RELAX_C` (const.py, 1.0) when `_vent_cusum.tripped and open_window_relax_enabled`, and `away.solve_bands` applies it as `config["min_temp"] = max(ECONOMY_ABSOLUTE_FLOOR, config["min_temp"] - by)` (`ECONOMY_ABSOLUTE_FLOOR` 15.0); `target_temp` is not touched. The pin drives `solve_bands` itself.

Carry 6 (af528396): docs/configuration.md (Main fuse size) and the `main_fuse_amperes` description in strings.json, en, de and sv said fuse 0 keeps the headroom sensor dormant. They now say the fuse advisor and fuse guard stay dormant while the headroom sensor follows the capacity-tariff peak alone, unavailable without a capacity tariff. Evidence: `EntryConfig.fuse_kw` answers None at 0 A; `Coordinator._power_headroom` drops a None fuse from `limits`, takes the capacity threshold when it is finite, answers 0.0 in a billed window with no peak yet, and returns `{"available": False}` only when no capacity term bills the window.

Carry 7 (31878861): docs/configuration.md (Solar production sensor) and the `pv_production_entity` description in strings.json, en, de and sv said the forecast corrects itself. They now say the sensor replaces the forecast's current step, capped at the installed capacity, and later steps stay modelled. Evidence: coordinator.py `production[0] = min(self._pv_production, config.peak_kw)` is the only write of the measurement into the forecast.

Carry 8 (734b6d33): docs/setup.md:91, plus the same sentence in docs/configuration.md's first-screen table and the `config.step.user` name description in strings.json, en, de and sv, said the entry name is shown in front of every entity. They now say it is the entry's title under Devices & services, and entities use the fixed device name, Heat Pump Optimizer. Evidence: `Coordinator.device_info` builds `DeviceInfo(..., name="Heat Pump Optimizer", ...)` with `_attr_has_entity_name = True` (entity.py); the name answer is used only as the entry title (config_flow.py, `title=self._data.get(CONF_NAME, ...)`).

Carry 9 (753b6610): docs/dashboard-card.md (Savings receipt) said the savings figure compares spot cost only. It now says the plan and the thermostat baseline are both priced at spot plus the per-kWh grid fee. Evidence: `MonthlyLedger.observe_spot_and_settle_savings` passes `spot=spot + fee_per_kwh` to `add_savings_settlement`, which books both `savings_baseline` and the actual line at that price. The card's own `receipt.covers` string is corrected by #3563 (R10-USER-TEXT-VERIFY-CARD, open); the doc sentence states the pricing rather than quoting the note, so it is true on either side of that merge.

Carry 10 (f14f17f5): docs/dashboard-card.md (Advisor page) said the replay uses the install's measured delivery. It now says the mean electrical power the heat pump has measured where there is history, half its configured maximum otherwise. Evidence: topology.py `power = sum(samples) / len(samples) if samples else params.max_electrical_power * _ADVISOR_DUTY_FRACTION` (`_ADVISOR_DUTY_FRACTION` 0.5), fed to `_advisor_replay`.

Carry 11 (c7e69450): docs/dashboard-card.md's Health picture alt text, and the Health prose's learning list (savings "the first settled month", the same claim in a wrapped line the carry's grep misses), now say the first month with a booked saving. Evidence: #3563's correction table: the savings sensor is available once any month, the open one included, has booked `savings_baseline`. The committed health PNGs at this head still show the card's old string; #3563 re-takes them with the new one, so this alt text matches the picture once #3563 lands and is ahead of it until then.

Carry 12 (a0e752f6): not built here. Re-measured at this head (`plan_view.py`, then `HPO_PAGES_OUT=<dir> node tests/card_browser.mjs`, `cmp` against docs/img/card): health-light and health-dark are byte-identical (the renderer's control), but advisor, savings and setup all differ, and savings and setup are not claimed stale, so this host cannot tell a stale picture from its own rendering. The re-take needs the host that recorded them. Carry: R11-INTAKE-R10-RESIDUE (items a0e752f6)

Carry 13 (3bbcabdc): de.json's `grid` options page was titled "Netz-Spitzentarif" under the menu entry "Lastspitzentarif des Netzes". Each de options page now carries the name of the menu entry a user clicks: the census found three more, all de: `modbus_prefill` ("Wärmepumpen-Gerät" to "Wärmepumpengerät"), `thermal_model` ("(Experte)" to "(Experten)", and the building-preset text that names that page) and `solar_pv` ("Solaranlage" to "Solarmodule"). The pin is a census over every options menu entry whose page has a title, in all four files. Design choice: the options flow only, because its menu entries name the page they open, while the config flow's are actions ("Continue setup") and legitimately differ.

## Head

3047b48a3e7ceb9731d43d1a8ff040d8727bf3d4, measured against origin/main 50373173d486faf394b24637c177ab38b691b394 at 2026-11-13T23:29Z. Merge base e23124ff6e45bac1d48b4a775dad555a37965355; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged.

## Mutation proof

Text-only diff, so each mutant changes the production line that decides a corrected sentence and runs `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`; unmutated: `ALL 380 checks PASSED`. Each was applied as one exact string replacement and restored, then `git diff --quiet` passed.

- M1 away.py `solve_bands`: widen `config["target_temp"]` instead of `config["min_temp"]`: `FAIL solve_bands lowers min_temp by OPEN_WINDOW_RELAX_C and leaves target_temp`.
- M2 away.py: drop `max(ECONOMY_ABSOLUTE_FLOOR, ...)`: `FAIL solve_bands never takes min_temp below ECONOMY_ABSOLUTE_FLOOR`.
- M3 entry_config.py `fuse_kw`: `amps > 0` to `amps >= 0`: `FAIL EntryConfig.fuse_kw answers None at main fuse 0, and a capacity at 16 A (control)`.
- M4 coordinator.py: `production[0] = min(...)` to `production[:] = min(...)`: `FAIL the coordinator replaces production[0] alone, capped at peak_kw (anchor)`.
- M5 coordinator.py `device_info`: `name="Heat Pump Optimizer"` to `name=self.entry.title`: the anchor FAIL and the three fixed-device-name FAILs (setup.md, configuration.md, the name option text).
- M6 ledger.py: `spot=spot + fee_per_kwh` to `spot=spot`: `FAIL observe_spot_and_settle_savings prices the settlement at spot + fee_per_kwh (anchor)`.
- M7 topology.py: `_ADVISOR_DUTY_FRACTION` 0.5 to 0.6: `FAIL _ADVISOR_DUTY_FRACTION is a fraction the page can name` and the dashboard-card replay FAIL.

Pin on old text: the new arm run with this diff's custom_components and docs stashed (`git stash push -- custom_components docs`) prints `14 of 380 checks FAILED`: the old-wording refusal (carries 5 to 11), the eleven corrected-sentence checks and the de census (grid, modbus_prefill); restored, `ALL 380 checks PASSED`.

## Null control

Each refused wording, put back into a one-document corpus, is refused (seven `the old wording, put back, is refused (null control)` checks), and a de grid title set back to "Netz-Spitzentarif" is refused by the census; all pass in the arm. The census compares 25 pairs per file (the count it prints) and requires more than 0, so a renamed menu key cannot make it vacuous.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`: `ALL 380 checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2711 ENTITY CHECKS PASSED` (its first run failed `de.json points the derivation at the page it actually overwrites`, fixed by the second commit).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/env_drift.py --all e23124ff6e45bac1d48b4a775dad555a37965355`: `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`. Against origin/main it reports `DRIFT config_flow`: the `dhw_hysteresis_entity` / `space_hysteresis_entity` leaves main added after this base, present on main's side only; this diff adds none.
- Scoped gate (`GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`, at d0963ece7f, before the second commit): `MODE: SCOPED`, 2 failed: `tests/entities.py` (the de cross-reference above, fixed and re-run green) and `tests/env_drift.py --all origin/main` (main's config_flow drift above; green against the merge base).
- Seam enumeration (fixer step 8): `git grep -n -i -E "lowers the (heating )?target by|headroom sensor dormant|correct itself against|in front of every|spot cost only|measured delivery|first settled month|Heizziel um|värmemålet med|utrymmessensorn vilande|Reserve inaktiv|vorangestellt|Visas framför" -- ':!dev/' ':!tests/golden' ':!*.png'` at c79e44e2: every docs and string-file hit is closed in this diff; the card JS hits (`health.learn_savings_why`, `advisor.basis_*`, `receipt.covers`) are #3563's own corrections (R10-USER-TEXT-VERIFY-CARD); tests/card.mjs hits pin that card text and move with #3563; topology.py's comment on the advisor's `basis` says the history arm replays "measured delivery" where the code averages measured electrical power: comment-only, in a file outside this group's set, read by no user. Carry: dismissed: a code comment no user reads; the docs and card sentences are corrected (carry 10, #3563).
- Menu/title census rule (`jq` over `.options.step`: each `menu_options` key whose page has a `title` unequal to the label), at c79e44e2: de mismatches `grid`, `modbus_prefill`, `thermal_model`, `solar_pv`; strings, en, sv none. At the head: none in all four.

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=3047b48a3e7ceb9731d43d1a8ff040d8727bf3d4 -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Carry 12's re-take of docs/img/card/advisor-*.png on the recording host, with the re-measure above, lands in `dev/programme/rosters/wave-r10-groups.json` (group R11-INTAKE-R10-RESIDUE, branch handoff/audit-r10-roster; the relay folds it). Carry: R11-INTAKE-R10-RESIDUE (items a0e752f6)

## Friction

none
