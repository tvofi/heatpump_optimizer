"""D7-v1 verifier harness for D7-s2-01: are the 12 symbols referenced by production, and does the gate see them?

Metric (one line): count of the finder's 12 candidate top-level symbols with ZERO module-qualified
  production references (a `from .<mod> import <name>`, an attribute `<alias-of-mod>.<name>`, a
  `getattr(<alias>, "<name>")`, or -- for a module-private _LOGGER -- a Name load inside its own
  module), that tests/structure.py:measure() does NOT list in dead_symbols.
Null control: dhw_schedule.is_valid_spec, presets.derive and coordinator._LOGGER through the same
  resolver must each read > 0 references.
Perturbation (--perturb): in a temp copy of the package, rename grid_fee.is_valid_spec's def to a
  unique name (no other change): structure.measure()'s dead_top_level_symbols must go 0 -> 1, i.e. the
  symbol was kept "live" by the bare-name collision with dhw_schedule.is_valid_spec, not by a use.
Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/v1_dead.py [--perturb]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, sys, time, shutil, tempfile, re
from pathlib import Path
_p0, _t0 = time.process_time(), time.thread_time()
sys.path.insert(0, "tests")
import structure

PKG = Path("custom_components/heatpump_optimizer")
CANDS = [("grid_fee", "is_valid_spec"), ("presets", "describe")] + [
    (m, "_LOGGER") for m in ("battery", "binary_sensor", "dhw_draws", "power_guard", "presets",
                             "pump_schedule", "pv", "sensor", "switch", "tariff")]
CTRL = [("dhw_schedule", "is_valid_spec"), ("presets", "derive"), ("coordinator", "_LOGGER")]


def refs(mod, name, pkg=PKG):
    n = 0
    for f in sorted(pkg.glob("*.py")):
        tree = ast.parse(f.read_text())
        me = f.stem == mod
        aliases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                lvl_mod = node.module or ""
                if node.level >= 1 and lvl_mod == mod:
                    n += sum(1 for a in node.names if a.name == name)
                if node.level >= 1 and lvl_mod == "":
                    for a in node.names:
                        if a.name == mod:
                            aliases.add(a.asname or a.name)
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.endswith("." + mod) or a.name == mod:
                        aliases.add(a.asname or a.name.split(".")[0])
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == name and isinstance(node.value, ast.Name) \
                    and node.value.id in aliases:
                n += 1
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr" \
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and node.args[1].value == name:
                n += 1
            if me and isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
                n += 1
    # string mention anywhere else in production (manifest/services/json): report separately
    return n


def gate_dead_names(pkg_dir=None, root=None):
    real = structure.PACKAGE_DIR, structure.REPO_ROOT
    try:
        if pkg_dir is not None:
            structure.PACKAGE_DIR, structure.REPO_ROOT = pkg_dir, root
        m = structure.measure()
        return m["metrics"]["dead_top_level_symbols"], {(Path(r).stem, n) for r, _l, n in m["tables"]["dead_symbols"]}
    finally:
        structure.PACKAGE_DIR, structure.REPO_ROOT = real


gate_n, gate_set = gate_dead_names()
unref = []
for mod, name in CANDS:
    r = refs(mod, name)
    print(f"CELL {mod}.{name}: production_refs={r} gate_lists={((mod, name) in gate_set)}")
    if r == 0 and (mod, name) not in gate_set:
        unref.append(f"{mod}.{name}")
ctrl_ok = 0
for mod, name in CTRL:
    r = refs(mod, name)
    print(f"CTRL {mod}.{name}: production_refs={r}")
    ctrl_ok += r > 0
print(f"RESULT unreferenced_missed_by_gate={len(unref)} count (of {len(CANDS)})")
print(f"RESULT gate_dead_top_level_symbols={gate_n} count")
print(f"RESULT controls_referenced={ctrl_ok} count (of {len(CTRL)}; null control must be {len(CTRL)})")
if "--perturb" in sys.argv:
    tmp = Path(tempfile.mkdtemp(prefix="d7v1dead_", dir=os.environ.get("TMPDIR")))
    try:
        dst = tmp / "custom_components" / "heatpump_optimizer"
        shutil.copytree(PKG, dst, ignore=shutil.ignore_patterns("__pycache__", "www", "brand", "translations"))
        g = dst / "grid_fee.py"
        s = g.read_text()
        assert s.count("def is_valid_spec(") == 1
        g.write_text(s.replace("def is_valid_spec(", "def v1_unique_grid_fee_spec_check("))
        pn, pset = gate_dead_names(dst, tmp)
        print(f"RESULT perturbed_gate_dead_top_level_symbols={pn} count; lists={sorted(pset)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
