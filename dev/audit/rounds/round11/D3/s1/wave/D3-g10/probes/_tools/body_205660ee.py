from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

NAME, OLD, NEW = "_thermal_view", "if ctx._thermal_params.two_tank_modelled:", "if False:"
KEYS = ("two_tank_modelled", "wood_tank_temperature")


def drive(mutated, two_tank):
    c = make_coord()
    c._current_state.wood_tank_temperature = 55.0
    with arm(NAME, OLD, NEW, mutated), \
            mock.patch.object(ThermalParameters, "two_tank_modelled", new_callable=mock.PropertyMock, return_value=two_tank):
        view = c._thermal_view()
    return sum(k in view for k in KEYS), view.get("wood_tank_temperature")


b, m = drive(False, True), drive(True, True)
print(f"RESULT two_tank_baseline={b[0]} keys wood={b[1]}")
print(f"RESULT two_tank_mutant={m[0]} keys wood={m[1]}")
print(f"RESULT null_moved={int(drive(False, False) != drive(True, False))} count (two_tank_modelled False)")
tail()
