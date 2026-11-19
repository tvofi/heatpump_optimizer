#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): a raise body with one digit changed, against the budget-raise gate.

Metric: per arm, whether tools/policy/budget_raise_gate.py:justified (justification() then
  score_check() against a measured score.py report line) refuses a `## Raise justification`
  body; RESULT digit_arms_refused counts the one-digit arms refused, of digit_arms. Count key:
  the gate's own (ok, why) return, never the harness's edit.
The measured line is score.py's format (`Architecture score: dS {dS:+.4f} {verdict}`,
  tools/audit/archscore/score.py), fixed at `Architecture score: dS +0.0137 IMPROVES`.
Arms: null (the body's last score line is the measured one) -> accepted;
  each of the five digits moved by one -> refused; the verdict word swapped -> refused;
  the true line followed by a wrong one -> refused; no `Payments tried:` line -> refused;
  a wrong line followed by the true one -> accepted (the contract reads the last line).
Expected: null accepted; digit_arms_refused 5 of 5; other refusal arms 3 of 3, exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/raise_body_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): `--perturb` rebinds score_check with its two
  `round(float(...), 4)` comparisons at 2 places: digit_arms_refused falls 5 -> 3
  (the third and fourth decimals no longer count).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util
import inspect
import pathlib
import sys
import textwrap
import time

ROOT = pathlib.Path.cwd()
MEASURED = "Architecture score: dS +0.0137 IMPROVES"


def load():
    spec = importlib.util.spec_from_file_location("brg_d11s3", ROOT / "tools/policy/budget_raise_gate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def body(*score_lines, paid=True):
    lines = ["## Summary", "x", "", "## Raise justification"]
    if paid:
        lines.append("Payments tried: moved the helper; split the class (dS reported below)")
    lines += list(score_lines)
    lines += ["", "## Red checks", "none"]
    return "\n".join(lines) + "\n"


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    g = load()
    if "--perturb" in sys.argv:
        src = textwrap.dedent(inspect.getsource(g.score_check))
        assert src.count("round(float(m.group(1)), 4)") == 1 and src.count("round(float(a), 4)") == 1
        src = src.replace("round(float(m.group(1)), 4)", "round(float(m.group(1)), 2)").replace(
            "round(float(a), 4)", "round(float(a), 2)")
        ns = dict(vars(g))
        exec(compile(src, "budget_raise_gate.py(perturbed)", "exec"), ns)
        g.score_check = ns["score_check"]
        print("PERTURBED: score_check compares at 2 decimals")
    measure = lambda: MEASURED
    arms = {"null": (body(MEASURED), True)}
    digits = [i for i, ch in enumerate(MEASURED) if ch.isdigit()]
    for k, i in enumerate(digits):
        d = MEASURED[i]
        nd = str((int(d) + 1) % 10)
        arms["digit_%d" % k] = (body(MEASURED[:i] + nd + MEASURED[i + 1:]), False)
    arms["verdict_swapped"] = (body(MEASURED.replace("IMPROVES", "NULL")), False)
    arms["true_then_wrong"] = (body(MEASURED, "Architecture score: dS +0.0200 IMPROVES"), False)
    arms["no_payments_line"] = (body(MEASURED, paid=False), False)
    arms["wrong_then_true"] = (body("Architecture score: dS +0.0200 IMPROVES", MEASURED), True)
    res = {}
    for name, (b, want_ok) in arms.items():
        ok, why = g.justified(b, measure)
        res[name] = ok
        print("arm %-18s ok=%s want=%s  %s" % (name, ok, want_ok, why[:100]))
    dig = [n for n in res if n.startswith("digit_")]
    print("RESULT null_accepted=%d" % int(res["null"]))
    print("RESULT digit_arms=%d count" % len(dig))
    print("RESULT digit_arms_refused=%d count" % sum(1 for n in dig if not res[n]))
    print("RESULT other_refusal_arms_refused=%d count" % sum(
        1 for n in ("verdict_swapped", "true_then_wrong", "no_payments_line") if not res[n]))
    print("RESULT wrong_then_true_accepted=%d" % int(res["wrong_then_true"]))
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f ratio" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin "):
                sw = int(l.split()[1])
    except OSError:
        pass
    print("RESULT swapins=%d count" % sw)


if __name__ == "__main__":
    sys.exit(main())
