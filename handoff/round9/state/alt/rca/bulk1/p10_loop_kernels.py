"""P10 detector prototype: model-kernel calls made in the Home Assistant
interpreter outside the process worker, counted per route, on a replayed day.

METRIC: kernel_calls[route] where a kernel is any ThermalModel.simulate_*
method and route is
  worker   -- inside process_worker.run_worker (the #199/#290 process route; allowed)
  executor -- inside hass.async_add_executor_job, not in the worker
              (a GIL-holding thread in the parent: R1 D9-02/R2 D9-05/R3 D9-03/R5 D9-06 shape)
  loop     -- neither (inline on the event loop: R9 D9-s1-03/D9-s2-01 shape)
keyed on the innermost production frame outside thermal_model.py.
Counts, not time: no timing, no BLAS dependence.
ARMS: base (tree as is); fixed (sensor._sensor_advisor_attribute returns {},
standing in for moving #1658 D9-s2-01 off the loop); fallback (_ensure_worker
raises ProcessWorkerUnavailable: the #511 fallback route, #783/#1337 shape).
Run from a tree root: PYTHONPATH=tests/hastub:tests:custom_components python3 <this> <arm> [hours]
"""
import sys, threading, collections, json, tempfile
from pathlib import Path
from datetime import timedelta, datetime
arm = sys.argv[1]; hours = float(sys.argv[2]) if len(sys.argv) > 2 else 3
import replay, harness
from heatpump_optimizer import thermal_model as tm, process_worker as pw, coordinator as cm
from heatpump_optimizer import sensor as sensor_mod
TL = threading.local()
counts = collections.Counter(); sites = collections.Counter()
def route():
    if getattr(TL, "worker", 0): return "worker"
    if getattr(TL, "executor", 0): return "executor"
    return "loop"
def site():
    f = sys._getframe(2)
    while f is not None:
        fn = f.f_code.co_filename.replace("\\", "/")
        if "/heatpump_optimizer/" in fn and not fn.endswith("thermal_model.py"):
            return f"{Path(fn).name}:{f.f_code.co_name}"
        f = f.f_back
    return "?"
for name in ("simulate_step", "simulate_trajectory", "simulate_trajectory_batch",
             "simulate_trajectory_with_dhw", "simulate_dhw_step", "simulate_dhw_only"):
    real = getattr(tm.ThermalModel, name)
    def wrap(self, *a, _real=real, **k):
        if not getattr(TL, "inside", 0):
            r = route(); counts[r] += 1
            if r != "worker": sites[(r, site())] += 1
        TL.inside = getattr(TL, "inside", 0) + 1
        try: return _real(self, *a, **k)
        finally: TL.inside -= 1
    setattr(tm.ThermalModel, name, wrap)
real_rw = pw.run_worker
def run_worker(*a, **k):
    TL.worker = getattr(TL, "worker", 0) + 1
    try: return real_rw(*a, **k)
    finally: TL.worker -= 1
pw.run_worker = run_worker
real_ex = harness.FakeHass.async_add_executor_job
async def ex(self, func, *args):
    TL.executor = getattr(TL, "executor", 0) + 1
    try: return await real_ex(self, func, *args)
    finally: TL.executor -= 1
harness.FakeHass.async_add_executor_job = ex
if arm == "fixed":
    sensor_mod._sensor_advisor_attribute = lambda coordinator: {}
src = json.loads(Path("tests/replay/synthetic-dhw-only.json").read_text())
start = datetime.fromisoformat(src["window"]["start"])
src["window"]["end"] = (start + timedelta(hours=hours)).isoformat()
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "fx.json"; p.write_text(json.dumps(src))
    if arm == "fallback":
        real_run = replay.run_fixture
        def patched_ensure():
            raise cm.ProcessWorkerUnavailable("forced by p10 fallback arm")
        # run_fixture installs its own worker; override after it by wrapping _await_process
        real_await = cm._await_process
        async def failing_await(hass, fn, *args):
            raise cm.ProcessWorkerUnavailable("forced by p10 fallback arm")
        cm._await_process = failing_await
    run = replay.run_fixture(p, 30)
print(f"RESULT arm={arm} cycles={run['cycles']} worker={counts['worker']} "
      f"executor={counts['executor']} loop={counts['loop']}")
for (r, s), n in sorted(sites.items(), key=lambda x: -x[1]):
    print(f"  SITE {r:8s} {s:55s} {n}")
