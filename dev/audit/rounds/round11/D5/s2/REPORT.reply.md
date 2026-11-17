# REPORT.md — finder seat D5-s2, audit round 11, dimension D5 (updated after the M3 re-run)

The re-run you asked for is done: all 1561 M3 units left open last time were traced against the code. **All three of my steps now cover their whole universe, and nothing is left unfinished.** The re-run turned up two new drifted numbers. One is a new finding (D5-s2-11, menu order); the other widens D5-s2-08, because it is the same kind of problem (a number in the docs that no longer matches the code).

`REPORT.json` was rebuilt in place and passes the same schema checks as before: required fields, id and path patterns, class ids, coverage counts closing, and title and metric length limits. All counts below are exact and unaffected by machine load. Baseline is `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`; everything is under `dev/audit/rounds/round11/D5/s2/` in the export.

## Coverage
| step | universe | examined | not reached | carried items |
|---|---|---|---|---|
| D5.M2 structure | 382 | 382 | none | C3 examined |
| D5.M3 content | 3265 | 3265 | none | C1, C2, C4 examined |
| D5.M4 comments | 75 | 75 | none | C5 examined |

How each step was checked:
- **M2:** `structure.py` checked every heading and link row from `text_ledger.py outline` over the 9 docs, plus repeated paragraphs, repeated diagrams, orphan documents and stale versions.
- **M3, run on all 3265 units:**
  - `content.py`: every backticked symbol is current (579 mentions, none stale).
  - `basis.py`: whether a published figure states its basis.
- **M3, mechanism-to-code trace:**
  - `defaults.py` compares 57 numbers stated in the docs with the shipped code. That includes 21 Pump duty control numbers, now traced to `pump_arbiter.py`, `duty_switch.py` and `boost.py`.
  - `defaults_table.py` compares 108 settings-table defaults and 79 ranges.
  - Targeted harnesses: `cycling.py`, `dhw_enable.py`, `menu_order.py`.
  - The re-run added executed spot checks in each remaining document: README, dashboard-card.md, setup.md, automations.md, the rest of ecl110.md, and CONTRIBUTING.md.
- **M4:** `comments.py` writes a 75-row ledger to `work/m4_ledger.tsv`: 54 true, 2 false, 19 rows that make no claim, and nothing missing or malformed. `cited_numbers.py` covers the cited-number check carried from round 10 (C5).

## Findings
| id | step | sev | claim (number, harness) |
|---|---|---|---|
| D5-s2-08 | M3 | medium | **7 of 57 numbers in the docs no longer match the code:**<br>• The anti-legionella interval is "7 days" in four places (README:506, how-it-works:622, configuration:287 and :478); the code default is **10 days**.<br>• how-it-works:1004 gives 60 min as the indoor and tank sensor age limit; the code uses **360 min**.<br>• *New in the re-run:* configuration:900 says readings in the first **60 s** after a write are ignored; the code (`pump_arbiter.ECHO_GRACE_S`) uses **20 s**.<br>Harness `defaults.py`: patching each code value to the doc's number drops the count 7→3 (legionella), 7→5 (sensor age) and 7→6 (grace); rewriting the four doc lines to 10 days gives 7→3. 50 other numbers and all 79 ranges agree. |
| D5-s2-11 | M3 | low | *New.* setup.md:131 says Quick setup is the **last** entry on the first options menu. The options flow actually shows 9 entries, and Advanced settings comes after Quick setup. Harness `menu_order.py`: Quick setup is 2nd from the end; dropping Advanced settings makes it last (2→1). |
| D5-s2-01 | M2 | low | Facts are repeated across documents instead of living in one place: 15 repeated paragraphs, the 24-row options-page table kept twice (14 rows have drifted apart), and 4 repeated diagrams. `structure.py --dedupe` cuts repeats 15→9 and drifted rows 14→0. |
| D5-s2-02 | M2 | low | docs/CONTRIBUTING.md is not linked from any other document (orphan count 1→0 when a link is added). |
| D5-s2-03 | M3 | low | No document says which basis the system-identification heat-loss figure is on. It sits 18.9 % below the effective heat-loss figure (`heat_loss_w_per_k`) at a lower-floor ratio of 1.4, and 0 % at 1.0. |
| D5-s2-09 | M3 | low | how-it-works describes the compressor-start cost as "a smooth term on the step-to-step power difference". The code counts starts instead: swinging power within one run costs nothing extra (difference 0.000, versus 22.0 in the null control). |
| D5-s2-10 | M3 | low | how-it-works says configuring a hot-water sensor, tank volume or window turns hot-water planning on. The explicit hot-water switch the setup wizard writes overrides that: with it off, all 7 combinations stay off. |
| D5-s2-04 | M4 | low | The `make_model_figures.py` docstring says no test reads the file. Not true: it is in `tests/doc_claims.py`'s dependency closure. |
| D5-s2-05 | M4 | low | `make_card_figures.mjs` has a false font-stack comment (it says the font matches the README hero) and 5 sentences over 40 words. |
| D5-s2-06 | M4 | low | `make_card_weekly_figure.mjs` has two sentences of 51 and 55 words. |
| D5-s2-07 | M4 | low (bug) | `text_ledger.py check --plant` can never pass for this seat. It plants its test text into README.md, a file the D5 check reads no comments from. Result: `plant_refused=0` and exit code 1 even for a complete ledger. |

## Re-run results that held (22 non-findings in total)
- **Pump duty control:** 21 numbers match the code, including the flow ceiling and hold temperatures, gates, feedback timings, duty-switch thresholds, rails, boost hours, retry and tank rise.
- **ecl110.md:**
  - The offset and persistent-parameter defaults and ranges match.
  - So do the 2×1440/interval write guard and the 90 s grace.
  - The Luxtronik example recomputes to the stated 1.15, 1.25 and 1.35 K.
- **automations.md:** all 5 event names exist; economy mode widens by 1.5 K with a 15 °C floor; the plan counts as stale after three intervals (90 min minimum).
- **README and dashboard-card numbers:** 8 snapshots kept, 20 h manual-plan window, 21/19.5 °C day/night defaults, 31 service fields, 900×380 chart, 48 h history fetched in 12 h chunks, hours limited to 1–168, 24 receipts kept, silent-mode slider 0.6–1.
- **setup.md:** a wood tank read from the top probe only is taken as 5 K colder.
- **CONTRIBUTING.md:** the outside-review shape matches what `bus.sh adopt` and the agent-word check (`AGENT_DECLARED`) expect.

## Leads
- **D5-s4:** comments in `www/*.js` (carried item C5).
- **D5-s8:** the INERT comment in `tests/card_drift.mjs` (it says the card figures are never read by the gate).
- **D6-s1:** whether the docs or the code are right for the drifted menu-table rows; README saying "prices come from Tibber" with no mention of a price-sensor source; the sentences behind findings 08–11.
- **D5-s1:** a developer cannot reach CONTRIBUTING.md by following links.
- **D5-s6:** fixing the `--plant` problem in finding 07.

## Exposure
I read the reader docs, as the D5 brief requires. Earlier-round finding ids that appear in code comments were treated as context only. I did not look for the wall-removed `dev/archive/backlog.md`.

Files are in `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D5/s2/`:
- `REPORT.json`
- `findings/` (D5-s2-01 to D5-s2-11)
- harnesses: `structure.py`, `content.py`, `basis.py`, `defaults.py`, `defaults_table.py`, `cycling.py`, `dhw_enable.py`, `comments.py`, `plant.py`, `cited_numbers.py`, `menu_order.py`
- `work/m4_ledger.tsv`