"""D3-s3-01 production-seam check (box G1-V3, lens V3).

Metric: timestamps (of 2) returned by production open_meteo._parse_block that
differ between the baseline function and the M02 mutant (the
`if parsed.tzinfo is None:` guard deleted), built by compiling the production
source with that one line and its body removed, in memory. Run under the process
TZ given in $TZ.
Command: TZ=Europe/Stockholm PYTHONPATH=tests/hastub python tools/audit/round9/D3/verify-v3-catchup/D3-s3-01_prod.py [--null]
Expected: 2 under Europe/Stockholm, 0 under UTC, 0 with --null. Baseline 1936d5ca.
"""
import os
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(k, "1")
import sys, time, inspect, textwrap, resource
sys.path.insert(0, ".")
time.tzset()
t0p, t0t = time.process_time(), time.thread_time()
from custom_components.heatpump_optimizer import open_meteo as om
src = textwrap.dedent(inspect.getsource(om._parse_block))
guard = "        if parsed.tzinfo is None:\n            parsed = parsed.replace(tzinfo=timezone.utc)\n"
assert guard in src, "guard text not found"
mut_src = src if "--null" in sys.argv else src.replace(guard, "")
ns = dict(om.__dict__)
exec(compile(mut_src, "<M02>", "exec"), ns)
mut = ns["_parse_block"]
block = {"time": ["2026-01-15T00:00", "2026-01-15T01:00"], om._VARIABLE: [10.0, 20.0]}
base_t = list(om._parse_block(block, om._VARIABLE).times)
mut_t = list(mut(block, om._VARIABLE).times)
delta = sum(1 for a, b in zip(base_t, mut_t) if a != b) + abs(len(base_t) - len(mut_t))
print("TZ", os.environ.get("TZ"), "base", base_t[:1], "mut", mut_t[:1])
print(f"RESULT mutant_delta={delta} timestamps")
print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
