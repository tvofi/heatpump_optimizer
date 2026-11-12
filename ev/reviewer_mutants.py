#!/usr/bin/env python3
"""Reviewer's own mutants (builder: the fix-review seat, not the finder, not the fixer).
One exact-once text edit per private copy of the head tree's package and tests/,
the fixer's section harness run on the copy through DSP_SECTION_ROOT."""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
HEAD = Path(sys.argv[1]).resolve()
PKG = "custom_components/heatpump_optimizer/"
M = [
 ("R1 _co_optimize does not restore the availability vector after a refused candidate", PKG+"optimizer.py",
  "                return candidate_space, replanned, candidate_status\n            self._space_avail = kept_avail\n",
  "                return candidate_space, replanned, candidate_status\n"),
 ("R2 _avoid_priced_switches does not restore the availability vector after a refusal", PKG+"optimizer.py",
  "    opt._space_avail = kept_avail\n    return incumbent\n", "    return incumbent\n"),
 ("R3 the achieved objective is handed no availability vector", PKG+"optimizer.py",
  "            if self.model.params.dhw_store.combi else None,\n            self._space_avail,\n        ))",
  "            if self.model.params.dhw_store.combi else None,\n            None,\n        ))"),
 ("R4 the predicted cost is handed the shipped draw", PKG+"optimizer.py",
  "energy_cost_of, baseline_power, heat_space, optimal_dhw, h.humidity,",
  "energy_cost_of, baseline_power, optimal_space, optimal_dhw, h.humidity,"),
 ("R5 _co_optimize's headroom ignores the availability vector", PKG+"optimizer.py",
  "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, None, _duty_floor(self))"),
 ("R6 the batch energy cost is handed the shipped draw", PKG+"optimizer.py",
  "grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,", "grid_power,"),
 ("R7 the batch switch term is handed the delivered draw", PKG+"optimizer.py",
  "switch_cost(space_matrix, dhw_plan_power)),", "switch_cost(heat_matrix, dhw_plan_power)),"),
 ("R8 the batch simulation is handed the shipped draw", PKG+"optimizer.py",
  "power_matrix=heat_matrix,", "power_matrix=space_matrix,"),
 ("R9 the availability vector is classified with no duty floor", PKG+"optimizer.py",
  "return duty_legs.availability(space, tank, lost, _duty_floor(opt))", "return duty_legs.availability(space, tank, lost, None)"),
 ("R10 the ban forbids only the step heating runs in, not the one before", PKG+"duty_legs.py",
  "        ban |= on\n        ban[:-1] |= on[1:]\n", "        ban |= on\n"),
 ("R11 the candidate pass runs on a combi store", PKG+"optimizer.py",
  "or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:", "or not opt.config.cycling_cost > 0:"),
 ("R12 the candidate pass runs with no cycling cost", PKG+"optimizer.py",
  "if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:", "if stops is None or opt.model.params.dhw_store.combi:"),
 ("R13 a two-leg step is not charged", PKG+"duty_legs.py",
  "    charged = two.copy()\n", "    charged = np.zeros_like(two)\n"),
 ("R14 the reverse direction bans nothing", PKG+"duty_legs.py",
  "        ban |= on\n        ban[1:] |= on[:-1]\n", "        pass\n"),
 ("R15 the headroom on a clamped install carries the lost time too", PKG+"duty_legs.py",
  "    if avail is None or floor is not None:\n", "    if avail is None:\n"),
 ("R16 the incumbent's short steps do not excuse the candidate", PKG+"optimizer.py",
  "            unheld.add(step)\n", "            unheld.add(step); break\n"),
 ("R17 the publication realises nothing after the candidate pass (control-shaped: delivered on clamped install keyed off)", PKG+"optimizer.py",
  "        return space, dhw, space\n    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))",
  "        return space, dhw, space\n    return space, dhw, space"),
]
HARNESS = HEAD / "dev/audit/harnesses/r10_duty_switch_price_section.py"
def run(edit):
    d = Path(tempfile.mkdtemp(prefix="revmut-"))
    try:
        for sub in ("custom_components", "tests"):
            shutil.copytree(HEAD / sub, d / sub, ignore=shutil.ignore_patterns("__pycache__", "golden", "mutation*"))
        if edit:
            name, f, old, new = edit
            p = d / f; t = p.read_text()
            if t.count(old) != 1:
                return f"PATTERN NOT FOUND ONCE ({t.count(old)})", []
            p.write_text(t.replace(old, new))
        env = dict(os.environ, DSP_SECTION_ROOT=str(d), PYTHONPATH=str(d / "tests/hastub"), PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, str(HARNESS)], cwd=d, env=env, capture_output=True, text=True, timeout=1500)
        out = r.stdout + r.stderr
        red = [l.strip() for l in out.splitlines() if l.startswith("  FAIL ")]
        if "SECTION CHECKS" not in out:
            red.append("the section stopped: " + (out.strip().splitlines() or ["?"])[-1][:200])
        return f"exit {r.returncode}", red
    finally:
        shutil.rmtree(d, ignore_errors=True)
print("head", subprocess.run(["git","rev-parse","HEAD"],cwd=HEAD,capture_output=True,text=True).stdout.strip(), flush=True)
st, red = run(None); print(f"== control, no edit: {st}, {len(red)} red", flush=True)
surv = 0
for e in M:
    st, red = run(e)
    verdict = "KILLED" if red else ("SURVIVED" if st.startswith("exit") else st)
    surv += verdict == "SURVIVED"
    print(f"== {e[0]}: {verdict} ({st}, {len(red)} red)", flush=True)
    for l in red[:4]: print("     " + l[:260], flush=True)
print(f"RESULT reviewer_mutants={len(M)} survived={surv}", flush=True)
