#!/usr/bin/env python3
"""D11-s1 (round 11, D11.M1): which budget METER a pull request can rewrite with no owner review.

Metric (one line): of the meters that grade the budget files budget_raise_gate.SCHEMA protects, the
number a REQUIRED job executes from the pull request's own copy (no `git checkout "$PINNED" --` of it
in that job) AND that no owner-carrying .github/CODEOWNERS pattern matches.
Count's key: tools/pr/outside.py:owner_patterns over the CODEOWNERS text (production; it errs toward
OWNED, so an unowned verdict is strict) and the text of the required jobs gate.py:REQUIRED names.
The meter of each budget file is the declared METERS table below; the harness asserts each meter's
text names its budget file, so a renamed meter fails loudly instead of counting.
Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/meter_boundary.py [--perturb]
Expected at 92d38ecb640b: RESULT meters=8, RESULT pr_copy_unowned=1 (tests/structure.py), exact.
Null control: tests/coverage_ratchet.py, the meter decision 0013 moved to the base's copy and an owner,
reads pinned and owned (RESULT null_coverage_ratchet_exposed=0).
Perturbation: --perturb appends `/tests/structure.py @tvofi` to the CODEOWNERS text owner_patterns
reads -> pr_copy_unowned to_zero.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B6 (shared); counts, contention-immune.
Writes nothing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import pathlib
import re
import sys
import time

import yaml

sys.path[:0] = ["tools/ci", "tools/pr", "tools/policy"]
import gate  # noqa: E402
import outside  # noqa: E402
import budget_raise_gate  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv

METERS = {
    "tests/structure_budgets.json": "tests/structure.py",
    "tests/mutation_budgets.json": "tests/mutation_table.py",
    "tests/coverage_budgets.json": "tests/coverage_ratchet.py",
    "tests/stress_budgets.json": "tests/stress.py",
    "tests/typing_budgets.json": "tests/typing_ruler.py",
    "tests/ci_budgets.json": "tests/ci_ratchet.py",
    "dev/governance/config/policy_budgets.json": "tools/policy/policy_lint.mjs",
    "dev/governance/config/machinery_budgets.json": "tools/audit/machinery_ratchet.py",
    "dev/governance/config/machinery_target_budgets.json": "tools/audit/machinery_ratchet.py",
}
assert set(METERS) == set(budget_raise_gate.SCHEMA), sorted(set(budget_raise_gate.SCHEMA) ^ set(METERS))
for bud, m in METERS.items():
    assert pathlib.Path(bud).name in pathlib.Path(m).read_text(), (m, bud)

co = pathlib.Path(".github/CODEOWNERS").read_text()
if PERTURB:
    co += "\n/tests/structure.py @tvofi\n"
owned_re = outside.owner_patterns(co)


def owned(p):
    return any(r.fullmatch(p) for r in owned_re)


# Required jobs: every `<stem> / <job>` name gate.py can require, resolved to the job's text.
req_jobs = {}
for name in gate.gate_required():
    stem, job = name.split(" / ", 1)
    wf = yaml.safe_load(open(f".github/workflows/{stem}.yml"))
    for jid, j in wf["jobs"].items():
        nm = str(j.get("name", jid))
        if jid == job or nm == job or (job.split(" (")[0] in (jid, nm.split(" (")[0])):
            req_jobs[name] = j
            break
    else:
        raise SystemExit(f"required name {name} resolves to no job")

RUNSH = pathlib.Path("tests/run.sh").read_text()


def runsh_runs(meter):
    return re.search(r'^\s*run "\$PYTHON" ' + re.escape(meter) + r"\b", RUNSH, re.M) is not None


def exposure(meter):
    """Required jobs that execute `meter` from the pull request's copy."""
    out = []
    for name, j in req_jobs.items():
        steps = j.get("steps") or []
        restored, executed = False, False
        for s in steps:
            run = s.get("run") or ""
            if 'git checkout "$PINNED"' in run and (meter in run or "pinned.list" in run and meter in yaml.safe_dump(steps)):
                restored = True
            lines = [ln for ln in run.splitlines() if not ln.strip().startswith("#")]
            body = "\n".join(lines)
            direct = re.search(r"(python3?|node|bash)\b[^\n]*\b" + re.escape(meter), body) is not None
            via_runsh = "./tests/run.sh" in body and runsh_runs(meter)
            if (direct or via_runsh) and not restored:
                executed = True
        if executed:
            out.append(name)
    return out


rows = []
for m in sorted(set(METERS.values())):
    ex = exposure(m)
    rows.append((m, ex, owned(m)))
    print(f"METER {m}\towned={owned(m)}\tpr_copy_in_required={','.join(ex) or '-'}")
bad = [r for r in rows if r[1] and not r[2]]
for m, ex, _ in bad:
    print(f"EXPOSED {m} via {', '.join(ex)}")
cr = [r for r in rows if r[0] == "tests/coverage_ratchet.py"][0]
print(f"RESULT meters={len(rows)} meters")
print(f"RESULT pr_copy_unowned={len(bad)} meters")
print(f"RESULT null_coverage_ratchet_exposed={int(bool(cr[1]) and not cr[2])} meters")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
