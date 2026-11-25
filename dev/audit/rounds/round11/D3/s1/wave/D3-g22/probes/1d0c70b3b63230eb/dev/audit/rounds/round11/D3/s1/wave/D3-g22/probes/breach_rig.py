"""Box D3-g22 breach-report rig: calls HeatPumpOptimizer._publish_breach_reports (baseline or an in-memory mutant)
on a minimal result record and returns the published breach figures, or the exception name."""
from types import SimpleNamespace
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer

OPT = rig.bare_optimizer()


def publish(fn, *, traj, tmin, n, caps=None, sb=False, db=False, req=None, dtraj=None):
    res = SimpleNamespace(sensor_trajectory=lambda two_zone: list(traj), dhw_temp_trajectory=dtraj,
                          predictive_info={})
    OPT._dhw_requirement = None if req is None else np.asarray(req, dtype=float)
    try:
        fn(OPT, res, None if caps is None else np.asarray(caps, float), sb, db, n, np.asarray(tmin, float))
    except Exception as e:
        return type(e).__name__
    return {k: v for k, v in res.predictive_info.items() if "breach" in k}


def mutant(old, new):
    return rig.mutant(HeatPumpOptimizer, "_publish_breach_reports", old, new)


BASE = HeatPumpOptimizer._publish_breach_reports
