# D5-s3 report (round 10, baseline 17f1c55fad1b)

Method: M4 executable check over all 76 `custom_components/heatpump_optimizer/*.py`
modules — every backticked identifier in a comment or docstring checked against the
identifier tokens of all code in custom_components/, tests/, tools/, www/*.js and the
package json/yaml (`comment_symbols.py`). 27 raw hits; 26 triaged by reading as
external (HA, numpy, Nord Pool, device payloads, example entity ids, another repo's
`tools/gen_gchv_package.py`), math notation, substring of a real name, or a sentence
stating the name does not exist. M1–M3 over the code/JS cells: spot only.

## Findings
- D5-s3-01 (low, hygiene): coordinator.py:1976 comment says the sensors state the feed
  currency via ``money_currency``; no such attribute/key exists anywhere — sensors carry it
  as `unit_of_measurement` and a `"currency"` attribute. RESULT comment_symbols_untriaged_missing=1.

## Non-findings
- 75 of 76 modules: every backticked comment identifier resolves (same harness).
- Two `dev/audit/harnesses/*.py` paths cited in draw_range.py / early_cutoff.py exist.

## Unfinished
- M1–M3 on production cells only spot-checked; cited-number-vs-constant check not automated;
  README/docs M4 not run.

## Exposure
Production comments cite earlier finding ids (e.g. `D2-01`, `#1657`); read as context only.
Harness: `dev/audit/rounds/round10/D5/s3/comment_symbols.py`.
