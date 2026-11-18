"""Null control for the R5-D2-02 fix: the buffer substep term must change the
step count ONLY for the throttled two-zone families whose tank is small enough
to be stiff, and must leave every other family's count -- hence its trajectory,
bitwise -- untouched.

Reimplements the PRE-FIX `_stability_substeps` ratio rule and compares it to
the shipped one for every harness family at the harness's own weather samples.

Run from the worktree root: PYTHONPATH=tests/hastub python3 <this>
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.path.insert(0, os.path.join(os.path.abspath(os.getcwd()), "tools/audit/round5/D2/seat-a"))

from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    EULER_STABILITY_MAX_RATIO,
)
import d2a_common as C  # noqa: E402


def base_n_sub(model, wind, rain, dt):
    """The pre-fix rule: four boundary-floored masses only."""
    p = model.params
    if p.two_zone_enabled:
        u_upper = model.effective_heat_loss_coefficient(p.upper_floor_heat_loss, wind, rain)
        u_lower = model.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, wind * 0.5, rain * 0.5)
        worst = max(
            (u_upper + p.inter_zone_transfer) / p.upper_floor_thermal_mass,
            (u_lower + p.inter_zone_transfer + p.slab_heat_transfer) / p.lower_floor_thermal_mass,
            p.slab_heat_transfer / p.slab_thermal_mass,
        )
    else:
        u_eff = model.effective_heat_loss_coefficient(p.heat_loss_coefficient, wind, rain)
        worst = max(
            (u_eff + p.slab_heat_transfer) / p.room_thermal_mass,
            p.slab_heat_transfer / p.slab_thermal_mass,
        )
    ratio = worst * dt
    if ratio <= EULER_STABILITY_MAX_RATIO:
        return 1
    return int(np.ceil(ratio / EULER_STABILITY_MAX_RATIO))


def main():
    fams = C.build_families()
    wind = np.linspace(0.0, 6.0, 48)
    rain = np.linspace(0.0, 2.0, 48)
    dt = 0.25
    for name, b in fams.items():
        model = b["optimizer"].model
        # the harness's own weather vectors, if it carries them; else the sweep
        wi = getattr(b, "get", lambda *_: None)
        rows = []
        for k in range(0, len(wind), 6):
            w, r = float(wind[k]), float(rain[k])
            rows.append((model._stability_substeps(w, r, dt), base_n_sub(model, w, r, dt)))
        new = sorted({a for a, _ in rows})
        old = sorted({c for _, c in rows})
        print("RESULT family=%-18s n_sub_fix=%-10s n_sub_base=%-10s n_sub_buf=%.3f" % (
            name, new, old,
            model.params.max_electrical_power * max(model.params.cop_nominal, 1.0)
            / max(model.params.emitter_design_delta_t, 1.0) / model.params.buffer_tank_thermal_mass * dt
            if model.params.buffer_tank_thermal_mass > 0 else -1.0))


if __name__ == "__main__":
    main()
