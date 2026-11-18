# D4-s2 finder report (re-run): round 11, D4.M2 (config flow and blueprints)

The re-run closes every item the orchestrator asked for. It found one more bug, so there are now two, both low severity. Step D4.M2 covers 14 of its 15 files. The 15th is the card JS, which stays with M1/M3 as you asked. Both items handed over from round 10 (C1, C2) are now examined.

**Report JSON (updated in place):** `~/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D4/s2/REPORT.json`
**Findings:** `.../dev/audit/rounds/round11/D4/s2/findings/D4-s2-01.json`, `.../D4-s2-02.json`

**Harnesses**, all under `.../dev/audit/rounds/round11/D4/s2/`:
- From the first run: `flow_pages.py`, `flow_errors.py`, `blueprint_inputs.py`
- New in this run: `flow_validators.py`, `flow_paths.py`, `services_icons.py`

No commits, no pushes and no GitHub calls. Exposure is empty. The scratch directory is `~/hpo-orch/r10s6/r11/scratch/D4-s2`. Every number is a count, so the box load (load1 between 67 and 168) does not affect it.

## Findings

**D4-s2-01 (low, bug): the setup wizard's device pre-fill page shows window errors with an unfilled `{min_window_minutes}`.**
- **Cause:** `HeatPumpOptimizerConfigFlow._device_prefill_form` does not pass `_WINDOW_PLACEHOLDERS`. The options flow's `_prefill_form` does.
- **Number:** 8 placeholder-and-language pairs left unfilled (2 errors × 4 language files).
- **Controls:** 7 sibling cells leave 0 unfilled.
- **Perturbation:** `--perturb` adds the placeholders to the wizard's form and the count drops to 0.

**D4-s2-02 (low, bug, new in this run): the German message for `run_optimization_no_prices` uses `{entry_id}`, but the raise passes `{entry_ids}`.**
- **Where:** `translations/de.json`, `exceptions.run_optimization_no_prices.message`. A German user who calls `run_optimization` with too few price steps gets a message whose entry name is never filled in.
- **Number:** 1 placeholder mismatch among the 4533 translated strings compared with `strings.json`, and 1 raise site in `services.py` missing a placeholder its message reads.
- **Control:** the English and Swedish strings for the same key match.
- **Perturbation:** `--perturb-fix-de` renames the placeholder in memory and both counts drop to 0.
- **Fix:** rename it in `de.json`, and add this placeholder-match check to the gate's translation tests.

## Re-run items
| Item | Command | Result |
|---|---|---|
| Every remaining validator branch | `flow_validators.py` | 29 of 29 cells fire through the real step handlers. Every returned key has a string in its section in all 4 files, with 0 placeholders left unfilled. `--perturb` (comfort-band check disabled) drops the fired count to 22. |
| Wrong-kind value in every numeric option | `flow_validators.py` | "21 °C" and "abc" typed into all 131 numeric fields (262 submits): 0 accepted. |
| Reconfigure rendered with a stub entry | `flow_validators.py` | It opens the user page: 5 fields, all labelled in every language. |
| Step counts and what a user must know | `flow_paths.py` | Full wizard: 10 pages (8 forms, 2 menus). The only value a user must supply is the weather entity, a picker. The 3 technical fields are the heat-pump power and COP figures on `building_extras`. Quick setup: 7 pages (5 forms, 2 menus), same single required value, no technical fields. The perturbation cuts the quick path to 4 pages. |
| I1 rubric, page by page | `flow_paths.py` | The rubric is written in the harness header and scored over 37 forms (below). |
| `services.yaml` and `icons.json` | `services_icons.py` | 15 services and 87 fields, all named and described in every language. Every service has an icon and there are no orphan icons. All 24 raised exception keys have messages in every language. This check found D4-s2-02. |

The comfort-band cells cover all five checks: target above minimum, below maximum, night above day, empty day window and comfort outside the band. The other branches are:
- power and part-load (×4)
- the four `heat_curve_*` checks
- combi tank, flow target and flow-curve lift
- frequency control and disinfection control
- the per-day selector, holiday windows and `dhw_min` (×2)
- peak months and peak hours
- silent-mode windows
- price entity and Tibber token

**I1 rubric results:**
- **No field claimed by two pages:** the only key that appears on more than one topic page is `after_save`, the save-then-close control every options page carries by design.
- **Related fields kept together:** 8 places where fields of one family are separated by another field. I reviewed each and judged all 8 deliberate. Examples:
  - the upper- and lower-floor fields alternate as pairs on the zones page;
  - the price source is followed by each source's own field;
  - `compressor_modulation` sits inside the heat-pump power band.

**Wood slots** are not part of the config flow. `invalid_wood_slots` is an error code returned in a service's response data, not a translated message, so it is not a UI string.

## Carried from the first run
- 0 unlabelled fields (328 fields × 4 language files).
- 0 technical-term fields missing help text (125 fields).
- 0 error keys missing a string.
- 0 unfilled placeholders on the untouched pages.
- The shortest setup path is 4 pages.
- 0 gaps in the 26 blueprint inputs.

## Coverage, D4.M2
- **Universe:** 15 files. **Examined:** 14.
- **Not reached:** `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`. The M2 method has nothing to apply to it, so it stays with M1/M3.
- **Handed over from round 10:** C1 examined, C2 examined.

## Unfinished and limits, D4.M2
- The card JS stays with M1/M3, as above.
- There is no Home Assistant frontend here, so how the pages render is inferred from the schemas and strings through the test stub.
- The wrong-kind result depends on the stub's number selector, which copies Home Assistant's float conversion and range check.

## Leads
None.