# Reviewer's own driver: the real _async_hb_control at its production defaults
# (no spy_timeout, no rest passed), against stub py-spy binaries.
import asyncio, sys, tempfile, time
from pathlib import Path
sys.path[:0] = ["tests", "tests/hastub", "."]
import nightly_ha as n
SAYS = {"hang": "exec sleep 60",
        "spin": "printf 'Thread 1 (active+gil)\\n    _hb_spin (nightly_ha.py:1)\\n'",
        "idle": "printf 'Thread 1 (active+gil)\\n    some_other (x.py:1)\\n'",
        "torn": "printf '    _hb_spin (nightly_ha.py:1)\\n'; exit 1"}
def run(label, *answers):
    with tempfile.TemporaryDirectory() as tmp:
        calls, stub = Path(tmp)/"calls", Path(tmp)/"py-spy"
        cases = "".join(f"  {k}) {SAYS[a]} ;;\n" for k, a in enumerate(answers, 1))
        stub.write_text(f'#!/bin/sh\necho >> "{calls}"\ncase $(wc -l < "{calls}") in\n{cases}  *) {SAYS[answers[-1]]} ;;\nesac\n')
        stub.chmod(0o755)
        c = n.Checks(); t = time.monotonic()
        asyncio.run(n._async_hb_control(c, py_spy=str(stub)))
        dt = time.monotonic() - t
        made = len(calls.read_text().splitlines()) if calls.exists() else 0
        ok = "hb:positive_control" not in c.failures()
        print(f"RESULT {label}: pass={ok} calls={made} elapsed={dt:.1f}s detail={c.results['hb:positive_control'][1][:160]!r}")
run("never-answers(real 5s cut)", "hang")
run("answers-without-spin", "idle")
run("rc1-only", "torn")
run("hang-hang-spin", "hang", "hang", "spin")
