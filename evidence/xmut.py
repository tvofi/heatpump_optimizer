"""Reviewer's own extra mutants, through the PR's mutant harness machinery (block(), run())."""
import importlib.util, sys
p = sys.argv[1]
spec = importlib.util.spec_from_file_location("m", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
X = {
 "X1-no-rest": ("            await asyncio.sleep(rest)\n", "            pass\n"),
 "X2-timeout-25": ("PY_SPY_TIMEOUT_S = 5.0\n", "PY_SPY_TIMEOUT_S = 25.0\n"),
 "X3-tries-2": ("HB_CONTROL_TRIES = 3\n", "HB_CONTROL_TRIES = 2\n"),
 "X4-no-break": ("        if all(hb_control_reading(summary)):\n            break", "        pass"),
 "X5-dump-default-30": ("spy_timeout=PY_SPY_TIMEOUT_S,", "spy_timeout=30.0,"),
 "X6-control-check-last-only": ("        any(all(r) for r in readings),", "        all(readings[-1]),"),
}
checks = m.block()
for k, (o, n) in X.items():
    f = m.run(k, o, n, checks)
    print(k, ("KILLED by: " + " | ".join(f)) if f else "SURVIVED", flush=True)
