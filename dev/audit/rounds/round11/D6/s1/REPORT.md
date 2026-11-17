# D6-s1, round 11: README and documentation claim verification

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, export `/home/user/audit-r11-baseline`, box B1.
The JSON report is `REPORT.json` beside this file, and the findings are in `findings/`.

## Exposure

I read the docs in my cells, as D6 requires. I read no earlier-round findings.

**Disclosure:** the export is not byte-identical to the baseline commit. `tests/doc_claims.py` crashed
on a non-UTF-8 AppleDouble file, `docs/._configuration.md`. While chasing that, I diffed `git archive 92d38ecb` against the export.
The diff showed the differing files and their hunks:

- 18 production modules: const, defrost, grid_fee, heat_curve, inputs, legionella, mixing_valve,
  optimizer, power_guard, presets, price_model, pump_arbiter, sensor, store, tariff, thermal_model, wood_fuel
- `translations/de.json`
- the card JS
- `docs/configuration.md` line 901, where 20 seconds became 60 seconds

These look like decision 0018's planted defects, so this seat's planted-defect recall is contaminated
and should be discounted. Three things followed from that:

- I checked D6-s1-01's echo-grace row and wrote the D1-s1 lead after seeing the diff.
- I measured everything against the export, which is the tree under test, never the archive.
- I deleted the extracted archive.

## Method

**M1.** `ledger.py` enumerates every unit with `text_ledger.enumerate_units`, keeping each unit's full text.
A committed rule classes each unit as claim or no-claim, and every unit gets a row in `ledger.tsv`:
- 3970 units in total
- 3340 claims
- 630 no-claims

`live_page.py` checks the live Pages site against the tree.

**M2.** These executed checks feed the ledger:
- **Settings tables:** each table row's default and range is compared with `config_flow._OPTION_FIELDS`, or with the wizard and `const` defaults. About 113 rows were keyed.
- **Backticked names:** paths, services, entity ids and identifiers are resolved against production, tests, tools and the baseline tree list `tree_92d38ecb.txt`.
- **Links and anchors:** relative links are checked against the tree. External URLs get a HEAD request; GitHub is not read. `tools/site/build_docs.mjs` runs, and `d6_page_anchors.py` checks anchors.
- **Behaviour:** `claims.py` drives production for 14 behavioural sentence rows.

Each claim without an executed check is rowed `unverifiable` with result `NOT-REACHED`. Those rows are counted under `not_reached`, not as examined.

**M3.** I ran `text_ledger.py check` and its `--plant` control.

## Findings

| id | file | false rows | what |
|---|---|---|---|
| D6-s1-01 | docs/configuration.md | 3 | The anti-legionella interval default is given as 7 days in 2 table rows; the code default is 10 days. The "first 60 seconds after a write are not counted" sentence is false: `pump_arbiter.hold` counts a reading at +5 s, and `ECHO_GRACE_S` is 20 s. |
| D6-s1-02 | README.md | 2 | "Every 7 days" is false; the default is 10. The closed-loop learner sentence is false: at a 35 % heavier true loss, the scale goes from 1.000 to 0.300 and the breach goes from 0.00 to 5.42 K·h. With a correct model the scale stays at 0.979. |

Perturbations take each count to 0:
- `claims.py --perturb-grace 60 --perturb-legionella 7` plus `ledger.py --perturb-default dhw_legionella_interval_days=7` takes `false_rows_total` from 5 to 0. The learner row is not in that run because it used `--skip-rolling`.
- `--perturb-grace 20` leaves 3 echo contradictions.

## Non-findings, with the number that held

| claim | number |
|---|---|
| 24 option pages, 23 editable | 24 = 8 + 16, 1 read-only |
| 20 h manual-plan window | a 30 h expiry clamps to 20 h; a slot at +20.25 h is refused |
| 8 weekly snapshots | 8 kept, 7-day gaps |
| ±12 % for a correct model | scale 0.979 |
| Peak guard: two samples engage it, two release it | [F, T, T, F] |
| `comfort_weight` defaults to 5 | 5.0 on tuning |
| Settings-table defaults and ranges | every one of the ~113 keyed rows agrees except the legionella rows |
| Docs build | build_docs PASS with 0 FAIL lines; 0 unresolved anchors over 10 pages |
| External links | 13 URLs answer HEAD 200 |
| Live site | 0 diff lines against `docs/index.html`; 9 of 9 sub-pages answer 200 with 0 unresolved anchors |

On its first pass the ledger produced 18 false rows that were all harness gaps, not doc defects. They were served URL paths, API hosts, files in another repository, composed name fragments, negated identifiers and a third-party integration. The rules now handle each case.

## Harnesses

Each harness carries its run command in its header.
- `ledger.py`: the ledger and M2 checks. Run it with `--tree dev/audit/rounds/round11/D6/s1/tree_92d38ecb.txt`.
- `claims.py`: the behavioural checks. It takes about 6 minutes; `--skip-rolling` skips the closed loop.
- `live_page.py`

The outputs are committed: `ledger.out`, `claims.out`, `check.out` and `check_plant.out`.

## Unfinished

**M2:** 2706 claim rows have no executed check. The counts by file are in REPORT.json. RELEASE_NOTES history was not checked per version. C4's golden-scenario half is not done.

## Leads

- **D2-s1, coordinator learner:** the learner diverges at plant_error 1.35.
- **D1-s1, `pump_arbiter.hold`:** no echo grace after a write.
- **unknown, `tests/doc_claims.py`:** it crashes on the AppleDouble files. On a clean copy it fails in `plan_view.py`: space slot energy 46.595 kWh against a schedule of 46.621 kWh.
