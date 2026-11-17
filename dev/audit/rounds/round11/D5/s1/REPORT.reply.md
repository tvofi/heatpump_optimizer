I walked the 17 cells you listed, so all 27 are now covered and nothing is left under `not_reached` or `unfinished`. The walk found two more doc errors, both low severity, so the report now has four findings. `REPORT.json` is updated in place and `check_report.mjs` still returns `ok D5-s1`.

**REPORT.json:** `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D5/s1/REPORT.json`. The four finding files are in `findings/` in that directory. I made no commits, no GitHub calls and did not read P.json.

---

# D5-s1 report, round 11, baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692

## Method
- **Cells:** step D5.M1 over `README.md` and `docs/**`.
- **Universe:** the three reader paths times the 9 `document` rows of `text_ledger.py outline`. That is 27 items, listed by `dev/audit/rounds/round11/D5/s1/enum_m1.py`.
- **Readers walked:**
  - a new user, from installing to a first plan;
  - a user configuring a feature (two-tank storage, ECL110, capacity tariff);
  - a developer looking for how to run the tests.
- **How claims were checked:** each claim I examined was traced to the code or rendered strings behind it.
- **Coverage:** 27 of 27 examined. The re-run added `dashboard-card.md`, `how-it-works.md` and `automations.md` on all three paths, and `architecture.md`, `ecl110.md` and `CONTRIBUTING.md` on the remaining paths.

## Findings

**D5-s1-01 (medium, bug): the two-tank docs give two different switch-on rules, and neither matches the code.**
- `docs/setup.md` (Quick setup, "Wood buffer tank" row) says a throttling valve plus the wood-tank probes is enough. It does not mention two zones.
- `docs/configuration.md` (layout catalog) says a valve, two zones and the top sensor.
- The code (`ThermalParameters.topology_layout` and `const.topology_layout_valid`) needs a valve, two zones, the top or bottom probe, and the wood furnace on.
- Harness: `two_tank_gate.py`, over a 16-cell grid.
  - `setup_md_mismatch=3`: every single-zone house with a valve and a probe. Quick setup's "two-zone: no" answer leads straight there.
  - `configuration_md_mismatch=1`: bottom probe only.
- Perturbation: dropping the two-zone condition moves the counts to 0 and 4 (executed).

**D5-s1-02 (medium, bug): the README contradicts itself on control paths.**
- It says control goes "over three paths" above a table with 5 rows.
- The "Known limitations" bullet says a stored curve parameter "is not supported in this version". The README's own table row and Removal section, `docs/ecl110.md` ("Kind persistent"), and the options-page selector (offering `['offset', 'persistent']`) all support it.
- Harness: `control_paths.py` gives `denied_kinds=1`, `readme_path_rows=5`, `readme_path_count_stated=3`.
- Perturbation: cutting the kinds to `('offset',)` gives `denied_kinds=0` (executed).

**D5-s1-03 (low, hygiene): `how-it-works.md` names an options page that does not exist.**
- It twice sends the reader to a "Grid costs page". The options menu has no page by that name.
- The real pages are "Grid peak tariff" (the tariff masks) and "Advanced settings → Transfer fees and contract" (the transfer fee).
- The same section calls the meter a "baseline load entity", but the field is labelled "Whole-house power meter".
- Harness: `page_names.py`, keyed on the menu labels in `translations/en.json`, gives `missing_pages=1`.
- Perturbation: renaming that label in memory gives 0 (executed).

**D5-s1-04 (low, hygiene): `how-it-works.md` and `configuration.md` disagree on whether an over-limit transfer fee is refused.**
- `how-it-works.md` says a fee above the 10 SEK/kWh plausibility limit "is flagged, not refused".
- `configuration.md` and the code say it is refused when the page is saved. `grid_fee.spec_problem` returns `grid_fee_rules_implausible` for all 3 probes, including the doc's own "= 25" example.
- The "flagged" behaviour applies only to values that never pass the page's check: a live fee sensor or an already-stored value.
- Harness: `fee_refusal.py` gives `refused_rules=3`.
- Perturbation: setting `fee_bound` to infinity gives 0 (executed).

## Dead ends and contradictions per reader path
| Reader | Count | Where |
|---|---|---|
| New user | 1 | D5-s1-02 |
| Feature | 5 | D5-s1-01, D5-s1-02, D5-s1-03, D5-s1-04 |
| Developer | 1 | `CONTRIBUTING.md` gives no test command and no link to `tests/README.md` |

On the feature path, the capacity-tariff section of `configuration.md` had no errors. The errors were in `how-it-works.md`'s capacity-tariff and transfer-fee sections (D5-s1-03 and D5-s1-04).

## Things checked that held
- **Capacity-tariff defaults:** all 9 defaults in `configuration.md` match `const.DEFAULT_PEAK_TARIFF_*`.
- **ECL110:** the README section and `ecl110.md` agree on where the settings live and that the topics ship empty.
- **Developer route:** `README.md` line 1124 and `architecture.md` line 420 link `tests/README.md`, and the file exists.

## Work handed over from the previous round
- **C1, examined:** two-tank, ECL110 and capacity tariff walked paragraph by paragraph across all docs.
- **C2, examined:** the six `docs/img` figure scripts are not `document` rows in the outline, so no reader path walks them.

## Harnesses
All under `dev/audit/rounds/round11/D5/s1/`:
- `two_tank_gate.py`
- `control_paths.py`
- `page_names.py`
- `fee_refusal.py`
- `enum_m1.py` (the enumerator)

All results are exact counts, so the box load (`load1` about 205–277) does not affect them.

## Unfinished
None.

## Leads (owner unknown)
- **For D6:** `README.md` line 522 says "All 82 entities appear"; the entity count needs checking.
- **For D6:** `configuration.md` line 993 says the top sensor is "the switch for the two-tank model", but the bottom probe alone also turns it on in the code.
- **Structure:** `docs/CONTRIBUTING.md` has no route to running the tests.

## Exposure
I read `README.md` and `docs/setup.md`, `configuration.md`, `ecl110.md`, `CONTRIBUTING.md`, `architecture.md`, `how-it-works.md`, `dashboard-card.md` and `automations.md`. I did not look for earlier finding ids.