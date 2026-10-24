"""D8-s3 / D8.M5 -- the ordering/naming/default matrix as one graduate-ready run.

Metric (one line): one RESULT per violation class from the D8-s3 matrix
(family splits, en/sv concept parity, setup-input lit-but-off, duplicate
enabled publications), plus the two graduation preconditions measured, not
asserted: RESULT values differing between two identical runs (determinism)
and outbound socket connects attempted (network; socket.connect is patched
to count and refuse).

Command (repo root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m5_matrix.py
    ... --perturb  (passes --perturb to every sub-harness: each finding class
                    falls; setup_input_lit_but_off, a non-finding, rises 0 -> 1 as
                    its instrument-sensitivity control)
Expected: family_split_unexplained_en=2, family_split_unexplained_sv=2,
          sv_concept_mismatch=1, setup_input_lit_but_off=0,
          duplicate_enabled_pairs=1, nondeterministic_results=0,
          network_connects=0 (all exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B4 (linux).
Instrumented: every platform's async_setup_entry through the sub-harnesses
(see each header); socket.socket.connect for the network class.
Graduation note: tests/closure.py and run.sh glob tests/*.py non-recursively,
so the graduate goes to tests/ top level with roster.py inlined, and must be
classified in a closure or on INERT (CLAUDE.md).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SUBS = {
    "m3_families.py": {"families_split_unexplained_name_en": "family_split_unexplained_en",
                       "families_split_unexplained_name_sv": "family_split_unexplained_sv",
                       "families_split_unexplained_entity_id": "family_split_unexplained_entity_id"},
    "m3_translation.py": {"concept_mismatch": "sv_concept_mismatch",
                          "key_set_differences": "translation_key_set_differences"},
    "m4_setup_inputs.py": {"lit_but_off": "setup_input_lit_but_off"},
    "m4_duplicates.py": {"duplicate_enabled_pairs": "duplicate_enabled_pairs"},
}
VOLATILE = ("thread_factor", "load1", "swapins")
BOOT = (
    "import socket, runpy, sys, atexit\n"
    "n=[0]\n"
    "def _c(self,*a,**k):\n"
    "    n[0]+=1\n"
    "    raise OSError('network refused by m5_matrix')\n"
    "socket.socket.connect=_c\n"
    "socket.socket.connect_ex=_c\n"
    "atexit.register(lambda: print(f'RESULT network_connects={n[0]} count'))\n"
    "sys.argv=[sys.argv[1]]+sys.argv[2:]\n"
    "runpy.run_path(sys.argv[0], run_name='__main__')\n"
)


def run(script, extra):
    out = subprocess.run([sys.executable, "-c", BOOT, os.path.join(HERE, script), *extra],
                         capture_output=True, text=True, env=os.environ.copy())
    res = {}
    for line in out.stdout.splitlines():
        if line.startswith("RESULT "):
            k, v = line[7:].split("=", 1)
            res[k] = v.split()[0]
    if out.returncode:
        res["_rc"] = str(out.returncode)
        sys.stderr.write(out.stderr[-2000:])
    return res


t0 = time.perf_counter()
extra = ["--perturb"] if "--perturb" in sys.argv else []
nondet = net = 0
final = {}
for script, keys in SUBS.items():
    a, b = run(script, extra), run(script, extra)
    for k in set(a) | set(b):
        if k in VOLATILE or k == "network_connects":
            continue
        if a.get(k) != b.get(k):
            nondet += 1
            print(f"NONDETERMINISTIC {script} {k}: {a.get(k)} vs {b.get(k)}")
    net += int(a.get("network_connects", 0)) + int(b.get("network_connects", 0))
    for src, dst in keys.items():
        final[dst] = a.get(src, "MISSING")
    if "_rc" in a:
        final[f"{script}_exit"] = a["_rc"]
for k, v in final.items():
    print(f"RESULT {k}={v} count")
print(f"RESULT nondeterministic_results={nondet} count")
print(f"RESULT network_connects={net} count")
print(f"RESULT wall_s={time.perf_counter() - t0:.1f} s provisional")
print("RESULT thread_factor=1.000")  # this parent does no numeric work; each child prints its own
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
