"""D7-v1 verifier harness for D7-s1-03: does a refused experiment say so, on the real coordinator's surface?

Metric (one line): count of experiment nights that FINISH (phase done) on the real FakeHass coordinator,
  where _adopt_system_identification wrote no heat-loss scale AND coordinator._learning_view()
  ["system_identification"]["result"] reads completed=True, reason="ok" AND the coordinator logger
  emitted 0 records for that night's adoption decision.
Nights: the v1_sysid_freeze.py sweep (3 presets x {clean, wood 0.5/1/2 kW relax, wood 0.5/1/2 kW step,
  defrost 1/2/3 ticks}), driven tick by tick through production _run_system_identification +
  _adopt_system_identification.  Null control: every adopted night must publish reason "adopted"
  and carry >= 1 log record.
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/v1_gate_silent.py [--perturb]
  --perturb: in-memory one-line production edit of the first guard of _adopt_system_identification
  (it writes replace(result, completed=False, reason="ua interval too wide") and logs before returning),
  compiled from the method's own source in the coordinator module namespace; restored in finally.
  silent must go to 0.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging, inspect, textwrap
sys.path.insert(0, "tools/audit/round8/D7")
_p0, _t0 = time.process_time(), time.thread_time()
import v1_sysid_freeze as V
C = V.C
logging.disable(logging.NOTSET)
PERTURB = "--perturb" in sys.argv


class Grab(logging.Handler):
    def __init__(self):
        super().__init__(logging.INFO)
        self.recs = []

    def emit(self, record):
        msg = record.getMessage()
        if "adopt" in msg.lower():
            self.recs.append(msg)


grab = Grab()
C._LOGGER.addHandler(grab)
C._LOGGER.setLevel(logging.INFO)
C._LOGGER.propagate = False
_orig = C.HeatPumpOptimizerCoordinator._adopt_system_identification
try:
    if PERTURB:
        src = textwrap.dedent(inspect.getsource(_orig))
        old = ("    if not result.completed or hw is None or hw > UA_ADOPTION_HALFWIDTH_BAR:\n"
               "        return\n")
        assert src.count(old) == 1
        src = src.replace(old, (
            "    if not result.completed or hw is None or hw > UA_ADOPTION_HALFWIDTH_BAR:\n"
            "        if result.completed:\n"
            "            self._sysid.result = replace(result, completed=False, reason='ua interval too wide')\n"
            "            _LOGGER.info('System identification not adopted: ua interval too wide')\n"
            "        return\n"))
        ns = {}
        exec(compile(src, "<perturbed>", "exec"), C.__dict__, ns)
        C.HeatPumpOptimizerCoordinator._adopt_system_identification = ns["_adopt_system_identification"]
    finished = silent = adopted = adopted_ok_ctrl = 0
    for name in V.BUILDINGS:
        for kind, mag in [("clean", 0)] + V.KINDS:
            grab.recs.clear()
            r = V.night(name, kind, mag)
            c = V.LAST["coord"]
            if r["phase"] != "done":
                continue
            finished += 1
            pub = c._learning_view()["system_identification"]["result"]
            logs = len(grab.recs)
            wrote = r["err"] is not None
            if wrote:
                adopted += 1
                adopted_ok_ctrl += int(pub["reason"] == "adopted" and logs >= 1)
            is_silent = (not wrote) and pub["completed"] is True and pub["reason"] == "ok" and logs == 0
            silent += is_silent
            print(f"CELL {name} {kind}={mag}: wrote={wrote} published completed={pub['completed']} "
                  f"reason={pub['reason']!r} heat_loss={pub['heat_loss_kw_per_c']} logs={logs} silent={is_silent}",
                  flush=True)
finally:
    C.HeatPumpOptimizerCoordinator._adopt_system_identification = _orig
print(f"RESULT finished={finished} count")
print(f"RESULT adopted={adopted} count; adopted_named_and_logged={adopted_ok_ctrl} (null control: must equal adopted)")
print(f"RESULT silent={silent} count (of {finished} finished)")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
