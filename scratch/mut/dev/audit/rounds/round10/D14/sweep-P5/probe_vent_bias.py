"""Probe for P5 seam coordinator._vent_cusum (D2-s3-72).

A closed window with a heat-loss model that is merely biased gives a
sustained colder-than-predicted replay residual. The detector is fed that
residual (coordinator.py, clipped at VENT_CUSUM_CLIP_C) and its trip freezes
every learner with reason "ventilation", including the one that would
remove the bias. Property: pure model bias, no ventilation, must not trip.
Fails today for any sustained bias above VENT_CUSUM_DRIFT_C (0.08 K/interval).
Null control: bias 0.0 -> no trip. Perturbation: bias 0.05 vs 0.10 flips it.
"""
import sys, importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
pkg = Path(__file__).resolve().parents[6] / "custom_components/heatpump_optimizer"
spec = importlib.util.spec_from_file_location("drift", pkg / "drift.py"); drift = importlib.util.module_from_spec(spec); sys.modules["drift"] = drift; spec.loader.exec_module(drift)
import re
const = (pkg / "const.py").read_text()
TH = float(re.search(r"VENT_CUSUM_THRESHOLD_C: Final = ([\d.]+)", const).group(1))
DR = float(re.search(r"VENT_CUSUM_DRIFT_C: Final = ([\d.]+)", const).group(1))

def trips(bias: float, n: int = 96) -> bool:
    c = drift.Cusum(threshold=TH, drift=DR, side=-1)
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(n):
        c.update(t + timedelta(minutes=15 * i), max(-TH / 2, min(TH / 2, -bias)))
    return c.tripped

null = trips(0.0); small = trips(0.05); bias = trips(0.10)
print(f"null(0.00)={null} below_drift(0.05)={small} model_bias(0.10)={bias}")
ok = not null and not small and not bias
print("PROBE", "PASS" if ok else "FAIL: model bias with no ventilation trips the open-window freeze")
sys.exit(0 if ok else 1)
