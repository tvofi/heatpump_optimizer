# D6-s2 report (round 10, baseline 17f1c55fad1b)

Scope: docs/** (architecture, automations, configuration, dashboard-card, ecl110, how-it-works, setup), steps M1-M3.
Exposure: docs/*.md (all seven, read by the harnesses; configuration.md and how-it-works.md opened by hand).

## Method
Mechanically extracted the structured claim shapes and checked each against production:
- `config_defaults.py`: every docs/configuration.md settings-table row whose label maps through strings.json to a
  `config_flow._OPTION_FIELDS` key; documented Default vs `config_flow._field_marker` rendered default; documented
  Range vs the NumberSelector min/max. Perturbation: target_temperature default -> 99.0, default_false 0 -> 1.
- `docs_refs.py`: entity ids cited in docs vs ids produced through the real platform `async_setup_entry`
  (tests/entities.py:collect); `heatpump_optimizer.<service>` vs services.yaml; relative links and anchors.
  Perturbation: produced id prefix renamed, entity_false 0 -> 16.

## Claims table (harness output is the table)
| shape | checked | true | false | unverifiable |
|---|---|---|---|---|
| setting defaults | 78 | 78 | 0 | 7 (default computed/derived by presets, not a literal) |
| setting ranges | 91 | 91 | 0 | - |
| entity ids | 16 | 16 | 0 | - |
| service names | 3 | 3 | 0 | - |
| relative links/anchors | 74 | 73 | 1 (export artefact) | - |

## Findings
None.

## Non-findings
- All 78 numeric defaults and 91 ranges in docs/configuration.md agree with the option-flow registry.
- One apparent default mismatch (Compressor rated starts "100 000") was a harness gap (thin-space thousands separator); fixed in the parser.
- All 16 cited entity ids exist; all 3 cited services exist.
- docs/how-it-works.md:1331 links ../dev/archive/backlog.md, absent only because the finder wall removed the backlog from the export; not a defect at the baseline.

## Unfinished
Prose behaviour, performance and unit claims (M1 shape "the optimizer will...") across how-it-works.md, architecture.md,
dashboard-card.md and ecl110.md were not extracted or checked; external link HEAD requests not run.
