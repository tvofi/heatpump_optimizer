## Automation examples

```yaml
automation:
  alias: Boost before prices spike
  trigger:
    - platform: state
      entity_id: sensor.heat_pump_optimizer_current_electricity_price
  action:
    - service: heatpump_optimizer.set_mode
      target:
        entity_id: climate.heat_pump_optimizer
      data:
        mode: boost
```
