# Round 11, D5, seat D5-s4 — code comments in custom_components/heatpump_optimizer/{j..z}*.py and www/*.js

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B11. Cells, as
`tools/audit/check_scopes.py --seat D5-s4` prints them: 50 Python modules and the card, steps M1 to M4.

## Method

- **M1 and M2.** `text_ledger.py outline --seat D5-s4` prints no document, heading or link row for
  .py or .js files, so both universes are 0. The comments cite no URL. Every path they cite resolves
  (comments.py C2, triaged by hand).
- **M3.** The step covers the D6 units of the documents `outline` prints. The cells hold no document,
  so the universe is 0.
- **M4.** There are 3367 D5 units (2224 comment blocks, 1143 docstrings). Each one has a row in
  `ledger.tsv`, written by `build_ledger.py`. Every unit went through `comments.py`, which runs these
  checks against the code tokens of every tracked file:
  - **C2.** Every name a unit cites must exist in the code.
  - **C5.** No sentence may be longer than 40 words.
  - **C7.** A number cited in a comment must agree with the `NAME = number` line the comment sits on.
  - **C4 and C3.** Heuristics only.

  Hand triage of the raw flags:
  - **C2.** 18 raw flags, of which 2 are false, both in `sysid.py`. The other 16 are math notation,
    DOM APIs, ranges, keys built with f-strings, or paths that do resolve.
  - **C7.** 42 raw flags. 21 were driven by `py_numbers.py` and `card_numbers.mjs`, and none failed.
    The other 21 cite measurements or history, not the constant itself.

  Behavioural truth was checked by running the code (`semantic.py`) in 16 checks, covering log_latch,
  plan_step, silent_mode, pump_schedule and plan_slots.

`text_ledger.py check --dim D5 ledger.tsv --plant --seat D5-s4 ...` gives:
`units=3367 rows=3367 claims=3200 true=33 false=2 stale=0 unverifiable=3165 unrowed=0 orphan=0 malformed=0 plant_refused=1`.

## Findings

- **D5-s4-01 (C5, low, hygiene).** 558 of 3367 units (16.6 %, in 45 of 51 files) contain a sentence
  over 40 words, 716 such sentences in all.
  - Leave-one-out: if the card is dropped, 403 remain.
  - Perturbation: splitting one sentence in pump_mode.py brings that file from 3 to 2.
  - One finding per criterion rather than one per file, because the mechanism is the same everywhere
    (COMMON.md, "group by phenomenon").
- **D5-s4-02 (C2, low).** Two units in `sysid.py` name variables that exist nowhere in the code:
  ``T_prev``, and `prior_rel = prior_w / data_w`. The code computes `prior_rel = s_noise / prior_sd`.
  - Perturbation: rewriting line 2073 moves the count from 2 to 1.
- **D5-s4-03 (instrument, low, bug).** `text_ledger.py:scan_c_like` loses one line each time a JS quote
  is cut off at a newline. As a result, 737 of the card's 892 units carry a wrong line number, off by
  up to 11 lines.
  - Fixing that one line in memory brings the count to 1, and that remaining 1 is a tie in the
    locator, not a scan error.
  - The file is in D5-s6's cells. The defect showed up while measuring this seat's card, and it had
    misled this seat's own C7 adjacency check until units were relocated by their text.

## Non-findings

All with the exact commands in REPORT.json:
- `py_numbers.py`: 11 of 11 hold.
- `card_numbers.mjs`: 10 of 10 hold.
- `semantic.py`: 16 of 16 hold.
- The card's copy of the staleness rule (3 intervals, 90 min) matches `coordinator.py`.
- The design paths the card cites exist on `archive/handoff/audit-r9-alt`.
- There are 0 URLs in the comments.
- The sensor-rename comments agree with `_pin_identity`.

## Harnesses

`comments.py`, `ledger_lines.py`, `py_numbers.py`, `card_numbers.mjs`, `semantic.py`, `build_ledger.py`
(with `ledger.tsv`). Each runs from the export root with `PYTHONPATH=tests/hastub`, and each header
gives its command, the values to expect and its perturbation. The only timing number is `comments.py`'s
wall/cpu line, and it is provisional.

## Unfinished

- **M4, C1.** Behaviour was driven for 35 of 3200 claim units. The other 3165 rows are
  `unverifiable` (mechanical checks only). The biggest files are the card (892), optimizer.py (424),
  thermal_model.py (366), sensor.py (223), pump_arbiter.py (159) and sysid.py (143).
- **C4 and C3.** These ran only as heuristics: 43 and 8 flags, all read, none confirmed.
- **M3, C6.** Docstring mechanism paragraphs were traced in five modules only.
- **C2 and C3 carries.** They point at docs/, which lies outside this seat's cells. They are routed as
  leads to D5-s1 and D5-s2.

## Redispatched

| item | state |
|---|---|
| C1 | examined: M3 has a stated denominator, 0 documents |
| C2 | not_reached: outside the cells, lead to D5-s1 |
| C3 | not_reached: outside the cells, lead to D5-s2 |
| C4 | examined: universe 0 |
| C5 | examined: universe 0, 0 URLs |
| C6 | not_reached: see Unfinished |
| C7 | examined: number check automated, JS comments scanned |

## Leads

- **plan_slots.** `plan_slots` picks the slot `reason` on a tie in an order set by
  PYTHONHASHSEED. Under seeds 1 to 6 the same plan published 'cheap' three times and 'preheat' three
  times. Owner: unknown.
- **C2 carry.** Goes to D5-s1.
- **C3 and the docs half of C7.** Go to D5-s2.
- **The 3165 unverifiable claim rows.** Go to D6.

## Exposure

Comment units cite earlier finding ids: D2-01, D2-07, D7-01, D4-01, R9-*, R10-*. One grep showed two
rows of `dev/programme/register/audit-2026-09.md`. The tag `archive/handoff/audit-r9-alt` was listed
only to resolve a cited path. None of this was used as a to-do.
