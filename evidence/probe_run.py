"""Run the reviewer probe at HEAD and under each surviving mutant (same archive/prelude as the fixer's harness)."""
import importlib.util, os, subprocess, sys, tempfile
spec = importlib.util.spec_from_file_location("h", "dev/audit/harnesses/r11_owner_fault_hold_mutants.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
probe = open(sys.argv[1]).read()
M = [("none", None, None, None),
 ("consult ignores released", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=inp.mode == MODE_OFF"),
 ("consult ignores Off", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=False, released=inp.entry_released"),
 ("publish ignores mode_off", "heat_curve.py", "fault_hold.holding(entry, hass, config, off=mode_off, released=released)", "fault_hold.holding(entry, hass, config, off=False, released=released)"),
]
with tempfile.TemporaryDirectory() as copy:
    a = subprocess.run(["git", "archive", "HEAD", "custom_components", "tests", "tools"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", copy], input=a, check=True)
    prelude = os.path.join(copy, "fh_prelude.py")
    subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", prelude, h.START, h.END], cwd=copy, capture_output=True, check=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
    fp = os.path.join(copy, "tests/features.py"); feats = open(fp).read()
    i = feats.index(h.END); open(fp, "w").write(feats[:i] + probe + chr(10) + feats[i:])
    for name, f, old, new in M:
        src = None
        if f:
            path = os.path.join(copy, h.P + f); src = open(path).read()
            assert src.count(old) == 1, name
            open(path, "w").write(src.replace(old, new))
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", "exec(open(%r).read())" % prelude, h.START, h.END], cwd=copy, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
        if src: open(path, "w").write(src)
        out = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("PROBE") or "Error" in l]
        print(f"MUTANT {name}: rc={r.returncode}", *out[-3:], sep="\n  ", flush=True)
