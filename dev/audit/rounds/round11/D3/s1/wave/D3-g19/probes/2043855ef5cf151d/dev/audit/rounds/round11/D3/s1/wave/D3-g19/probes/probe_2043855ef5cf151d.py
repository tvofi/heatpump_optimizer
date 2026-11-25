#!/usr/bin/env python3
# Metric: what grid_fee.parse_rules returns for spec=None (its signature's `str | None`, docstring "Empty input is an
#   empty list"), and the config-flow verdict grid_fee.spec_problem(None).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2043855ef5cf151d.py
# EXPECTED RESULT parse_none_baseline=[]
# EXPECTED RESULT parse_none_mutant=GridFeeError  (str(None) == 'None' is parsed as a rule with no '= rate')
# EXPECTED RESULT spec_problem_none_baseline=None
# EXPECTED RESULT spec_problem_none_mutant=invalid_grid_fee_rules
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT empty_string_delta=0 count  ('' and whitespace/separator-only specs: the split loop drops empty lines,
#   so the guard is redundant for every str input; it is load-bearing only for None)
# EXPECTED RESULT from_config_rules_delta=0 count  (from_config degrades a GridFeeError to [] with a WARNING)
# EXPECTED RESULT from_config_warnings_mutant=1 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:parse_rules (line 219 `    if not spec:`), reached by
#   spec_problem (config_flow._grid_fee_errors), GridFeeSchedule.from_config and apply_catalog.
# Perturbation: `    if not spec:` -> `    if False:` (GUARD_OFF 2043855ef5cf151d), applied in memory (function recompiled
#   from its own source, patched onto the module for the mutant arm). Direction: [] -> GridFeeError for None.
# Null control: '' , ' ', '\n', ';', ',' (identical [] in both arms), and a valid spec "Mon = 0.5".
# Inputs tried: None, '', ' ', '\n', ';', ',', 'Mon = 0.5'; from_config with grid_fee_rules=None in rules mode.
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
import logging  # noqa: E402
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

mut = mutated(gf, gf, "parse_rules", 219, "    if not spec:", "    if False:")


def run(fn, spec):
    try:
        return fn(spec)
    except gf.GridFeeError as exc:
        return type(exc).__name__


b, m = run(gf.parse_rules, None), run(mut, None)
sb = gf.spec_problem(None)
with mock.patch.object(gf, "parse_rules", mut):
    sm = gf.spec_problem(None)
empty = sum(int(repr(run(gf.parse_rules, s)) != repr(run(mut, s))) for s in ("", " ", "\n", ";", ",", "Mon = 0.5"))


class Count(logging.Handler):
    n = 0

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            Count.n += 1


h = Count()
gf._LOGGER.addHandler(h)
cfg = {"grid_fee_mode": gf.MODE_RULES, "grid_fee_fixed": 0.1, "grid_fee_rules": None}
rb = gf.GridFeeSchedule.from_config(cfg).rules
w0 = Count.n
with mock.patch.object(gf, "parse_rules", mut):
    rm = gf.GridFeeSchedule.from_config(cfg).rules
wm = Count.n - w0
print(f"RESULT parse_none_baseline={b}")
print(f"RESULT parse_none_mutant={m}")
print(f"RESULT spec_problem_none_baseline={sb}")
print(f"RESULT spec_problem_none_mutant={sm}")
print(f"RESULT moved={int(repr(b) != repr(m))} count")
print(f"RESULT empty_string_delta={empty} count")
print(f"RESULT from_config_rules_delta={int(rb != rm)} count")
print(f"RESULT from_config_warnings_baseline={w0} count")
print(f"RESULT from_config_warnings_mutant={wm} count")
tail()
