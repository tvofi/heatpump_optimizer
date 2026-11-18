"""Verifier D1#1, V2 for D1-s2-01: the NaN boundary, with Home Assistant's real save encoding.

Real HA's Store writes through helpers/json.py save_json -> orjson.dumps (no custom encoder is
passed by QuarantiningStore), and orjson serialises a non-finite float as null; the stub's
async_save uses stdlib json.dumps, which writes a bare NaN token. This wrapper
(1) counts the NaN spellings store._poisoned lets through (of float nan, "NaN", "nan",
"-nan", "Infinity", "-inf", "1e300"), and
(2) re-runs the finder's nan_boundary.py unchanged except that the stub Store.async_save
encodes non-finite floats as null (orjson semantics), so its leaves_reaching_live and
leaves_making_disk_undecodable are what real HA's encoder would produce.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_01_nan_realsave.py [--stores a,b]
"""
import json
import math
import os
import runpy
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from homeassistant.helpers import storage as S  # noqa: E402
from heatpump_optimizer import store  # noqa: E402

spell = [float("nan"), "NaN", "nan", "-nan", "Infinity", "-inf", "1e300"]
passed = [repr(s) for s in spell if not store._poisoned(s)]
print(f"PASSING {passed}")
print(f"RESULT nonfinite_spellings_passing_poisoned={len(passed)} of {len(spell)}")


def _orjsonish(v):
    if isinstance(v, float) and not math.isfinite(v):
        return None
    if isinstance(v, dict):
        return {k: _orjsonish(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_orjsonish(x) for x in v]
    return v


async def real_save(self, data):
    S._DISK[self._key] = json.dumps(_orjsonish(data))
    S._VERSIONS[self._key] = self._version
    S.SAVE_COUNTS[self._key] = S.SAVE_COUNTS.get(self._key, 0) + 1


S.Store.async_save = real_save
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "s2", "nan_boundary.py")
sys.argv = [target] + sys.argv[1:]
sys.path.insert(0, os.path.dirname(target))
runpy.run_path(target, run_name="__main__")
