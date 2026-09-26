"""D11-s2 harness: CLAUDE.md rule 1 quotes a mode line the gate never prints.

Metric: of CLAUDE.md rule 1's two load-bearing claims about closure.print_plan's
  output -- (a) the literal `MODE: SCOPED — 0 script(s) run` appears, (b) the
  FULL mode line prints a zero -- how many hold on the production printer
  (count; want 2).
Count key: substring tests on what tests/closure.py:print_plan writes for a
  scoped plan with 0 scripts to run and for a full plan; the quoted literal is
  extracted from CLAUDE.md at run time, not carried.
Perturbation: print_plan's scoped f-string with `--` replaced by `—` (in memory,
  the function re-compiled from its own source) -> claim (a) holds, count +1.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s2/mode_line.py
Expected: RESULT claims_holding=0 of 2; perturbed_claims_holding=1 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B3.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import tail  # noqa: E402
import inspect, io, re, textwrap
sys.path.insert(0, "tests")
import closure  # noqa: E402


def outputs(fn):
    s, f = io.StringIO(), io.StringIO()
    fn({"mode": "scoped", "reason": "", "run": [], "skip": {"tests/a.py": {"closure_size": 3, "reason": "no changed file in closure"}}, "changed": ["README.md"],
        "closure_sizes": {}}, stream=s)
    fn({"mode": "full", "reason": "push to main", "run": [], "skip": [], "changed": []}, stream=f)
    return s.getvalue(), f.getvalue()


def claims(fn, quoted):
    scoped, full = outputs(fn)
    a = quoted in scoped
    full_mode = [l for l in full.splitlines() if "MODE: FULL" in l]
    b = any(re.search(r"\b0\b", l) for l in full_mode)
    return a, b, scoped.splitlines()[1].strip(), full_mode[0].strip() if full_mode else ""


def main():
    text = open("CLAUDE.md", encoding="utf-8").read()
    m = re.search(r"`(MODE: SCOPED[^`]*)`", text)
    quoted = m.group(1)
    a, b, sl, fl = claims(closure.print_plan, quoted)
    print(f"# CLAUDE.md quotes: {quoted!r}")
    print(f"# print_plan scoped line: {sl!r}")
    print(f"# print_plan full line:   {fl!r}")
    src = textwrap.dedent(inspect.getsource(closure.print_plan)).replace(
        'MODE: SCOPED -- {len', 'MODE: SCOPED — {len')
    ns = dict(vars(closure))
    exec(compile(src, "print_plan_perturbed", "exec"), ns)
    pa, pb, _, _ = claims(ns["print_plan"], quoted)
    print(f"RESULT claims=2 count")
    print(f"RESULT claims_holding={int(a) + int(b)} count")
    print(f"RESULT claim_a_literal={int(a)} count")
    print(f"RESULT claim_b_full_prints_zero={int(b)} count")
    print(f"RESULT perturbed_claims_holding={int(pa) + int(pb)} count")
    tail()


if __name__ == "__main__":
    main()
