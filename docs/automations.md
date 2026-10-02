# Automations

Without a heat pump on/off switch — and without the ECL110 or
frequency-control paths — the optimizer's plan is published on sensors for
your own automations to act on ([configuration.md](configuration.md) says
exactly that where the trade-off is made). The examples below are complete and
use only entities and services this integration actually creates. Entity ids
are fixed at `sensor.heat_pump_optimizer_*` regardless of the name you gave the
entry, so they read `sensor.heat_pump_optimizer_cost_power_headroom` on every
install.

## Automation example: charge an EV from the Cost Power Headroom sensor

The Cost Power Headroom sensor (`sensor.heat_pump_optimizer_cost_power_headroom`) is
`min(main fuse, capacity threshold) − current house draw`, clamped at zero, in
kW — a number an EV charger can follow. It stays unavailable only while
nothing bounds the house: set a main fuse size in the options, or enable a
capacity tariff, and it appears — the fuse is unset by default, so a
tariff-only install has the sensor too. Until the month's first metering
window closes there is no reference peak yet, so a tariff-only install then
reads 0.0 kW — no kW is free while the month's peak is being set — and the
`limit_source` attribute reads `capacity tariff with no peak reference yet`,
which tells that state apart from a measured limit. With no fuse and no
capacity tariff it stays unavailable, and without a whole-house meter it only
sees the heat pump itself, which the sensor's attributes say out loud.

This automation starts a simple charger whenever at least 5 kW of headroom
opens up and stops it below 2 kW:

```yaml
automation:
  - alias: Charge the EV while the grid has headroom
    trigger:
      - platform: numeric_state
        entity_id: sensor.heat_pump_optimizer_cost_power_headroom
        above: 5
      - platform: numeric_state
        entity_id: sensor.heat_pump_optimizer_cost_power_headroom
        below: 2
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: sensor.heat_pump_optimizer_cost_power_headroom
                above: 2
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.ev_charger
        default:
          - service: switch.turn_off
            target:
              entity_id: switch.ev_charger
```

A charger with a dynamic current limit can instead follow the number directly,
writing it to the charger's current entity with `number.set_value`.

## Automation example: economy mode when electricity is expensive

The Cost Electricity Price (now) sensor
(`sensor.heat_pump_optimizer_cost_current_electricity_price`) publishes the hourly
spot price in your currency per kWh. `set_mode` accepts `auto`, `comfort`,
`economy`, `boost` and `off`: economy lets the plan ride out expensive hours up
to 1.5 °C below the comfort floor (never below 15 °C), and `auto` hands full
optimization back. Swap the thresholds for your market's prices:

```yaml
automation:
  - alias: Economy mode through the evening price peak
    trigger:
      - platform: numeric_state
        entity_id: sensor.heat_pump_optimizer_cost_current_electricity_price
        above: 0.40
        id: price_high
      - platform: numeric_state
        entity_id: sensor.heat_pump_optimizer_cost_current_electricity_price
        below: 0.25
        id: price_back_down
    action:
      - choose:
          - conditions:
              - condition: trigger
                id: price_high
            sequence:
              - service: heatpump_optimizer.set_mode
                data:
                  mode: economy
          - conditions:
              - condition: trigger
                id: price_back_down
            sequence:
              - service: heatpump_optimizer.set_mode
                data:
                  mode: auto
```

`set_mode` acts on every loaded entry at once and requests a fresh solve
immediately, so the new mode shows up in the plan straight away. The services
stay registered while every entry is unloaded; a call that then finds no
loaded entry fails with a validation error rather than doing nothing (see
[configuration.md](configuration.md)).

## Automation example: know when a manual plan is pinned

While an `apply_manual_plan` override is active, the plan sensors carry a
`manual_override` attribute with the expiry time; the attribute is absent
otherwise. This fires a notification when one appears:

```yaml
automation:
  - alias: Notify when a manual plan takes over
    trigger:
      - platform: state
        entity_id: sensor.heat_pump_optimizer_plan_space_heating
        attribute: manual_override
    condition:
      - "{{ trigger.to_state.attributes.get('manual_override') is not none }}"
    action:
      - service: notify.persistent_notification
        data:
          title: Manual plan active
          message: >-
            Heating slots are pinned until
            {{ state_attr('sensor.heat_pump_optimizer_plan_space_heating',
            'manual_override').expires_at }}.
```

The pins constrain timing only — safety still releases any slot the tank
minimum, the legionella clock or the comfort floor cannot honour, and released
slots are reported in the same `manual_override` attribute.

## Events: what the optimizer tells you

The integration fires five Home Assistant events, each once per occurrence, so
an automation decides where a message goes. Every event carries `entry_id`, the
config entry that fired it. What has been sent is remembered across restarts,
so a condition that is still true after a restart is not announced again, and an
unchanged refresh fires nothing. A condition that clears and comes back fires
again.

| Event | Fires when | Data |
|---|---|---|
| `heatpump_optimizer_monthly_receipt` | a month has closed and its receipt is published | `entry_id`, `month` (`YYYY-MM`), `total_sek`, `saving_sek` and `saving_pct` (against a plain thermostat, `null` when the month has no savings row), `currency` |
| `heatpump_optimizer_comfort_at_risk` | the coldest step of the plan is below your minimum temperature | `entry_id`, `predicted_min_c`, `at` (the step's time), `floor_c`, `peak_guard_suppressing` (the peak guard is holding heating back) |
| `heatpump_optimizer_input_stale` | a required input has not updated within its limit; once per input | `entry_id`, `input`, `age_minutes`, `max_age_minutes` |
| `heatpump_optimizer_plan_stale` | the plan is older than three solve cycles (at least 90 minutes) | `entry_id`, `age_minutes` |
| `heatpump_optimizer_manual_plan_released` | safety released slots of a manual plan; once per channel and override | `entry_id`, `channel` (`space` or `dhw`), `steps` (the released step numbers when it fired), `reason`, `expires_at` |

A receipt that already exists when the integration is updated to the release
that adds these events is not announced; the next month's is.

```yaml
automation:
  - alias: Tell me when the house may get cold
    trigger:
      - platform: event
        event_type: heatpump_optimizer_comfort_at_risk
    action:
      - action: notify.mobile_app_phone
        data:
          message: >-
            The plan expects {{ trigger.event.data.predicted_min_c }} °C,
            below your {{ trigger.event.data.floor_c }} °C minimum.
```

The blueprint below turns all five into messages for one notify target.

## Blueprints

The three examples above, and the events, are also shipped as importable Home Assistant blueprints,
taking the sensor and thresholds as inputs instead of the
hard-coded entity ids. Import them from Settings → Automations & Scenes →
Blueprints → Import Blueprint:

- [Charge an EV from grid headroom](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/charge_ev_from_grid_headroom.yaml) — from the first example above.
- [Economy mode through the evening price peak](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/economy_mode_on_price_peak.yaml) — from the second example above.
- [Notify when a manual plan takes over](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_on_manual_plan.yaml) — from the third example above.
- [Notifications](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notifications.yaml) — sends the five events above to a notify target, one switch per event, with quiet hours that the comfort alert passes through.
