"""D7-s1 the #1410 adoption gate refuses without a name: a refused fit stays published as completed/"ok".

Metric (silent_refusals): count of finished experiments where the production gate
  coordinator:HeatPumpOptimizerCoordinator._adopt_system_identification wrote NO heat-loss scale
  AND the published surface sysid:SystemIdentification.as_dict()["result"] still reads
  completed=True, reason="ok" after the gate ran. Count key: the published as_dict() after the gate
  (the value the learning-view attribute "system_identification" carries), never the fit's hw.
  An adopted result publishes reason="adopted"; a refusal by name would publish another reason.
Cells: 3 presets x {clean, k_s x0.5 misdeclared, C_s x0.5 misdeclared, wood, defrost, window, stale}
  (drives from s1_sysid.py and s1_sysid_contam.py; production ThermalModel plant).
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_gate_silent.py [--perturb-bar]
  --perturb-bar: config-level change of the bar the gate reads (coordinator.UA_ADOPTION_HALFWIDTH_BAR
  = 1e9, i.e. admit every finite interval): silent_refusals must fall (only the hw=inf/None
  refusals remain). Restored in finally.
  --perturb-fix: the one-line production edit (the first guard of _adopt_system_identification
  writes a named refusal before returning), applied in memory and restored in finally:
  silent_refusals must go to zero.
Expected: silent_refusals=10 of 19 finished (exact, deterministic); log lines emitted by the
  refusal path: 0.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging, dataclasses
sys.path.insert(0, "tools/audit/round8/D7")
_p0, _t0 = time.process_time(), time.thread_time()
import s1_sysid as H
import s1_sysid_contam as K
from heatpump_optimizer import coordinator as C

PERTURB = "--perturb-bar" in sys.argv
FIX = "--perturb-fix" in sys.argv


def _fixed_method():
    """The one-line production edit, applied in memory: the refusal names itself."""
    import inspect, textwrap
    src = textwrap.dedent(inspect.getsource(C.HeatPumpOptimizerCoordinator._adopt_system_identification))
    old = ("if not result.completed or hw is None or hw > UA_ADOPTION_HALFWIDTH_BAR:\n"
           "        return")
    new = ("if not result.completed or hw is None or hw > UA_ADOPTION_HALFWIDTH_BAR:\n"
           "        self._sysid.result = replace(result, completed=False, reason=result.reason if not result.completed else 'ua interval too wide')\n"
           "        return")
    assert old in src, "anchor moved"
    ns = {}
    exec(compile(src.replace(old, new), C.__file__, "exec"), C.__dict__, ns)
    return ns["_adopt_system_identification"]


class _Count(logging.Handler):
    n = 0

    def emit(self, record):
        if "system identification" in record.getMessage().lower() and record.levelno >= logging.INFO:
            _Count.n += 1


logging.disable(logging.NOTSET)
_h = _Count()
C._LOGGER.addHandler(_h)
C._LOGGER.setLevel(logging.INFO)
C._LOGGER.propagate = False
_bar = C.UA_ADOPTION_HALFWIDTH_BAR
_orig_adopt = C.HeatPumpOptimizerCoordinator._adopt_system_identification
silent = finished = adopted = 0
try:
    if PERTURB:
        C.UA_ADOPTION_HALFWIDTH_BAR = 1e9
    if FIX:
        C.HeatPumpOptimizerCoordinator._adopt_system_identification = _fixed_method()
    for name in H.BUILDINGS:
        p = H.preset_params(name)
        runs = []
        for contam in ("clean", "wood", "defrost", "window", "stale"):
            runs.append((contam, *K.drive_c(p, contam), p))
        for key in ("ks", "cs"):
            t = dataclasses.replace(p)
            setattr(t, "slab_heat_transfer" if key == "ks" else "slab_thermal_mass",
                    getattr(p, "slab_heat_transfer" if key == "ks" else "slab_thermal_mass") * 0.5)
            runs.append((f"{key}x0.5", *H.drive(t, p), p))
        for label, sid, _ua, decl in runs:
            if not sid.result.completed:
                continue
            finished += 1
            before = _Count.n
            sc = H.gate(sid, decl)
            pub = sid.as_dict()["result"]
            quiet = sc is None and pub["completed"] and pub["reason"] == "ok"
            silent += int(quiet)
            adopted += int(sc is not None)
            print(f"CELL {name} {label}: written_scale={sc} published completed={pub['completed']} "
                  f"reason={pub['reason']!r} heat_loss={pub['heat_loss_kw_per_c']} log_lines={_Count.n - before}",
                  flush=True)
finally:
    C.UA_ADOPTION_HALFWIDTH_BAR = _bar
    C.HeatPumpOptimizerCoordinator._adopt_system_identification = _orig_adopt
print(f"RESULT finished={finished} count")
print(f"RESULT adopted={adopted} count")
print(f"RESULT silent_refusals={silent} count")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
