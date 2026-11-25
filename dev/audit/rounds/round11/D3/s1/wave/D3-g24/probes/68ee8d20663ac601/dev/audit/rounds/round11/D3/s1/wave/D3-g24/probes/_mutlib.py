# Shared helper of box D3-g24's probes (not a harness itself): apply a one-line mutant to a
# production function IN MEMORY by recompiling the function from its own source with the
# anchored line replaced, so the gate's tree on disk is never touched.
# Also prints the harness-contract footer (thread_factor, load1, swapins).
import inspect, os, sys, textwrap, time
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
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
_T0 = (time.process_time(), time.thread_time())


def mutated(owner, name, old, new, module):
    """The function owner.name recompiled with the line `old` (stripped match, exactly one
    occurrence) replaced by `new`; globals are the production module's own dict."""
    fn = inspect.getattr_static(owner, name) if inspect.isclass(owner) else getattr(owner, name)
    raw = fn.__func__ if isinstance(fn, (staticmethod, classmethod)) else fn
    src = textwrap.dedent(inspect.getsource(raw))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor {o!r} found {src.count(o)} times"
    ns = dict(module.__dict__)
    exec(compile(src.replace(o, n, 1), module.__file__, "exec"), ns)
    out = ns[name]
    return staticmethod(out) if isinstance(fn, staticmethod) else out


def footer():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")
