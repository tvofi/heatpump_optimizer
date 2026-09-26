"""V2 (independent) for D1-s1-51: the hastub Store versus Home Assistant 2026.2.3's real Store.

Metric: of 9 hostile stored documents plus 3 healthy controls (my grid: hostile tokens nested inside list/dict payload shapes
the integration's stores use, plus big-integer and underflow boundaries and 3 healthy controls),
count those whose payload from production QuarantiningStore.async_load differs between
(a) QuarantiningStore over tests/hastub's Store (the data text placed on the stub's _DISK), and
(b) QuarantiningStore over the REAL homeassistant.helpers.storage.Store of HA 2026.2.3, run in a
subprocess on a real HomeAssistant(config_dir) object, the same data text written into
<config>/.storage/<key> inside HA's own {"version","minor_version","key","data"} wrapper.
Count key: the payload production QuarantiningStore.async_load returns (json.dumps, sort_keys).
Also counted: documents real HA returns None for (whole store lost) while the stub keeps a
healthy sibling, and .corrupt.* files real HA leaves behind.
Command: LEADS_HA_ROOT=<root> PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_store_codec_realha.py
Expected: divergent=7 of 9 hostile (exact; counts); whole_store_lost_real_kept_stub=4; controls 0 of 3.
  --orjson -> divergent=0 of 9.
Perturbation: --orjson swaps the stub's json.loads for orjson.loads returning None on a decode
error (the fix shape); divergent must fall (expected to 0 on the stub-vs-real comparison).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "custom_components")
import leads_realha  # noqa: E402

T0 = (time.process_time(), time.thread_time())
ORJSON = "--orjson" in sys.argv

DOCS = [
    ("list_nan", '{"history": [1.0, NaN, 2.0], "total": 3.5}', True),
    ("deep_neg_inf", '{"model": {"bins": [[0.1, -Infinity]]}, "n": 4}', True),
    ("list_1e309", '{"rows": [1e309, 2.0], "ok": true}', True),
    ("neg_1e400", '{"x": -1e400, "keep": 7}', True),
    ("u64_max_plus1", '{"count": 18446744073709551617, "keep": 7}', True),
    ("i64_min_minus1", '{"count": -9223372036854775809, "keep": 7}', True),
    ("int_30_digits", '{"count": 123456789012345678901234567890, "keep": 7}', True),
    ("underflow_1e-400", '{"tiny": 1e-400, "keep": 7}', True),
    ("string_nan", '{"v": "NaN", "keep": 7}', True),
    ("ctl_1e308", '{"v": 1e308, "keep": 7}', False),
    ("ctl_i64_max", '{"v": 9223372036854775807, "keep": 7}', False),
    ("ctl_nested", '{"a": {"b": [1, 2.5, null, "x"]}, "keep": 7}', False),
]

REAL = r'''
import asyncio, glob, importlib.util, json, os, sys, tempfile, logging
logging.disable(logging.CRITICAL)
from homeassistant.core import HomeAssistant
spec = importlib.util.spec_from_file_location("hpo_store", "custom_components/heatpump_optimizer/store.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs = json.loads(sys.stdin.read())
async def main():
    d = tempfile.mkdtemp()
    hass = HomeAssistant(d)
    os.makedirs(os.path.join(d, ".storage"))
    out = {}
    for name, text in docs:
        key = "heatpump_optimizer_" + name
        with open(os.path.join(d, ".storage", key), "w") as fh:
            fh.write('{"version": 1, "minor_version": 1, "key": "%s", "data": %s}' % (key, text))
        got = await mod.QuarantiningStore(hass, 1, key).async_load()
        corrupt = len(glob.glob(os.path.join(d, ".storage", key + ".corrupt.*")))
        out[name] = [json.dumps(got, sort_keys=True, default=repr), corrupt]
    print(json.dumps(out))
asyncio.run(main())
'''


def stub_results():
    from homeassistant.helpers import storage
    from heatpump_optimizer.store import QuarantiningStore
    if ORJSON:
        import orjson

        def dec(text):
            try:
                return orjson.loads(text)
            except orjson.JSONDecodeError:
                return None
        storage.json = type("J", (), {"loads": staticmethod(dec), "dumps": staticmethod(json.dumps)})
    out = {}
    for name, text, _ in DOCS:
        storage._DISK["k_" + name] = text

        async def go(n=name):
            return await QuarantiningStore(None, 1, "k_" + n).async_load()
        got = asyncio.run(go())
        out[name] = json.dumps(got, sort_keys=True, default=repr)
    return out


def main():
    real = json.loads(leads_realha.run_real(REAL, json.dumps([[n, t] for n, t, _ in DOCS])))
    stub = stub_results()
    div = div_ctl = lost_real_kept_stub = corrupt_files = 0
    for name, _, hostile in DOCS:
        r, corrupt = real[name]
        s = stub[name]
        d = r != s
        if hostile:
            div += d
        else:
            div_ctl += d
        corrupt_files += corrupt
        lost_real_kept_stub += (r == "null" and s != "null")
        print(f"RESULT doc_{name}: real={r[:70]} stub={s[:70]} divergent={int(d)} real_corrupt_file={corrupt}")
    n_h = sum(1 for d in DOCS if d[2])
    print(f"RESULT divergent={div} of_{n_h} hostile documents")
    print(f"RESULT control_divergent={div_ctl} of_{len(DOCS) - n_h}")
    print(f"RESULT whole_store_lost_real_kept_stub={lost_real_kept_stub} of_{n_h}")
    print(f"RESULT real_corrupt_files={corrupt_files}")
    pc, tc = time.process_time() - T0[0], time.thread_time() - T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")


main()
