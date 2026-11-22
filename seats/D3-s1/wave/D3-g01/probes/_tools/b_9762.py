

CLS = co.HeatPumpOptimizerCoordinator
NOON = co.dt_util.now().replace(hour=12, minute=0, second=0, microsecond=0)


def drive(fn, cfg, mode="auto", now=NOON, dt_minutes=None, plan=False, stale=None):
    """One _async_drive_pumps tick on a live coordinator; returns the pump service calls it made."""
    c = coord(**cfg)
    c._mode = mode
    if dt_minutes is not None:
        object.__setattr__(c._ctx, "_opt_config", co.replace(c._ctx._opt_config, time_step_minutes=dt_minutes))
    if plan:  # a fresh plan that started 2 h ago, heating every step
        stamps = [now - co.timedelta(hours=2) + co.timedelta(minutes=15 * i) for i in range(96)]
        c._optimization_result = SimpleNamespace(power_schedule=[2.0] * 96, dhw_power_schedule=[0.0] * 96, timestamps=stamps)
    if stale is not None:
        c._plan_is_stale = lambda: stale
    calls = []

    async def call(domain, service, data, *a, **k):
        calls.append((service, data["entity_id"]))

    c.hass.services.async_call = call
    with mock.patch.object(co.dt_util, "now", lambda: now):
        try:
            asyncio.run(fn(c))
        except Exception as err:
            calls.append(("raised", type(err).__name__))
    return calls


MUT = recompile(CLS, "_async_drive_pumps", "if not vvc_entity and not space_entity:", "if False:")
inputs = {
    "no_pumps": ({}, {}),
    "no_pumps_mode_off": ({}, {"mode": "off"}),
    "no_pumps_with_plan": ({}, {"plan": True, "stale": False}),
    "space_pump_held_stale": ({"space_circulation_pump_entity": "switch.space"}, {"plan": True, "stale": True}),
    "no_pumps_dhw_windows": ({"dhw_enabled": True, "dhw_schedule_enabled": True, "dhw_windows": "06:00-08:30"}, {}),
    "no_pumps_midnight": ({}, {"now": NOON.replace(hour=0)}),
}
moved = 0
for name, (cfg, kw) in inputs.items():
    b, m = drive(CLS._async_drive_pumps, cfg, **kw), drive(MUT, cfg, **kw)
    moved += b != m
    print(f"RESULT {name}_calls_baseline={b} mutant={m}")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT positive_control_calls={len(drive(MUT, {'vvc_pump_entity': 'switch.vvc'}))} count")
tail()
