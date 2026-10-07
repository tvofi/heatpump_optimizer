"""Reviewer r9c-rev-2018, round 2: my r1 harness's mutants, now run against the
head's OWN pin block (exec'd verbatim from tests/stress.py), not a re-implementation."""
import ast, contextlib, io, os, sys, textwrap
src = open(sys.argv[1]).read()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "timing_check")
base = ast.get_source_segment(src, fn)
start = src.index("    # The recorder's exemption, narrow in both directions")
end = src.index("# The single-scenario detection statistic (#346)")
end = src.rindex("\n", 0, src.rindex("# ====", 0, end))
pin = textwrap.dedent(src[start:end])
class Results:
    def __init__(self, n): self.checks = 0; self.failures = 0; self.names = []
    def check(self, name, cond, detail=""):
        self.checks += 1; self.failures += (not cond); self.names.append((name[:50], bool(cond))); return cond
MUTANTS = {"none": None,
  "T1 exempt passes too": ("if recording and not condition:", "if recording:"),
  "T2 env read inverted": ('== "1"', '!= "1"'),
  "T3 env default to recording": ('os.environ.get(CLOSURE_RECORDING_ENV) == "1"', "True"),
  "T4 never exempt": ("if recording and not condition:", "if False:")}
for name, m in MUTANTS.items():
    code = base if m is None else base.replace(*m)
    assert m is None or code != base, name
    R = Results("R")
    ns = {"os": os, "io": io, "contextlib": contextlib, "Results": Results, "R": R,
          "CLOSURE_RECORDING_ENV": "HPO_CLOSURE_RECORDING", "print": lambda *a, **k: None}
    exec(code, ns); exec(pin, ns)
    print(f"RESULT mutant={name!r} pin_checks={R.checks} pin_failures={R.failures} "
          f"-> {'baseline' if m is None else ('killed' if R.failures else 'SURVIVES')}")
print("RESULT env after pin:", repr(os.environ.get("HPO_CLOSURE_RECORDING")))
