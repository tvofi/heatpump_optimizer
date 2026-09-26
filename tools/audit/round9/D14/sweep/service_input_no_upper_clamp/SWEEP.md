# Sweep: "service input without an upper-bound clamp"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D1-s2-54
(verified, low). Not a ledger class (new).

## Enumerator

```
$ grep -n 'expires_at' custom_components/heatpump_optimizer/services.py custom_components/heatpump_optimizer/manual_plan.py
```

widened to every service-call schema field in `services.py` with no
`vol.Range` upper bound:

```
$ grep -n "vol.Coerce(float)\|vol.Coerce(int)\|vol.All(" custom_components/heatpump_optimizer/services.py
```

## Positive control

`services.py:867` (`handle_apply_manual_plan`): `raw_expires =
data.get("expires_at")`, parsed with `dt_util.parse_datetime` and validated
only for "unparseable" or (inside `manual_plan.build_override`) "in the
past" — no upper bound against the plan horizon (96 steps / 24h at 15-min
resolution). Confirmed at baseline `1936d5ca`; `services.py` and
`manual_plan.py` are unchanged on `origin/main`.

## Widened candidates, dispositioned

`SERVICE_SCHEMA_SIMULATE_PLAN` (services.py:86-111, the what-if simulator)
has six `vol.Coerce(float)` fields (`target_temp`, `min_temp`, `max_temp`,
`comfort_temp_day`, `comfort_temp_night`, `comfort_weight`) with no
`vol.Range`. **Not applicable**: the schema's own comment says "every field
is optional: the card sends only the one the user is dragging" for a
read-only what-if simulation with no persisted or actuating effect — an
unbounded `simulate_plan` input cannot pin real heating/DHW slots the way
`apply_manual_plan`'s `expires_at` can, so it is a different risk shape
(no lasting consequence), not this class.

`SERVICE_SCHEMA_SET_THERMAL_PARAMS` and the assign-entity schema (further
down `services.py`) already apply `vol.Range` with an explicit max on
every comparable numeric field checked (`day_start_hour` 0-23,
`day_end_hour` 0-24, `manual_setpoint` 0-30, `comfort_temp_day` 5-30,
`dhw_min_temperature` 35-55, `heat_pump_cop_nominal` 1.0-8.0) — these are
**guarded**, confirming the package's general pattern is to range-bound
service inputs; `apply_manual_plan`'s `expires_at` is the outlier that
skips it.

## Null control

The guarded fields above (all with `vol.Range(min=..., max=...)`) show the
enumerator does not flag every optional field indiscriminately — only
fields that both lack a `vol.Range` max AND persist a lasting effect are
candidates, and only `expires_at` clears both.

## Perturbation

Not independently re-run; the finding's own harness
(`tools/audit/round9/D1/leads/manual_plan_expiry.py`) already carries the
executed evidence ("apply_manual_plan accepts expires_at past the horizon:
the override owns all 96 steps unenforced").

## Disposition

| seam | disposition |
|---|---|
| services.py:867 `handle_apply_manual_plan`'s `expires_at` | instance — D1-s2-54 |
| services.py:86-111 `SERVICE_SCHEMA_SIMULATE_PLAN` (6 unbounded fields) | not applicable — read-only, no persisted/actuating effect |
| services.py `SERVICE_SCHEMA_SET_THERMAL_PARAMS`, assign-entity (range-bound fields) | guarded — already `vol.Range`-clamped |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: clamp `expires_at` to
`now + MANUAL_PLAN_WINDOW_HOURS` (or the plan horizon) at
`build_override`/`handle_apply_manual_plan` — left for the fixer.

## Gate seconds

~0.02s (two grep invocations).
