import numpy as np
from heatpump_optimizer import draw_range as D
rng = np.random.default_rng(1)
for gate_draw in (0.30, 0.9, 1.4):
    d = D.DrawRange()
    for _ in range(48): d.observe_idle(gate_draw + rng.normal(0, 0.03))
    for i in range(72):
        asked = [1.5, 2.0, 3.0][i % 3]
        drawn = 0.9 * asked   # follows the ask, sub-ceiling commanded
        d.observe(drawn, asked, 1.5, 5.0, (35.0, 55.0))
    ev = d._evidence()
    print(f"gate-held draw {gate_draw}: idle_kw {d.idle_kw():.2f} evidence {len(ev)}/72 observed {d.observed()} follows_ask {D.follows_ask(d)}")
