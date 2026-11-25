import numpy as np
from custom_components.heatpump_optimizer import optimizer as opt
from custom_components.heatpump_optimizer.external_heat import ExternalHeatObservation
OLD, NEW = "return arr if bool(np.any(arr > 0.0)) else None", "return arr if bool(np.any(arr >= 0.0)) else None"
MUT = mutant_method("_external_heat_forecast", OLD, NEW)
T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def suppressing_coord(**kw):
    c = coord(wood_furnace_enabled=True, external_heat_detection_enabled=True)
    c._external_heat.config.enabled = True
    o = dict(now=T0, dhw_temp=None, buffer_temp=None, commanded_power_kw=0.0, measured_power_kw=0.0,
             override=True, outlet_temp=None, wood_top=None, wood_bottom=None, hp_tank_temp=None, space_demand_kw=5.0)
    o.update(kw)
    c._external_heat.update(ExternalHeatObservation(**o))
    return c


def horizon(arr, n=96):
    """optimizer._horizon_weather, the solve's one reader of ForecastSeries.external_heat_kw."""
    s = opt.ForecastSeries(prices=np.ones(n), outdoor_temps=np.zeros(n), wind_speeds=np.zeros(n),
                           precipitation=np.zeros(n), solar_radiation=np.zeros(n), external_heat_kw=arr)
    return opt._horizon_weather(s, n).external_heat_kw


cases = {
    # the user's flag says a fire burns, no outlet/wood probes: suppressing, displacement 0, free heat 0
    "override_on_no_wood_probes": suppressing_coord(),
    # probes present but wood side below the pump tank + margin: displacement 0
    "override_on_cold_wood_tank": suppressing_coord(outlet_temp=40.0, wood_top=41.0, wood_bottom=40.0, hp_tank_temp=40.0),
}
moved_symbol = moved_solve = 0
for name, c in cases.items():
    b, m = CLS._external_heat_forecast(c, 96), MUT(c, 96)
    hb, hm = horizon(b), horizon(m)
    moved_symbol += int((b is None) != (m is None))
    moved_solve += int((hb is None) != (hm is None) or (hb is not None and not np.array_equal(hb, hm)))
    print(f"RESULT {name} suppressing={c._external_heat.suppressing} free_heat_kw={c._external_heat.state.free_heat_kw} "
          f"symbol_baseline={'None' if b is None else 'array'} symbol_mutant={'None' if m is None else 'zeros[%d]' % len(m)} "
          f"solve_input_baseline={hb} solve_input_mutant={hm}")
print(f"RESULT reach=line_5259_executed_by_this_probe count")
print(f"RESULT moved_at_symbol={moved_symbol} count")
print(f"RESULT moved_at_solve_input={moved_solve} count")
tail()
