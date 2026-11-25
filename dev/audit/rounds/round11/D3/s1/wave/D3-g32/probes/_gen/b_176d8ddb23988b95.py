import logging
from datetime import datetime, timezone
from custom_components.heatpump_optimizer import sysid

mut = mutate(sysid.SystemIdentification, "_finish", "        if self.result.completed:", "        if False:")
now = datetime(2026, 1, 14, 3, 0, tzinfo=timezone.utc)
done = sysid.SysIdResult(completed=True, time_constant_hours=40.0, heat_loss_kw_per_c=0.2,
                         thermal_mass_kwh_per_c=8.0, internal_gains_kw=0.3, confidence=0.8, reason="ok")
refused = sysid.SysIdResult(completed=False, reason="fit failed")


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.n = 0

    def emit(self, record):
        self.n += record.levelno >= logging.INFO


def finish(fn, outcome):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s._slab_pair = (8.0, 0.5)
    h = Count()
    sysid._LOGGER.addHandler(h)
    old = sysid._LOGGER.level
    sysid._LOGGER.setLevel(logging.DEBUG)
    try:
        with mock.patch.object(sysid.SystemIdentification, "identify_slab", lambda self: outcome):
            fn(s, now)
    finally:
        sysid._LOGGER.removeHandler(h)
        sysid._LOGGER.setLevel(old)
    return (s.phase, s.last_run, s.result.as_dict(), s._slab_fit_used), h.n


b, bl = finish(sysid.SystemIdentification._finish, done)
m, ml = finish(mut, done)
print(f"RESULT completed_state_moved={int(b != m)} count  (phase, last_run, result, routing flag)")
print(f"RESULT completed_info_logs_baseline={bl} mutant={ml}")
b, bl = finish(sysid.SystemIdentification._finish, refused)
m, ml = finish(mut, refused)
print(f"RESULT null_refused_state_moved={int(b != m)} count  info_logs_baseline={bl} mutant={ml}")
tail()
