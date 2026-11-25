# Shared helper for the box D3-g37 probes (not a harness itself; no RESULT lines).
# mutant(module, qualname_top, old, new): recompile one top-level production function from its own
# source with the single mutated line replaced, in a copy of the module's globals, and return it.
# The module on disk is never touched (README: perturb in memory). `swap(module, name, fn)` is a
# context manager that installs the mutant as the module attribute so production callers reach it.
import contextlib
import inspect
import json
import os
import sys
import textwrap
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
S1 = ROOT / "dev/audit/rounds/round11/D3/s1"


def record(key):
    """The key's mutant record (file, line, old, new) as the gate applies it."""
    return json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]


def mutant(module, name, old, new):
    fn = getattr(module, name)
    src = textwrap.dedent(inspect.getsource(fn))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor {o!r} not unique in {name}"
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == o:
            lines[i] = line[: len(line) - len(line.lstrip())] + n
            break
    else:
        raise AssertionError(f"anchor {o!r} is not a whole line of {name}")
    ns = dict(module.__dict__)
    exec(compile("\n".join(lines), module.__file__, "exec"), ns)
    return ns[name]


def mutant_for(module, key):
    m = record(key)
    lines = Path(ROOT / m["file"]).read_text().split("\n")
    assert lines[int(m["line"]) - 1] == m["old"], "baseline line moved"
    name = None
    for i in range(int(m["line"]) - 1, -1, -1):
        s = lines[i]
        if s.startswith("def ") or s.startswith("async def "):
            name = s.split("def ", 1)[1].split("(", 1)[0]
            break
    return mutant(module, name, m["old"], m["new"]), name, m


@contextlib.contextmanager
def swap(module, name, fn):
    real = getattr(module, name)
    setattr(module, name, fn)
    try:
        yield
    finally:
        setattr(module, name, real)


def tail():
    import time
    import resource
    pc = time.process_time()
    tc = time.thread_time()
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
