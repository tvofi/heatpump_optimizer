import subprocess, sys, pathlib, os, time
wt = pathlib.Path(os.environ["HOME"]) / "wt"
f = wt / "custom_components/heatpump_optimizer/fault_log.py"
orig = f.read_text()
muts = {
 "F empty items kept": ("        if part.strip()\n    ]", "    ]"),
 "K loaded no tail cap": ("if len(row) == 4][-EPISODES_MAX:]", "if len(row) == 4]"),
 "L end unclamped": ("        end_s = max(now_s, start_s)", "        end_s = now_s"),
}
env = dict(os.environ, PYTHONPATH="tests/hastub:tools/devices")
scripts = sys.argv[1:]
for name, (a, b) in [(None, (None, None))] + list(muts.items()):
    if a: f.write_text(orig.replace(a, b))
    try:
        for s in scripts:
            t=time.time()
            p = subprocess.run([sys.executable, s], cwd=wt, env=env, capture_output=True, text=True, timeout=900)
            print(f"{name or 'UNMUTATED'} :: {s}: rc={p.returncode} ({time.time()-t:.0f}s) {p.stdout.strip().splitlines()[-1:] }", flush=True)
    finally:
        f.write_text(orig)
