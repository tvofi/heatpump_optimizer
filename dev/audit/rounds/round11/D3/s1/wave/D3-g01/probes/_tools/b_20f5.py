

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


MUT = recompile(CLS, "_async_drive_pumps", "if params.dhw_enabled and params.dhw_windows_active",
                "if params.dhw_enabled or params.dhw_windows_active")
VVC = {"vvc_pump_entity": "switch.vvc", "dhw_windows": "06:00-08:30"}
cases = {
    "dhw_disabled_vvc": {**VVC, "dhw_enabled": False, "dhw_schedule_enabled": True},
    "dhw_enabled_schedule_off_vvc": {**VVC, "dhw_enabled": True, "dhw_schedule_enabled": False},
}
for name, cfg in cases.items():
    print(f"RESULT {name}_baseline={drive(CLS._async_drive_pumps, cfg)}")
    print(f"RESULT {name}_mutant={drive(MUT, cfg)}")
cfg = cases["dhw_disabled_vvc"]
print(f"RESULT inputs dhw_disabled at 07:00: baseline={drive(CLS._async_drive_pumps, cfg, now=NOON.replace(hour=7))} "
      f"mutant={drive(MUT, cfg, now=NOON.replace(hour=7))}")
nulls = ({**VVC, "dhw_enabled": True, "dhw_schedule_enabled": True},
         {**VVC, "dhw_enabled": False, "dhw_schedule_enabled": False})
print(f"RESULT null_delta={sum(int(drive(CLS._async_drive_pumps, c) != drive(MUT, c)) for c in nulls)} count")
tail()
