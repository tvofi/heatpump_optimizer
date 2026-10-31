"""L4 lead (raised by D14-s2) for D4-s2 / D4.M2 -- does the buffer-tank answer read back as answered?

Metric (one line): roundtrip_mismatch = answer combinations (2^5 over quick_setup.FIELD_QUESTIONS)
  where quick_setup.stored_answers(derive(answers) applied onto a bare entry) differs from the
  answers given, per question; buffer_mismatch is the buffer-tank question's share.
  Count key: the dict stored_answers returns (the Configure page's pre-fill).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/leads/l4_quick_roundtrip.py [--perturb]
Perturbation (--perturb): the read-back keyed the way the lead suggests, on ThermalParameters.
  buffer_is_store (volume AND a throttling valve), patched in memory -> buffer_mismatch up (the
  quick-setup "yes" writes a volume and no valve, so a store-keyed read-back says "no").
Expected: roundtrip_mismatch=0 of 32 combos; --perturb 16 (all buffer). Exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: quick_setup:derive, quick_setup:stored_answers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect
import itertools
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import quick_setup as Q  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

if "--perturb" in sys.argv:
    _orig = Q.stored_answers

    def stored_answers(current):
        out = _orig(current)
        if Q.FIELD_BUFFER_TANK in out:
            out[Q.FIELD_BUFFER_TANK] = ThermalParameters.from_config(dict(current)).buffer_is_store
        return out
    Q.stored_answers = stored_answers


def main():
    t0, th0 = time.process_time(), time.thread_time()
    sig = inspect.signature(Q.derive)
    mism = buf = 0
    n = 0
    for combo in itertools.product((False, True), repeat=len(Q.FIELD_QUESTIONS)):
        answers = dict(zip(Q.FIELD_QUESTIONS, combo))
        derived = Q.derive(answers) if len(sig.parameters) == 1 else Q.derive(answers, {})
        back = Q.stored_answers(dict(derived))
        n += 1
        for q in Q.FIELD_QUESTIONS:
            if q in back and back[q] != answers[q]:
                mism += 1
                buf += int(q == Q.FIELD_BUFFER_TANK)
    print(f"RESULT combos={n} count")
    print(f"RESULT roundtrip_mismatch={mism} count")
    print(f"RESULT buffer_mismatch={buf} count")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
