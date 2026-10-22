"""Reviewer's own F2 driver: hang-once stub py-spy through a tree's heartbeat control, in-process."""
import asyncio, sys, tempfile, time
from pathlib import Path
tree = Path(sys.argv[1])
sys.path[:0] = [str(tree/"tests"), str(tree/"tests"/"hastub"), str(tree)]
import nightly_ha as n
with tempfile.TemporaryDirectory() as tmp:
    calls, stub = Path(tmp)/"calls", Path(tmp)/"py-spy"
    stub.write_text(f'#!/bin/sh\necho >> "{calls}"\nexec sleep 600\n'
                    "printf 'Thread 1 (active+gil)\\n    _hb_spin (nightly_ha.py:1)\\n'\n")
    stub.chmod(0o755)
    c = n.Checks(); t0 = time.monotonic()
    if hasattr(n, "_async_hb_control"):
        asyncio.run(n._async_hb_control(c, py_spy=str(stub)))
    else:
        n._py_spy_path = lambda: str(stub)
        async def control():
            asyncio.get_running_loop().call_soon(n._hb_spin, n.HB_CONTROL_S)
            await asyncio.sleep(n.HB_CONTROL_S + 0.2)
        async def go():
            summary, _ = await n._async_hb_measure(c, "hb:positive_control", control)
            return summary
        n.check_hb_positive_control(c, asyncio.run(go()))
    el = time.monotonic() - t0
    made = len(calls.read_text().splitlines()) if calls.exists() else 0
ok = "hb:positive_control" not in c.failures()
print(f"NEVER tree={tree.name} pass={ok} calls={made} elapsed={el:.1f}s detail={c.results['hb:positive_control'][1]}")
