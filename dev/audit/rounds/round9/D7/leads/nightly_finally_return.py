"""D7-s3-51: tests/nightly_ha.py:_async_check_a4 returns from inside a finally block (PEP 765 --
a SyntaxWarning on CPython 3.14), which discards an exception still in flight from the try.

Metric: of 2 arms where the broken-price refresh raises a BaseException the inner handler does not
catch (asyncio.CancelledError, KeyboardInterrupt) and the recovery refresh then raises, count arms
in which _async_check_a4 returns normally (the in-flight exception swallowed). Plus the count of
SyntaxWarnings compiling the file emits. Count key: whether the production-of-the-lane coroutine
tests/nightly_ha.py:_async_check_a4 propagates.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/nightly_finally_return.py [--fixed]
Expected: swallowed=2 of 2, syntax_warnings=1. --fixed (perturbation: the same function compiled with
the finally's `return` replaced by a flag checked after the block) -> swallowed=0, warnings=0.
Null control: recovery refresh succeeds -> the in-flight exception propagates (swallowed 0 of 2).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, asyncio, types, warnings, time, resource
sys.path.insert(0, "tests")
_T0 = (time.process_time(), time.thread_time())
FIXED = "--fixed" in sys.argv
SRC = open("tests/nightly_ha.py").read()
if FIXED:
    SRC = SRC.replace(
        "        except Exception as err:  # noqa: BLE001\n            check_a4_recovered(checks, False, before, [])\n            return\n    check_a4_recovered(",
        "        except Exception as err:  # noqa: BLE001\n            check_a4_recovered(checks, False, before, [])\n            _recovery_failed = True\n        else:\n            _recovery_failed = False\n    if _recovery_failed:\n        return\n    check_a4_recovered(")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    code = compile(SRC, "tests/nightly_ha.py", "exec")
n_warn = sum(1 for w in caught if issubclass(w.category, SyntaxWarning))
mod = types.ModuleType("nightly_ha_probe")
mod.__file__ = "tests/nightly_ha.py"
exec(code, mod.__dict__)
mod.break_price_source = lambda broken: None
mod._a4_records = lambda hass, entry: []


class Hass:
    async def async_block_till_done(self):
        return None


def arm(exc, recovery_raises):
    calls = {"n": 0}

    class Coord:
        last_update_success = False

        async def async_refresh(self):
            calls["n"] += 1
            if calls["n"] == 1:
                raise exc
            if recovery_raises:
                raise RuntimeError("recovery refresh failed")

    entry = types.SimpleNamespace(runtime_data=Coord(), entry_id="e")
    try:
        asyncio.run(mod._async_check_a4(mod.Checks(), Hass(), entry))
        return 1
    except BaseException:  # noqa: BLE001
        return 0


sw = arm(asyncio.CancelledError(), True) + arm(KeyboardInterrupt(), True)
ctl = arm(asyncio.CancelledError(), False) + arm(KeyboardInterrupt(), False)
print(f"RESULT swallowed={sw} of_2")
print(f"RESULT control_swallowed={ctl} of_2")
print(f"RESULT syntax_warnings={n_warn}")
pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={pc / tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
