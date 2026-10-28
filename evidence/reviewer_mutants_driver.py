import subprocess, sys, os, time
from pathlib import Path
M = {
 "X1-no-rest": ("            await asyncio.sleep(rest)\n", "            pass\n"),
 "X2-timeout-25": ("PY_SPY_TIMEOUT_S = 5.0", "PY_SPY_TIMEOUT_S = 25.0"),
 "X3-tries-2": ("HB_CONTROL_TRIES = 3", "HB_CONTROL_TRIES = 2"),
 "X5-default-30": ("spy_timeout=PY_SPY_TIMEOUT_S,", "spy_timeout=30.0,"),
 "H1-rest-const-0": ("HB_CONTROL_REST_S = 1.0", "HB_CONTROL_REST_S = 0.0"),
 "H2-ctrl-default-tries-1": ("tries: int = HB_CONTROL_TRIES,", "tries: int = 1,"),
 "H3-break-on-any": ("        if all(hb_control_reading(summary)):\n            break", "        if any(hb_control_reading(summary)):\n            break"),
 "H4-boot-tries-1-kw": ("    await _async_hb_control(checks)\n", "    await _async_hb_control(checks, tries=1)\n"),
}
name, wt, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
f = wt/"tests/nightly_ha.py"; orig = f.read_text(); a, b = M[name]
assert orig.count(a) == 1, (name, orig.count(a))
f.write_text(orig.replace(a, b))
t = time.time()
p = subprocess.run([sys.executable, "tests/entities.py"], capture_output=True, text=True, cwd=wt, env=dict(os.environ, PYTHONPATH="tests/hastub"))
(out/f"full-{name}.log").write_text(p.stdout + p.stderr)
fails = [l for l in p.stdout.splitlines() if l.startswith("  FAIL")]
last = (p.stdout.strip().splitlines() or ["<no out>"])[-1]
print(f"{name} rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} ({time.time()-t:.0f}s) last: {last}")
for l in fails: print("   ", l[:240])
