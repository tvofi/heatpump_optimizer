import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np, golden
from heatpump_optimizer.optimizer import count_compressor_starts as c
moved = 0
for name, spec in golden.SCENARIOS.items():
    cap = golden.capture(name, dict(spec))
    sp = np.asarray(cap.get("power_schedule") or [], float)
    dh = np.asarray(cap.get("dhw_power_schedule") or np.zeros_like(sp), float)
    if dh.size != sp.size: dh = np.zeros_like(sp)
    t = sp + dh
    a, b = c(t), c(t, 0.2)
    band = int(((t > 0.1) & (t <= 0.2)).sum())
    if a != b: moved += 1
    print(f"{name:32s} starts@0.1={a} starts@0.2={b} steps_in_(0.1,0.2]={band} published={cap.get('compressor_starts')}", flush=True)
print(f"RESULT scenarios_whose_starts_move_at_0.2={moved}")
