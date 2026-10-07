"""l3_write_only_scratch: ThermalModel per-step scratch members that production writes and no
production consumer reads.

Metric (one line): ThermalModel._step_* members with >=1 production write and 0 consumer reads
during the solves, a consumer read being a get whose caller frame is under custom_components/ in
a function that never writes that member (a step function re-reading its own accumulator is not a
consumer); key = the runtime descriptor's caller frames, not source text.
Drive: tests/golden.py capture() of winter_single_dhw, dhw_cold_tank, wood_two_tank, wood_coil
(real HeatPumpOptimizer.optimize solves), plus a static AST count of Attribute loads outside
thermal_model.py (tests excluded).
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py [--perturb reader]
Expected: write_only_members=4 of 5 (exact: _step_dhw_refused, _step_dhw_floor_injected,
          _step_dhw_draw_kw, _step_wood_refused); live control _step_buffer_refused has consumer
          reads > 0 (simulate_trajectory); --perturb reader (a one-line production reader of
          _step_dhw_draw_kw in simulate_trajectory, compiled under thermal_model.py) -> 3 of 5.
Tests read them: tests/features.py (grep count printed as test_file_refs).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbol: heatpump_optimizer.thermal_model:ThermalModel._step_dhw_refused (and the other 4).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, sys, time
from collections import defaultdict
from pathlib import Path
sys.path[:0] = ["tests", "custom_components"]
t0p, t0t = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "reader"
import golden  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

PKG = str(Path("custom_components/heatpump_optimizer").resolve())
ATTRS = ["_step_buffer_refused", "_step_dhw_refused", "_step_dhw_floor_injected", "_step_dhw_draw_kw", "_step_wood_refused"]
writers = defaultdict(set)
reads = defaultdict(lambda: defaultdict(int))
writes = defaultdict(int)


def _install(name):
    slot = "__l3_" + name
    default = getattr(tm.ThermalModel, name)

    def fget(self):
        f = sys._getframe(1)
        if os.path.realpath(f.f_code.co_filename).startswith(PKG):
            reads[name][f.f_code.co_qualname] += 1
        return self.__dict__.get(slot, default)

    def fset(self, v):
        f = sys._getframe(1)
        if os.path.realpath(f.f_code.co_filename).startswith(PKG):
            writers[name].add(f.f_code.co_qualname)
            writes[name] += 1
        self.__dict__[slot] = v
    setattr(tm.ThermalModel, name, property(fget, fset))


for a in ATTRS:
    _install(a)

if PERTURB:
    _orig = tm.ThermalModel.simulate_trajectory
    ns = {"_orig": _orig}
    code = ("def simulate_trajectory(self, *a, **k):\n"
            "    out = _orig(self, *a, **k)\n"
            "    self._l3_seen = self._step_dhw_draw_kw\n"
            "    return out\n")
    exec(compile(code, tm.__file__, "exec"), ns)
    tm.ThermalModel.simulate_trajectory = ns["simulate_trajectory"]

for name in ("winter_single_dhw", "dhw_cold_tank", "wood_two_tank", "wood_coil"):
    golden.capture(name, golden.SCENARIOS[name])

# static: Attribute loads of these names in production modules other than thermal_model.py
static_outside = 0
for p in Path("custom_components/heatpump_optimizer").glob("*.py"):
    if p.name == "thermal_model.py":
        continue
    for n in ast.walk(ast.parse(p.read_text())):
        if isinstance(n, ast.Attribute) and n.attr in ATTRS and isinstance(n.ctx, ast.Load):
            static_outside += 1
test_refs = sum(Path("tests/features.py").read_text().count(a) for a in ATTRS[1:])

dead = 0
for a in ATTRS:
    consumers = {fn: c for fn, c in reads[a].items() if fn not in writers[a]}
    is_dead = writes[a] > 0 and not consumers
    dead += is_dead and a != "_step_buffer_refused"
    print(f"member {a:26s} writes={writes[a]:8d} writers={sorted(writers[a])} "
          f"self_reads={sum(c for fn, c in reads[a].items() if fn in writers[a])} consumer_reads={dict(consumers)} write_only={is_dead}")
ctl = sum(c for fn, c in reads["_step_buffer_refused"].items() if fn not in writers["_step_buffer_refused"])
print(f"RESULT write_only_members={dead} of {len(ATTRS)} count")
print(f"RESULT live_control_buffer_consumer_reads={ctl} count")
print(f"RESULT static_loads_outside_thermal_model={static_outside} count")
print(f"RESULT test_file_refs={test_refs} count")
print(f"RESULT perturbed={int(PERTURB)}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
