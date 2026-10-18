"""Review-2 seat: does a sweep re-run at an OLD head cancel the NEW head's code run?
    python3 -I tools/sweep_crosshead.py <rev1>/measure/rev
The sim's sweep fires SWEEP s after a green gate and checks only that the run is at
the same head as the green one. A push between the green gate and the sweep's act
puts a new code run in the same per-PR code lane (CI-code-<pr>, not per head)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
sys.argv = sys.argv[:1] + [sys.argv[1]]
import importlib.util
spec = importlib.util.spec_from_file_location("rcs", str(Path(__file__).with_name("rerun_concurrency_sim.py")))
import gate_sim as S
src = Path(__file__).with_name("rerun_concurrency_sim.py").read_text().split("\nmain()")[0]
ns = {"__name__": "rcs", "__file__": __file__}; exec(compile(src, "rcs", "exec"), ns)
GH = ns["GH"]
w0 = S.World("REV1", S.T(), {}); w0.run([(0, "open"), (300, "edit", {"body": "b2"})])
e = [r for r in w0.runs if r["kind"] == "edit"][0]
print(f"edit run's gate completes at t={e['gate_entry']['completed'] if False else e['end']}; sweep acts {S.SWEEP} s later")
for dt in (-30, -5, 1, 10, 19):
    tp = e["end"] + dt
    w = GH("REV1", S.T(), {}); s = w.run([(0, "open"), (300, "edit", {"body": "b2"}), (tp, "push", {"head": "H2"})])
    _, bc, bd, be, orc = s[-1]
    print(f"push H2 at gate{dt:+d}s: oracle {S.fmt(orc)} merge box created {S.fmt(bc)} completed {S.fmt(bd)} every {S.fmt(be)}  {[m for _, m in w.log]}")
