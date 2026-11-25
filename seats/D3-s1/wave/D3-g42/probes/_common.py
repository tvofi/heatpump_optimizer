"""Shared driver of the D3-g42 probes (machine: box D3-g42; every number is exact arithmetic, not timing).
A probe file defines KEY and measure(mod) -> list[(metric, value)]; main(KEY, measure) runs it in two child
processes: the baseline tree, and a scratch copy of custom_components with the key's one-line mutant applied
(the gate's tree is never touched). It prints RESULT <metric>_baseline / _mutant / _moved."""
import os, sys, json, shutil, subprocess, tempfile
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path

def root():
    here = Path(__file__).resolve()
    for c in here.parents:
        if (c / "custom_components/heatpump_optimizer/manifest.json").is_file():
            return c
    raise RuntimeError("no root")

def src_root():
    """Directory holding the pristine baseline custom_components (env PROBE_BASE, a `git archive` of the baseline; falls back to the tree)."""
    return Path(os.environ.get("PROBE_BASE") or root())

def scratch(key):
    R = root()
    rec = json.load(open(R / "dev/audit/rounds/round11/D3/s1/state/results/complete" / f"{key}.json"))["mutant"]
    d = Path(tempfile.mkdtemp(prefix=f"d3g42-{key}-"))
    shutil.copytree(src_root() / "custom_components", d / "custom_components")
    f = d / rec["file"]
    lines = f.read_text().split("\n")
    assert lines[rec["line"] - 1] == rec["old"], (lines[rec["line"] - 1], rec["old"])
    lines[rec["line"] - 1] = rec["new"]
    f.write_text("\n".join(lines))
    return d

def child(key, path, pyfile):
    env = dict(os.environ, PROBE_ARM="1", PYTHONPATH=f"{path}:{root()}/tests/hastub")
    out = subprocess.run([sys.executable, pyfile], env=env, cwd=path, capture_output=True, text=True)
    if out.returncode:
        return {"_error": out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "rc"}
    return {l.split()[1].split("=", 1)[0]: l.split("=", 1)[1] for l in out.stdout.splitlines() if l.startswith("RESULT ")}

def main(key, measure, pyfile):
    if os.environ.get("PROBE_ARM"):
        import importlib
        mod = importlib.import_module("custom_components.heatpump_optimizer.thermal_model")
        assert str(Path(mod.__file__).resolve()).startswith(str(Path.cwd().resolve())), mod.__file__
        for k, v in measure(mod):
            print(f"RESULT {k}={v!r}")
        return
    base = child(key, str(src_root()), pyfile)
    d = scratch(key)
    mut = child(key, str(d), pyfile)
    shutil.rmtree(d, ignore_errors=True)
    moved = 0
    for k in sorted(set(base) | set(mut)):
        mv = base.get(k) != mut.get(k)
        moved += mv
        print(f"RESULT {k}_baseline={base.get(k)}\nRESULT {k}_mutant={mut.get(k)}")
    print(f"RESULT metrics_moved={moved}")

def hits(mod, fname, lineno, fn):
    """Number of times line `lineno` of thermal_model executes while fn() runs (reach evidence)."""
    n = [0]
    def tr(frame, ev, arg):
        if frame.f_code.co_filename.endswith(fname):
            if ev == "line" and frame.f_lineno == lineno:
                n[0] += 1
            return tr
        return tr
    sys.settrace(tr)
    try:
        fn()
    finally:
        sys.settrace(None)
    return n[0]
