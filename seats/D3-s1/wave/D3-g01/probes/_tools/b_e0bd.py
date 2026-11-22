

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


MUT = recompile(CLS, "_async_drive_pumps", "dt_hours = max(ctx._opt_config.dt_hours, 1e-6)",
                "dt_hours = (ctx._opt_config.dt_hours)")
cfg = {"space_circulation_pump_entity": "switch.space"}
b, m = drive(CLS._async_drive_pumps, cfg, plan=True, stale=False), drive(MUT, cfg, plan=True, stale=False)
print(f"RESULT production_step_calls_baseline={b}")
print(f"RESULT production_step_calls_mutant={m}")
for extra in ({}, {"time_step_minutes": 0}, {"time_step_minutes": 5}, {"horizon_hours": 48}):
    print(f"RESULT production_dt_hours config={extra}: {coord(**cfg, **extra)._ctx._opt_config.dt_hours}")
moved = 0
for dtm in (15.0, 5.0, 1.0, 1e-5, 6e-5, 1e-6, 0.0):
    bb = drive(CLS._async_drive_pumps, cfg, plan=True, stale=False, dt_minutes=dtm)
    mm = drive(MUT, cfg, plan=True, stale=False, dt_minutes=dtm)
    moved += bb != mm
    print(f"RESULT inputs step_minutes={dtm}: baseline={bb} mutant={mm}")
print(f"RESULT moved_direct_inputs={moved} count  (dt 0 only)")
print(f"RESULT null_delta={int(b != m)} count")
tail()
