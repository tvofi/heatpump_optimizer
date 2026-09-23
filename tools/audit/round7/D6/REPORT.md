# D6 — README and documentation claim verification (round 7)

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave fully
merged), export at `/Users/timmalmstrom/audit-r7-baseline`.

## Method

One executed check per documented claim, in the order the brief sets: extract
every sentence with a number, a default, an entity or service name, a field, a
behaviour, a performance statement, a version or a link from `README.md`,
`docs/*.md` (except the audit records), `DISCLAIMER.md`, `services.yaml`,
`strings.json` + `translations/`, `manifest.json`, `hacs.json` and
`blueprints/automation/*.yaml`; number them; run one check each; tabulate the
verdict. The harness is `claims_check.py` (committed beside this file), whose
output *is* the claims table and the four D6 counts.

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round7/D6/claims_check.py
```

Entity names and counts are driven through the real `async_setup_entry` via
`tests/entities.py:collect`, not by listing classes. Constants are read from
the production modules that use them, not transcribed. The card's defaults are
read from `www/heatpump-optimizer-card.js`'s own `DEFAULTS`. Translations are
compared as flat leaf sets.

## Numbers

```
RESULT claims_extracted=38
RESULT claims_checked=34
RESULT claims_true=34
RESULT claims_false=0
RESULT claims_stale=0
RESULT claims_unverifiable=4
```

The machine was the shared fan-out box (`load1=7.22` at run time); every number
here is a count, which is contention-immune, so none is provisional. The
harness's own `thread_factor=1.002`, printed by the harness.

## Findings

**None.** Every claim I could execute against the baseline's own tree agreed
with the code and data. `claims_false=0`, `claims_stale=0`.

## Non-findings (claims that held, with the executed number)

| id | source | claim | result |
|---|---|---|---|
| C01 | VERSION / manifest.json / RELEASE_NOTES.md | the release version is one number everywhere | VERSION=6.6.9 manifest=6.6.9 notes=v6.6.9 |
| C02 | README.md / hacs.json | README requirement line, badge and hacs.json name the same HA floor | hacs=2025.2.0 badge=True reqline=True |
| C03 | docs/architecture.md | 65 modules, 22 import homeassistant at module level, 1 inside a function, the rest 42 | 65 / 22 / 1 / 42 |
| C04 | README.md / docs/setup.md | the options menu is 23 pages (8 everyday + 15 advanced) | 23 = 8 + 15 |
| C05 | docs/setup.md | a read-only overview page is among the 23 | setup_overview present |
| C06 | README.md / services.yaml / services.py | 12 services, and services.yaml lists the same fields as each voluptuous schema | 12 services, 12 yaml blocks, 0 field mismatches |
| C07 | README.md | set_thermal_parameters has 28 fields | 28 |
| C08 | README.md / docs/architecture.md | 74 entities: 59 sensors, 5 binary sensors, 4 buttons, 4 switches, 1 climate, 1 datetime | 74 = 59+5+4+4+1+1 (via `collect`) |
| C09 | README.md | nineteen entities disabled by default (18 sensors + the wood binary sensor) | 18 + 1 = 19 |
| C10 | docs/architecture.md | the ECL110 below-0 nudge threshold is `max(0.1, min_electrical_power*0.5)` | optimizer:6814 matches |
| C11 | docs/how-it-works.md | the DHW congestion premium refills within a 6-hour window either side | `_DHW_REFILL_WINDOW_HOURS=6.0` |
| C12 | README.md | the first plan is solved within one optimisation interval (30 minutes by default) | `DEFAULT_OPTIMIZATION_INTERVAL=30` min |
| C13 | README.md / docs/how-it-works.md | at most one `number.set_value` per five minutes | `FREQ_WRITE_MIN_INTERVAL_S=300.0` s |
| C14 | README.md | the frequency watchdog stands down after three active ticks | `FREQ_WATCHDOG_TICKS=3` |
| C15 | README.md / docs/how-it-works.md | the heat-curve correction moves at most 0.5 K per week | `MAX_DOWN_PER_WEEK=0.5` |
| C16 | README.md | the last eight learner snapshots are kept | `snapshots.RING_SIZE=8` |
| C17 | README.md / strings.json | the open-window relax lowers the target by 1 C | `OPEN_WINDOW_RELAX_C=1.0` |
| C18 | docs/automations.md / strings.json | economy rides up to 1.5 C below the comfort floor, never below 15 C | `ECONOMY_MIN_TEMP_WIDENING=1.5` / `ECONOMY_ABSOLUTE_FLOOR=15.0` |
| C19 | README.md | the card's editor pins run slots for up to 20 hours | `MANUAL_PLAN_WINDOW_HOURS=20` |
| C20 | docs/architecture.md / strings.json | the flow-curve learned offset is capped at 15 C | `FLOW_BIAS_CLAMP_K=15.0` |
| C21 | docs/how-it-works.md | capacity is floored at 60 % of nameplate | `CAPACITY_FLOOR_FRACTION=0.6` |
| C22 | docs/how-it-works.md | the defrost derate is clamped at 1.0, not 1.05 | `defrost.DERATE_MAX=1.0` |
| C23 | docs/how-it-works.md | the solar split puts 40 % on the upper floor | `DEFAULT_SOLAR_UPPER_FRACTION=0.4` |
| C24 | docs/dashboard-card.md | the optimizer horizon defaults to 24 hours | `horizon_hours=24.0` |
| C25 | docs/dashboard-card.md / README.md | the same keys in both languages, no Swedish entry missing | 1279 leaves each; 0 only-en, 0 only-sv; strings.json == en.json |
| C26 | README.md / docs/*.md | every relative link resolves | 90 links, 4 broken, all 4 the deliberately stripped set |
| C27 | README.md / docs/*.md | every in-page anchor resolves to a heading | 37 anchors, 0 unresolved |
| C28 | docs/dashboard-card.md | card defaults hours 24 / what_if true / show_stats true, hours capped at 168 | 24 / true / true / cap 168 |
| C29 | DISCLAIMER.md | it refers to a LICENSE that is the MIT licence | LICENSE exists, MIT |
| C30 | DISCLAIMER.md | the README carries a condensed summary of it | `## Disclaimer` present and links DISCLAIMER.md |
| C31 | docs/automations.md | three blueprints ship | 3 |
| C32 | docs/automations.md | the blueprints take inputs rather than hard-coding ids | 0 hard-coded ids |
| C33 | README.md / docs/automations.md / docs/dashboard-card.md | every entity id the docs name is a sensor this integration creates | 5 ids, 0 unaccounted |
| C38 | README.md | the peak guard needs two agreeing samples to engage and two to clear | `power_guard.HYSTERESIS_SAMPLES=2` |

### Unverifiable from the tree (recorded, not judged)

- C34 `docs/architecture.md` — "2025.2.0 is the first Home Assistant whose own
  `pyproject.toml` requires-python >=3.13.0": an external release fact; the
  brief forbids reading GitHub. Note the README, architecture.md, `hacs.json`
  and `tests/entities.py` all agree on the floor itself (C02).
- C35 `README.md` — "display names have been translated since v5.0.0": a
  historical release point; the export has no git history.
- C36 `docs/how-it-works.md` — the comfort-weight table (5 -> 19.4 C / 53 %):
  the doc itself labels it a one-off measurement on the author's house.
- C37 `README.md` — "the first plan is solved within one optimisation
  interval": a wall-clock figure; the box is shared with the fan-out.

## What could not be finished, and self-inflicted gaps (so a later round is not misled)

- **`grep CONGESTION` returns nothing** — the DHW congestion premium is
  implemented as a per-step auxiliary variable in `optimizer.py` (`optimizer.py:5062-5091`,
  the `_DHW_REFILL_WINDOW_HOURS` search), not a symbol named `CONGESTION`. The
  doc claim (C11) is *true*; the miss was a grep on the wrong token.
- **A slug function that collapses runs of spaces** reports four false
  unresolved anchors in `docs/setup.md` (`#screen-1--price-source-and-weather`
  and friends). Those headings use `·`/`—`, which GitHub strips leaving *two*
  spaces, so the real anchor has a double hyphen. Reproduce with GitHub's rule
  (drop punctuation, replace each space with `-`) and the count is 0 (C27).
- **A regex that reads the first `what_if:` in the card source** reports
  `what_if=false`; the first hit is inside a comment ("Set `what_if: false` to
  hide the panel"). Anchor to the key line and the default is `true` (C28).
- **`tests/entities.py` runs every check at import and `sys.exit`s**, and the
  export strips `tools/audit/round4/D6/claims.json` and
  `tools/audit/round4/D11/governance_cost.py`, which it reads at import time.
  The harness stubs exactly those two paths (a round-4 register and a round-4
  `GOV` set, not part of any D6 claim) so `collect` is reachable; the 56
  self-check FAIL lines this produces are export artefacts, not D6 results.
- Not attempted: `docs/plan-*.md`, `docs/HANDOVER.md`, `docs/decisions/*` (the
  programme records and ADRs, D5/record-owned), `docs/superpowers/*` (dated
  design specs — spot-checked: the wood-furnace spec's efficiency default 75,
  slider 10-95 % and 0.05 kW active-now threshold all match the shipped code).
  A network HEAD-request pass over the external links was not run (the brief
  forbids reading GitHub; the external links point there or to vendor docs).

## Exposure

Audit-era documents opened: `docs/architecture.md`, `docs/ecl110.md`,
`docs/setup.md`, `docs/configuration.md`, `docs/how-it-works.md`,
`docs/dashboard-card.md`, `docs/automations.md`, `DISCLAIMER.md`, `README.md`,
`AGENTS.md`, `RELEASE_NOTES.md`, `SECURITY.md` — none carries an earlier audit
finding (they are user-facing or the licence/disclaimer set).
`docs/plan-*.md`, `docs/HANDOVER.md`, `docs/delivery/` and `docs/decisions/`
were not opened beyond their file names. No `.git`, no `gh`, no GitHub.
