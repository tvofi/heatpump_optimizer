# D5 — Docs structure, flow and content; code comments (round 7)

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave merged).
Export: `~/audit-r7-baseline` (no `.git`; audit records, the
backlog and `RELEASE_NOTES.md` stripped).
Interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
`PYTHONPATH=tests/hastub`, run from the repository root.

Dimension brief: `tools/audit/briefs/D5.md`. Method followed in order: reader
paths, structure (link + anchor + heading + duplication), content spot-checks
(mechanism paragraphs against the code path), and the comments-in-code
executable checks (identifiers a comment names must exist; numbers a comment
cites must match the constant beside it).

Every number below is a **count** (contention-immune), so it is final under the
fan-out; no wall/CPU/RSS figure is reported and none is provisional. The
`thread_factor` is 1.0 by construction (pure text harnesses, no BLAS import);
`load1` is quoted from the run, not gated.

## Findings

### D5-01 — a production comment names an identifier that does not exist (`_dhw_hours_since_legionella`)

`legionella.py:358` says an attempt already drives `hours_since` to 0 "because
`_dhw_hours_since_legionella` counts attempts too". No such symbol exists in
the package. The behaviour the comment describes is the `hours_since` method at
`legionella.py:614` (it takes `max(last_cycle, attempt)`, so an attempt does
count). The wrong name is mirrored at `tests/features.py:27101`
(`mirrored_in_tests=1`).

Harness `comment_symbols.py` counts backticked identifiers in production
comments that resolve to nothing in the package, excluding external names
(HA/stdlib/numeric stack, and the external tvofi/tuya data-vocabulary keys the
module documents) and explicitly historical citations:

```
RESULT dangling_comment_identifiers=4 count
```
The four, in the order the harness prints them:

| comment | named | real production symbol |
|---|---|---|
| `legionella.py:358` | `_dhw_hours_since_legionella` | `hours_since` (line 614) |
| `const.py:80` | `MIN_POWER` | `CONF_HEAT_PUMP_MIN_POWER` / `DEFAULT_HEAT_PUMP_MIN_POWER` |
| `sysid.py:1283` | `T_prev` | the `previous` record (rate + delta columns) |
| `thermal_model.py:1831` | `MixedHotWater` | `MixedHotWaterSensor` |

`_dhw_hours_since_legionella` is the clearest: it names a specific function
that performs the described behaviour, and the function does not exist. The
other three are imprecise shorthand for a symbol that does exist. Fixing the
comment names drives the count down (the perturbation):

```
HPO_SYM_PERTURB=rename ... comment_symbols.py
RESULT dangling_after_perturbation=3 count
```

Severity **low**, class **hygiene**: no behaviour depends on it, but a reader
who greps the comment's name finds nothing, and the name has already
propagated into the test suite.

### D5-02 — the card's `hours` error message states a bound its own check does not enforce

`www/heatpump-optimizer-card.js` `setConfig` rejects on
`!Number.isFinite(hours) || hours <= 0 || hours > 168` — the accepted range is
`(0, 168]`. The message the throw raises, `errors.cfg_hours` (line 455 en, 900
sv), says "must be a number between 1 and 168", and the editor schema
(`_schema()`, line 11492) pins `min: 1, step: 1`. So a hand-written
`hours: 0.5` passes validation while the message calls it invalid and the
editor can neither produce nor correct it.

```
RESULT card_hours_message_min=1 number
RESULT card_hours_validation_min_exclusive=0 number
RESULT card_hours_editor_min=1 number
RESULT card_hours_bounds_disagree=1 count
```

Perturbation — the one-line production edit `hours <= 0` -> `hours < 1`:

```
HPO_CARD_PERTURB=align ... card_hours_bounds.py
RESULT card_hours_bounds_disagree_after_perturbation=0 count
```

Severity **low**, class **hygiene**. Tagged **for D4** as well: it is a
user-facing string.

## Non-findings (checked and held)

| claim checked | command | value |
|---|---|---|
| internal markdown links in README + docs/ resolve | `docs_structure.py` | `broken_internal_links=0` (5 targets are export-stripped: `RELEASE_NOTES.md`, `audit-2026-*.md`, `backlog.md`, `docs/delivery/*`) |
| heading fragments (`#section`) resolve to a real heading | `docs_structure.py` | `broken_anchors=0` over `anchors_checked=37` |
| no orphaned document | `docs_structure.py` | `orphan_docs=0`; every `docs/*.md` is linked directly from README (13 docs) |
| no heading-level skips (h2 -> h4) | `docs_structure.py` | `heading_depth_jumps=0` |
| no duplicated paragraphs (>= 40 words) between README and docs/ | `docs_structure.py` | `duplicated_paragraphs=0` |
| every doc has exactly one h1, first | inline check | clean |
| entity counts (Sensors 59, Binary 5, Buttons 4) | grep `async_setup_entry` + AST | 59 / 5 / 4 |
| "Nineteen entities disabled by default" (18 sensors + wood binary) | `is_disabled()` over the real setup | 19 (DHW install) |
| "12 services" | `services.yaml` keys | 12 |
| `set_thermal_parameters` = 28 fields | schema parse | 28 |
| option Setting/Default/Range rows match production | doc rows vs `_F(...)` table | 110 rows, 0 mismatches |
| ECL110 displace min/max (−20/+20, −30..0 / 0..+30) | `const.py:1274-1275`, `config_flow.py:1677-1678` | match |
| anti-legionella defaults (7 days, 60 °C, min 5 days) | `const.py:1250-1252,820` | match |
| VVC lead "default 20 minutes" | `DEFAULT_VVC_LEAD_MINUTES=20` | match |
| DHW Mixed Water "40 °C water" | `DHW_MIXED_USE_TEMP=40.0` | match |
| heavy-day target "90th-percentile" | `dhw_draws.py:102` `q=0.9` | match |
| comment-named identifiers in the card JS resolve | inline scan | 0 dangling |

## What could not be finished

- The three doc reader paths were walked by hand, not instrumented; the
  structural checks that can be executed are above and all hold. No dead end
  was found that a link/anchor/heading check can express.
- `RELEASE_NOTES.md` is stripped from this export, so release-history claims in
  the docs (e.g. "arrived in v6.6.5") cannot be checked here.
- Comments that "explain what the next line obviously does" were sampled, not
  enumerated; that judgement has no executable number and so no finding rests
  on it.

## Exposure

In-code and in-test comments cite earlier audit finding ids (e.g. D2-01 in
`sysid.py`, #558 C1 in the card, #282/#546/#1404 etc.), and `docs/HANDOVER.md`
and `docs/plan-2026-09-open-issues.md` carry the delivery and audit history.
Reading these is reading the record, not earlier D5 findings; none was
re-found. The export strips the audit records, the backlog and
`RELEASE_NOTES.md`, so GitHub and the release history were not readable here
and were not consulted.
