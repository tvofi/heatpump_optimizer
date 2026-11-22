from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

NAME = "_update_current_state"
WOOD = {"wood_tank_top_entity": "sensor.wood_top", "wood_tank_bottom_entity": "sensor.wood_bottom"}
# The wood probe per cycle: healthy, healthy, unavailable, unavailable, healthy.
SEQ = ("60.0", "60.0", "unavailable", "unavailable", "58.0")


def drive(mutated, seq=SEQ):
    """Five _update_current_state cycles; (warnings, infos, format errors, wood temperature per cycle)."""
    c = make_coord(WOOD, {"sensor.wood_top": FakeState("60.0", unit="°C"),
                          "sensor.wood_bottom": FakeState("50.0", unit="°C")})
    temps = []
    with arm(NAME, OLD, NEW, mutated), \
            mock.patch.object(ThermalParameters, "two_tank_modelled", new_callable=mock.PropertyMock, return_value=True), \
            counting("ood tank") as wood_log, counting("Two-tank model active") as two_log:
        for v in seq:
            for eid in ("sensor.wood_top", "sensor.wood_bottom"):
                c.hass.states.set(eid, FakeState(v, unit="°C"))
            asyncio.run(c._update_current_state())
            t = c._current_state.wood_tank_temperature
            temps.append(None if t is None else round(t, 3))
    hits = wood_log.hits + [h for h in two_log.hits if h not in wood_log.hits]
    warn = sum(1 for lv, _ in hits if lv == "WARNING")
    info = sum(1 for lv, _ in hits if lv == "INFO")
    fmt = sum(1 for _, msg in hits if msg.startswith("<format error>"))
    return warn, info, fmt, tuple(temps)


b, m = drive(False), drive(True)
print(f"RESULT wood_logs_baseline=(warnings,infos,format_errors,temps){b}")
print(f"RESULT wood_logs_mutant=(warnings,infos,format_errors,temps){m}")
print(f"RESULT temps_moved={int(b[3] != m[3])} count")
print(f"RESULT null_moved={int(drive(False, NULL) != drive(True, NULL))} count (null input {NULL})")
tail()
