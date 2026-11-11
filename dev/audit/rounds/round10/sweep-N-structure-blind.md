# Class sweep: N-structure-blind (round 10, D14 steps 3-4)

Ledger status (`dev/audit/config/bugclasses.json`): **barriered** by
`tests/structure.py` on the PR gate; 10 instances over R1, R2, R6-R9. This round
has 5 judged findings in the class: D7-s1-01, D7-s3-01, D7-s3-02, D7-s3-51
(filed as D7-arch3-01) and D7-s3-52 (filed as D7-arch3-02).

**Result: 9 seams. 5 are instances, and every one is a judged finding's own site.
4 are guarded. 0 are instances beyond the findings.**

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-structure-blind/enumerate.py`
runs five seam rules. Each rule comes from a finding's `seam_rule` and covers
the whole package plus every gate metric:

| rule | shape | scope walked |
|---|---|---|
| A | budget key = `max()` over a unit table with no threshold-count key on the same table | every key of `measure()`'s `metrics` dict, `table_maxima` resolved |
| B | liveness decided by a name set, not a resolved load | `dead_members` name-kept set; `HA_CONVENTION_NAMES` against the HA-loaded modules (`PLATFORMS` + `__init__`, `config_flow`, `diagnostics`, `repairs`) |
| C | executable package source in a language no dead-code metric reads | every `.js/.mjs/.ts/.cjs` under `custom_components/` (`structure.py` reads `*.py` only) |
| D | archscore predicate that string-matches an `ast.unparse`d annotation | every function under `tools/audit/archscore/` that takes `ann` and calls `unparse` |
| E | archscore census seeded from a static key set | `untyped_payload_keys` `Flow.returned_keys` against runtime payload keys |

## Seams and dispositions

| rule | seam | disposition | probe / guard |
|---|---|---|---|
| A | `structure.py measure:max_class_loc` | **instance** (D7-s1-01) | `class_growth.py`: 1201 lines added to the second class move 0 keys, against 1 for the coordinator |
| A | `measure:max_method_loc` | guarded | `methods_over_150` / `methods_over_200` count every method over the line |
| A | `measure:max_cc` | guarded | `functions_cc_over_15` / `functions_cc_over_25` |
| B | `dead_members:name_kept` | **instance** (D7-s3-01) | `namekept_receivers.py`: 6 candidates with 0 typed hits. The sentinel's other NOPROD rows are HA hooks or Protocol fields, which are the same seam |
| B | `HA_CONVENTION_NAMES` | guarded | all 13 convention-named defs sit in HA-loaded modules, so the probe returns 0 strays |
| C | `www/heatpump-optimizer-card.js` | **instance** (D7-s3-02) | `card_dead_fn.sh`: textWidth 0 calls, live control fmtTick 39 calls |
| D | `archscore common.py:is_coord_annotation` | guarded | 8 package Protocols. The only coordinator stand-ins (`_BoostCoord`, `_AwayCoord`) end in `Coord`, so 0 misses |
| D | `untyped_payload_keys.py:is_any` | **instance** (D7-s3-52) | `payload_any_spellings.py`: `Any\|None`, `Optional[Any]`, `"Any"` and an alias each read 0 of 6 |
| E | `untyped_payload_keys.py:Flow.returned_keys` | **instance** (D7-s3-51) | `payload_census_coverage.py`: 10 AwayView keys blind, headline 0 |

## Controls (run at 9355f107d, B5 macOS arm64)

- **Positive.** The enumerator lists all five finding sites as `instance`, and
  `--probes` re-runs each finding's harness. Each harness reproduced its value
  this run: keys_moved_second_class=0, typed_hits=0 over 6, textWidth_calls=0,
  blind_keys=10, and every spelling reads 0.
- **Null.** `--null` runs rules A, C and D on a clean fixture: a `measure()`
  whose max keys all have count siblings, a `.py`-only package, and an `ann`
  function with no `unparse`. It prints `null_fixture_instances=0`.
- **Perturbation.** `--perturb` adds one line in memory to `measure()`: a
  count key over `god_classes`. `max_class_loc` flips to guarded, and
  instances go from 5 to 4.

## Barrier note

The ledger barrier, `tests/structure.py`, covers the four guarded seams. It
does not cover the five instance seams; each finding's fix is that seam's
barrier. Every instance is a judged site, so this sweep adds no
`beyond_finding` seam to the ledger. The JSON's `barriered` is the count of
guarded seams (4).
