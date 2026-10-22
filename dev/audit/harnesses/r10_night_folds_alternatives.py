"""Measure the two internal-gains branches the RCA named, on this tree.

(a) "feed it the residual net of the UA fold's dT-proportional part": the UA
    fold's Newton target attributes the WHOLE residual to dT
    (dUA = -e*C/(dT*dt)), so the net residual the shape would see is zero.
(b) "regularise it until the probe stays under 5 %": raise the ridge until the
    enumerator's own probe passes, then re-read the positive arm.

Command (tree root): PYTHONPATH=tests/hastub:custom_components:tests python3 \\
    dev/audit/harnesses/r10_night_folds_alternatives.py
This is a measurement record, not a gate.
"""
import sys
from datetime import datetime, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer import coordinator as co  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator as Coord,
)
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

UTC = timezone.utc
T0 = datetime(2026, 1, 15, 19, 0, tzinfo=UTC)
G0 = 0.3


class Seat:
    """The coordinator attributes ``_fold_internal_gains`` reads."""

    def __init__(self):
        self._config = type("C", (), {"internal_gains_learning_enabled": True})()
        self._thermal_params = type(
            "P", (), {"two_zone_enabled": False, "internal_gains": G0,
                      "room_thermal_mass": 10.0, "upper_floor_thermal_mass": 10.0,
                      "heat_loss_coefficient": 0.15,
                      "upper_floor_heat_loss": 0.15}
        )()
        self._internal_gains_profile = None
        self._house_heat_loss_samples = 400


def drive(seat, residual_fn, n=400):
    dark = ThermalState(room_temperature=21.0, outdoor_temperature=0.0)
    for _ in range(n):
        held = (seat._internal_gains_profile or [G0] * 24)[19]
        Coord._fold_internal_gains(
            seat, T0, dark, residual_fn(held), 0.5
        )
    prof = seat._internal_gains_profile or [G0] * 24
    return max(abs(g - G0) for g in prof) / G0


# The +10 % UA error drive: dT = 20 K, U = 0.15, C = 10, dt = 0.5 h.
dT, U, C, DT = 20.0, 0.15, 10.0, 0.5
ua_error_residual = -0.10 * U * dT * DT / C

print("RESULT same_residual.rel_dev=%.4f" % drive(Seat(), lambda held: ua_error_residual))
print("RESULT positive.rel_dev=%.4f" % drive(Seat(), lambda held: (0.6 - held) * DT / C))

# (a) subtract the UA fold's dT-proportional part: it is the whole residual.
def net_of_ua_fold(held):
    implied_dua = -ua_error_residual * C / (dT * DT)
    return ua_error_residual + implied_dua * dT * DT / C


print("RESULT net_of_ua_part.rel_dev=%.4f" % drive(Seat(), net_of_ua_fold))
print("RESULT net_of_ua_part.positive_rel_dev=%.4f"
      % drive(Seat(), lambda held: net_of_ua_fold((0.6 - held) * DT / C)))

# (b) a ridge that keeps the UA-error drive under 5 %.
for ridge in (0.02, 0.5, 1.0, 1.5, 2.0):
    co.INTERNAL_GAINS_RIDGE = ridge
    ua = drive(Seat(), lambda held: ua_error_residual)
    pos = drive(Seat(), lambda held: (0.6 - held) * DT / C)
    print(f"RESULT ridge{ridge:.2f}.ua_rel_dev={ua:.4f} positive_rel_dev={pos:.4f}")
co.INTERNAL_GAINS_RIDGE = 0.02
