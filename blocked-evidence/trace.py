import sys, io, contextlib
sys.argv = sys.argv[:1]; sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
from heatpump_optimizer import draw_range
C = h.HeatPumpOptimizerCoordinator
orig = C._learn_measured_cop
log = []
def wrap(self, draw):
    a=(draw,)
    before = self._cop_scale; r = orig(self, *a)
    log.append((round(before,3), round(self._cop_scale,3), len(self._measured_cop.probe), len(self._measured_cop.held), self._measured_cop.scale_response, r, draw_range.ask_evidence(a[0] if a else None)))
    return r
C._learn_measured_cop = wrap
with contextlib.redirect_stdout(io.StringIO()): h.flat_row("x", h.flat(140, 2.2))
for i,l in enumerate(log):
    if i<3 or 40<i<110 and (i%3==0 or l[0]!=l[1]): print(i,l)
