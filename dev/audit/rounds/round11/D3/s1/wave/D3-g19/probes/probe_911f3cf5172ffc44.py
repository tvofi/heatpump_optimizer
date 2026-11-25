#!/usr/bin/env python3
# Metric: whether grid_fee.apply_catalog writes fields (a dict) or refuses (None) for a catalog row whose
#   grid_fee_rules fail parse_rules (a stale row), and how many SHIPPED catalog rows reach that branch at all.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_911f3cf5172ffc44.py
# EXPECTED RESULT stale_row_baseline=None
# EXPECTED RESULT stale_row_mutant=dict  (the mutant falls through and returns the unparseable rules for writing)
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT shipped_rows_reaching_line=0 count  (every shipped SWEDEN_CATALOG row parses: line 496 is
#   reachable only from a stale row, which the shipped catalog does not contain)
# EXPECTED RESULT null_delta=0 count  (every shipped row: identical return in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:apply_catalog (line 496 `        return None`
#   in the `except GridFeeError` arm), called by config_flow._apply_dso_catalog.
# Perturbation: line 496 `        return None` -> `        pass` (RETURN_DEL 911f3cf5172ffc44), applied in memory (function
#   recompiled from its own source, patched onto the module for the mutant arm only). Direction: None -> dict.
#   The stale row is injected in memory (mock.patch.dict on SWEDEN_CATALOG) because no shipped row is stale.
# Null control: every shipped catalog product id (both arms identical).
# Inputs tried: one injected row with rules "garbage" (no '='), one with "Mon = abc"; every shipped product id; None; "none"; unknown id.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

mut = mutated(gf, gf, "apply_catalog", 496, "        return None", "        pass")
shipped = list(gf.SWEDEN_CATALOG)
reach = 0
for pid in shipped:
    try:
        gf.parse_rules(str(gf.SWEDEN_CATALOG[pid]["grid_fee_rules"]))
    except gf.GridFeeError:
        reach += 1
null_delta = sum(int(gf.apply_catalog(p) != mut(p)) for p in shipped + [None, gf.DSO_PRODUCT_NONE, "no_such_product"])
template = dict(next(iter(gf.SWEDEN_CATALOG.values())))
moved = 0
for bad in ("garbage", "Mon = abc"):
    row = dict(template, grid_fee_rules=bad)
    with mock.patch.dict(gf.SWEDEN_CATALOG, {"stale_probe_row": row}):
        b, m = gf.apply_catalog("stale_probe_row"), mut("stale_probe_row")
    moved += int((b is None) != (m is None))
    if bad == "garbage":
        print(f"RESULT stale_row_baseline={None if b is None else type(b).__name__}")
        print(f"RESULT stale_row_mutant={None if m is None else type(m).__name__}")
        if m is not None:
            print(f"RESULT stale_row_mutant_rules_written={m.get(gf.CONF_GRID_FEE_RULES)!r}")
print(f"RESULT moved={int(moved > 0)} count")
print(f"RESULT stale_inputs_moved={moved} of 2 count")
print(f"RESULT shipped_rows={len(shipped)} count")
print(f"RESULT shipped_rows_reaching_line={reach} count")
print(f"RESULT null_delta={null_delta} count")
tail()
