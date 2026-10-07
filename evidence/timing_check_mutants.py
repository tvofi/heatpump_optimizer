"""Reviewer r9c-rev-2018's own harness: extracts stress.py's timing_check and
re-runs stress.py's own pin (lines ~3284-3298) against mutants of it, plus a
gate-shaped call (env absent, recording omitted) the pin does not make."""
import ast, contextlib, io, os, sys
src = open(sys.argv[1]).read()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "timing_check")
base = ast.get_source_segment(src, fn)
class Results:
    def __init__(self, n): self.checks = 0; self.failures = 0
    def check(self, name, cond, detail=""):
        self.checks += 1; self.failures += (not cond); return cond
MUTANTS = {
  "none": (None, None),
  "T1 exempt passes too": ("if recording and not condition:", "if recording:"),
  "T2 env read inverted": ('== "1"', '!= "1"'),
  "T3 env default to recording": ("os.environ.get(CLOSURE_RECORDING_ENV) == \"1\"", "True"),
  "T4 never exempt": ("if recording and not condition:", "if False:"),
}
for name, (a, b) in MUTANTS.items():
    code = base if a is None else base.replace(a, b)
    assert a is None or code != base, name
    ns = {"os": os, "R": Results("R"), "CLOSURE_RECORDING_ENV": "HPO_CLOSURE_RECORDING", "print": lambda *x, **k: None}
    exec(code, ns); tc = ns["timing_check"]
    g, r = Results("g"), Results("r")
    tc("probe", False, results=g, recording=False)
    tc("probe", False, results=r, recording=True)
    tc("probe", True, results=r, recording=True)
    pin = (g.failures, r.failures, r.checks) == (1, 0, 1)
    os.environ.pop("HPO_CLOSURE_RECORDING", None)
    gate = Results("gate"); tc("probe", False, results=gate)          # the gate: env absent
    os.environ["HPO_CLOSURE_RECORDING"] = "1"
    rec = Results("rec"); tc("probe", False, results=rec)              # the recorder: env set
    os.environ.pop("HPO_CLOSURE_RECORDING", None)
    env_ok = (gate.failures, rec.failures) == (1, 0)
    print(f"RESULT mutant={name!r} stress_pin={'pass' if pin else 'FAIL(killed)'} "
          f"gate_miss_fails={gate.failures==1} recorder_miss_exempt={rec.failures==0} "
          f"-> {'SURVIVES stress pin' if pin and name!='none' else ('baseline' if name=='none' else 'killed')}"
          f"{'' if env_ok else ' [gate/recorder behaviour WRONG]'}")
