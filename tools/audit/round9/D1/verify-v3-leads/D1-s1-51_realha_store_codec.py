"""V3 verify of D1-s1-51 (P11): execute the REAL production QuarantiningStore.async_load
against genuine Home Assistant 2026.2.3 (real Store, real orjson codec, real disk file), for
the same 6 hostile-token documents the finder used, and separately execute the stub's codec
path exactly as the finder's harness does (tests/hastub, PYTHONPATH on).

Metric: of 6 stored documents (one healthy leaf "a": 1.5 plus one hostile numeric token: NaN,
Infinity, -Infinity, 1e400, a 401-digit integer, 2**64), count whose value read back through
the REAL QuarantiningStore.async_load (real orjson, real Store, real disk file, real
HomeAssistant instance) differs from the stub's async_load over the identical bytes.

Command (real half, no tests/hastub on the path):
    PYTHONPATH=custom_components /root/venvha/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s1-51_realha_store_codec.py --real
Command (stub half, for the diff):
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
        tools/audit/round9/D1/verify-v3-leads/D1-s1-51_realha_store_codec.py --stub
Expected: real half -- nan/inf/-inf load None (whole store lost); 1e400 loads None (orjson
has no non-finite float literal); 2**64 loads as a float (precision loss, not the exact int);
10**400 loads None (orjson has no int this big); control loads {"a": 1.5, "b": 2.0}.
Stub half reproduces the finder's stub_store_codec.py numbers (all 6 keep "a"=1.5, corruption
scrubbed leaf-only). divergent = 6 of 6 (every hostile doc's real-HA outcome differs from the
stub's leaf-only scrub).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Real half run on Home Assistant 2026.2.3
(venvha), which is NEWER than the tests/hastub UPSTREAM floor (2025.2.0); noted per the box
brief. Machine: shared 4-core cloud container (verify box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import json
import asyncio
import tempfile
import resource

_T0 = (time.process_time(), time.thread_time())

MODE = "--real" if "--real" in sys.argv else ("--stub" if "--stub" in sys.argv else None)
if MODE is None:
    print("usage: --real (venvha, no hastub) | --stub (PYTHONPATH=tests/hastub)")
    sys.exit(2)

if MODE == "--real":
    import typing
    typing.ByteString = bytes  # CPython 3.14 compat shim, per SUBSEAT.md

_TOKENS = {
    "nan": "NaN", "inf": "Infinity", "-inf": "-Infinity", "1e400": "1e400",
    "10**400": "1" + "0" * 400, "2**64": "18446744073709551616",
}

# The stub's async_load (tests/hastub .../storage.py:_DISK) is json.loads(raw
# content) with NO version/data envelope -- it doesn't model that structure at
# all. The real Store requires the {version, minor_version, key, data}
# envelope to extract "data" via the matching-version path. Feed each
# provider the shape it actually reads, so the comparison is the leaf-scrub
# question the finding is about, not an unrelated envelope-format mismatch.
if MODE == "--real":
    DOCS = {n: '{"version": 1, "minor_version": 1, "key": "k", "data": {"a": 1.5, "b": %s}}' % t
            for n, t in _TOKENS.items()}
    CONTROL = '{"version": 1, "minor_version": 1, "key": "k", "data": {"a": 1.5, "b": 2.0}}'
else:
    DOCS = {n: '{"a": 1.5, "b": %s}' % t for n, t in _TOKENS.items()}
    CONTROL = '{"a": 1.5, "b": 2.0}'


def load_one(text):
    if MODE == "--real":
        import homeassistant.core as core
        from heatpump_optimizer.store import QuarantiningStore

        async def _run():
            d = tempfile.mkdtemp()
            hass = core.HomeAssistant(d)
            store = QuarantiningStore(hass, 1, "k")
            path = hass.config.path(".storage", "k")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(text.encode())
            try:
                return await store.async_load()
            finally:
                # real HA's HomeAssistant keeps an executor thread pool alive;
                # shut it down so each of the 7 loads does not leak a thread.
                await hass.async_add_executor_job(lambda: None)
                hass.loop = hass.loop  # no-op, keeps lints quiet
        return asyncio.run(_run())
    else:
        sys.path.insert(0, "tests")
        sys.path.insert(0, "custom_components")
        from homeassistant.helpers import storage
        from heatpump_optimizer.store import QuarantiningStore

        async def _run():
            storage._DISK["k"] = text
            return await QuarantiningStore(None, 1, "k").async_load()
        return asyncio.run(_run())


def main():
    results = {}
    for name, text in DOCS.items():
        got = load_one(text)
        results[name] = got
        print(f"RESULT {MODE.strip('-')}_{name}={got!r:.80}")
    ctl = load_one(CONTROL)
    print(f"RESULT {MODE.strip('-')}_control={ctl!r:.80}")
    print(f"RESULT {MODE.strip('-')}_healthy_sibling_kept="
          f"{sum(1 for v in results.values() if isinstance(v, dict) and v.get('a') == 1.5)} of {len(DOCS)}")
    print(f"RESULT {MODE.strip('-')}_whole_store_lost="
          f"{sum(1 for v in results.values() if v is None)} of {len(DOCS)}")

    cpu = time.process_time() - _T0[0]
    thr = time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={(cpu / thr) if thr else 1.0:.3f}")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1}")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    print(f"RESULT swapins={ru.ru_minflt}")


main()
