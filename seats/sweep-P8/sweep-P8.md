# Class P8 sweep, round 11 (D14 method steps 3-4)

Class P8 in `dev/audit/config/bugclasses.json` is a currency or unit resolved
by divergent precedence on different surfaces. The class row is `open`: there
is no detector and no barrier, and the `tests/entities.py` read rule was refused
as a barrier because it cannot see write seams.

The findings in the class are D14-s1-03 (with D14-s3-01 merged into it) and
D7-s3-01. This sweep ran in a detached worktree at
`origin/handoff/audit-r11-register`.

## Property

Every surface that names, bounds or converts a money figure or a temperature
resolves its unit by one rule:

- **Money**: the price feed's declared currency first (`#1657`), the instance
  currency only where the feed declares none.
- **Temperature**: `inputs.setpoint_unit` / the entity's own declared unit
  forwards, and the exact inverse backwards.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P8/enumerate_p8.py` scans every call
that resolves or converts a unit:

- an AST scan of the package's Python;
- a line scan of the card's currency resolver.

It generalises both findings' seams (`config_flow` calling the instance-first
`resolve_currency`; `inputs.temperature_from_c`) into four families:

- **CUR**: `resolve_currency`, `_feed_currency`, `declared_currency`,
  `money_scale`, and `config.currency` reads.
- **TEMP**: `normalize_temperature_c`, `temperature_from_c`, `temperature_c`,
  `_instance_unit`, `setpoint_unit`, `state_unit`, and `TEMPERATURE_UNIT_TO_C`
  uses.
- **PRICE**: `normalize_price_per_kwh`.
- **CARD**: the card's `currency()` and its config/HA reads.

It returns `RESULT seams=54 CUR=12 TEMP=36 PRICE=3 CARD=3`, saved as
`enumerate.out`.

- **Positive control**: the scan lists every judged site.
  - D14-s1-03: `config_flow._money` (619, 620), `_fee_placeholders` (2106),
    `_grid_fee_errors` (3973) and `grid_fee.fee_bound` (81).
  - D7-s3-01: `inputs.temperature_from_c` (446).
- **Null control**: `--fixture clean` returns `seams=0`.
- **Perturbation**: `--fixture perturbed` adds one line,
  `c = resolve_currency(hass)`, and returns `seams=1`.

## Probes

Run the probes as `PYTHONPATH=tests/hastub python3 D14/sweep-P8/probe_p8.py ...`:

| probe | value | null control |
|---|---|---|
| `currency` (SEK instance, EUR/kWh feed; D14-s1-03's harness) | money_seams=5, FAIL | `--null` (SEK feed): 0 |
| `currency --instance HUF` | money_seams=6 (adds the fee bound), FAIL | |
| `temperature --planted` (D7-s3-01's line re-introduced) | 12 of 35, FAIL | `temperature`: 0 of 35 at the register tree |

**D7-s3-01 does not reproduce at the register tree.** There,
`temperature_from_c` already reads `value_c / factor - offset`, the exact
inverse. `m8_agree.py --only temperature_roundtrip` reads
`disagreements_total=0`. The finder measured a planted copy whose line
multiplied. The `--planted` arm reproduces that copy's 12 of 35 exactly, so the
site stays a judged site with a probe that fails on the defect as judged.

## Dispositions (54 seams)

### Instances (6 seams, all judged sites, `beyond_finding: false`)

- `config_flow._money` (619, 620)
- `config_flow._fee_placeholders` (2106)
- `HeatPumpOptimizerOptionsFlow._grid_fee_errors` (3973)
- `grid_fee.fee_bound` (81)
- `inputs.temperature_from_c` (446)

`instances` (beyond the findings) = **0**.

### Guarded (40)

**Money**

- `coordinator.__init__` / `_update_current_state` resolve feed-first; this is
  the canonical rule.
- `_feed_currency` and `resolve_currency` are the resolvers themselves.
- The card's `currency()` reads its own unit first, then the integration's
  published feed currency, and uses the config or Home Assistant currency only
  as a fill-in. The harness's 13 entity surfaces agree.
- `normalize_price_per_kwh` is the one price converter.

**Temperature**

- Every set-point read, range, grid and write resolves through `setpoint_unit`
  (D12-s3-01's one rule).
- The `SetpointGrid.on_step`, `write_setpoint_c` and `setpoint_check._dhw`
  writes convert only through `temperature_from_c`, which is exact here.
- Absolute reads go through `normalize_temperature_c` in the entity's own unit.
- `read_room` applies the same climate-versus-other-entity rule.
- The forecast is read in the weather entity's `temperature_unit`.
- `read_temperature_delta_k` scales without an offset, and its unit-less
  reading as K agrees with the absolute readers' identity for C and K.

### Not applicable (8)

- `_audit_price_units` (5 seams): it is the repair that compares feed and
  instance currency, by design.
- 3 power or flow unit reads: each is one surface with one rule, outside the
  class's currency and temperature pair.

## Barrier

The class stays `open` (`barriered: false`). Proposed barrier: a zero rule in
`tests/entities.py` built from `enumerate_p8.py`'s CUR family:

- Any CUR call outside `coordinator.self.currency`'s precedence and the
  `_audit_price_units` repair fails the rule. Today that is exactly the
  `config_flow` judged sites.
- The rule also runs this sweep's `temperature` round-trip probe over the
  whole `TEMPERATURE_UNIT_TO_C` table.

Together these cover the write side that the existing read rule cannot see.
Gate cost: well under 1 s.

`root-cause.md`'s records for P8 are BULK-1-P8 and RCA-R8-P8-1513, cited in the
class row.
