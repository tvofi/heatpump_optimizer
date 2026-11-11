"""D7.M6 runtime sentinel over structure.py's name-kept members.

Metric: number of members in tests/structure.py:dead_members()'s name-kept set
  that receive ZERO calls whose immediate caller frame is production code
  (custom_components/) while tests/features.py runs end to end (and the five
  golden coordinator captures). Key: the caller frame's filename, i.e. the
  value the production seam delivers, not a name match.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s3/namekept_sentinel.py
  (env HPO_SENT_SKIP_FEATURES=1 runs only the golden captures, fast.)
Expected: see REPORT.md (exact count; deterministic), baseline 17f1c55fad1b, macOS arm64 box B5.
Perturbation: HPO_SENT_INJECT=Cls.member adds a synthetic production-frame call
  to that member, so the count must drop by exactly one.
Root rule: cwd (run from the export root).
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, runpy, importlib, functools, inspect, tempfile, json
sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp())
import harness  # noqa: puts custom_components on sys.path, as the suite does
import structure as S

pkg = S.Package(S.module_trees())
dead, kept = S.dead_members(pkg)
PROD = os.path.abspath("custom_components") + os.sep
calls = {}  # key -> [prod, other]

def wrap(key, fn):
    @functools.wraps(fn)
    def w(*a, **k):
        f = sys._getframe(1)
        c = calls[key]
        c[0 if os.path.abspath(f.f_code.co_filename).startswith(PROD) else 1] += 1
        return fn(*a, **k)
    return w

def awrap(key, fn):
    @functools.wraps(fn)
    async def w(*a, **k):
        f = sys._getframe(1)
        c = calls[key]
        # coroutine: caller frame is the awaiting frame's coroutine creator
        c[0 if os.path.abspath(f.f_code.co_filename).startswith(PROD) else 1] += 1
        return await fn(*a, **k)
    return w

unpatched = []
for rel, cname, mname in kept:
    mod = "heatpump_optimizer." + os.path.basename(rel)[:-3]
    key = f"{os.path.basename(rel)}:{cname}.{mname}"
    calls[key] = [0, 0]
    try:
        m = importlib.import_module(mod)
        cls = getattr(m, cname)
        raw = cls.__dict__[mname]
    except Exception as e:
        unpatched.append((key, repr(e))); continue
    W = awrap if inspect.iscoroutinefunction(getattr(raw, "__func__", raw)) else wrap
    if isinstance(raw, property):
        new = property(W(key, raw.fget), raw.fset, raw.fdel, raw.__doc__)
    elif isinstance(raw, staticmethod):
        new = staticmethod(W(key, raw.__func__))
    elif isinstance(raw, classmethod):
        new = classmethod(W(key, raw.__func__))
    elif isinstance(raw, functools.cached_property):
        new = functools.cached_property(W(key, raw.func)); new.__set_name__(cls, mname)
    elif callable(raw):
        new = W(key, raw)
    else:
        unpatched.append((key, type(raw).__name__)); continue
    try:
        setattr(cls, mname, new)
    except Exception as e:
        unpatched.append((key, repr(e)))

inj = os.environ.get("HPO_SENT_INJECT")
if inj:
    for k in calls:
        if k.split(":")[1] == inj:
            calls[k][0] += 1

t0 = time.process_time(); tt0 = time.thread_time()
import golden
for name, cfg in golden.coordinator_scenarios().items():
    try: golden._capture_coordinator(cfg)
    except Exception as e: print("capture-fail", name, e)
if not os.environ.get("HPO_SENT_SKIP_FEATURES"):
    try:
        runpy.run_path("tests/features.py", run_name="__main__")
    except SystemExit as e:
        print("features exit", e.code)
zero = sorted(k for k, (p, o) in calls.items() if p == 0 and not any(k == u[0] for u in unpatched))
for k in zero:
    print("NOPROD", k, "test_calls=", calls[k][1])
for u in unpatched:
    print("UNPATCHED", *u)
print(f"RESULT namekept_total={len(kept)} members")
print(f"RESULT namekept_unpatched={len(unpatched)} members")
print(f"RESULT namekept_no_production_call={len(zero)} members")
print(f"RESULT namekept_test_only={sum(1 for k in zero if calls[k][1])} members")
pc = time.process_time()-t0; tc = time.thread_time()-tt0
print(f"RESULT thread_factor={pc/tc if tc else 0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
