#!/usr/bin/env python3
# Metric: pull_prices' verdict for a Tibber reply with a given status and body (aiohttp-shaped fake session)
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e5eea05f4463602e.py
# EXPECTED RESULT pull_prices_401_html_body verdict baseline=reauth mutant=raised:ContentTypeError  (exact: counts; tolerance 0)
# EXPECTED RESULT pull_prices_502_html_body verdict baseline=fail mutant=raised:ContentTypeError  (exact: counts; tolerance 0)
# EXPECTED RESULT cases_moved=3 count (of 6)  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:_tibber_post (via pull_prices) (price_model.py line 844).
# Perturbation: `if resp.status != 200:` -> `if False:` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: sign_flip (reauth -> an exception the coordinator catches as an ordinary ClientError fetch failure).
# Null control: JSON error bodies (401, 500) and a 200 with no homes: identical.
# Count key: the value the production symbol returns (or the learner state it writes), never an input attribute.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
_T0 = (time.process_time(), time.thread_time())
from unittest import mock


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
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)


def mutant(func, line, old, new):
    """``func`` recompiled from its own source with file line ``line`` mutated (in memory only)."""
    lines, start = inspect.getsourcelines(func)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor line {line} moved: {lines[i]!r}"
    lines[i] = new + "\n"
    src = textwrap.dedent("".join(lines))
    ns = dict(pm.__dict__)
    exec(compile(src, pm.__file__, "exec"), ns)
    return ns[func.__name__]


def same(a, b):
    """Exact equality that treats nan == nan and compares arrays and exceptions."""
    if isinstance(a, BaseException) or isinstance(b, BaseException):
        return type(a) is type(b)
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True)
    if isinstance(a, float) and isinstance(b, float):
        return (a == b) or (np.isnan(a) and np.isnan(b))
    return a == b


def call(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except Exception as err:  # the mutant may raise where the baseline does not
        return err


import asyncio  # noqa: E402

import aiohttp  # noqa: E402

LINE, OLD, NEW = 844, "        if resp.status != 200:", "        if False:"
MUT = mutant(pm._tibber_post, LINE, OLD, NEW)


class _Resp:
    def __init__(self, status, body):
        self.status, self._body = status, body

    async def json(self):
        if isinstance(self._body, BaseException):
            raise self._body
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    """aiohttp.ClientSession.post's shape: every call answers with the same status and body."""

    def __init__(self, status, body):
        self.status, self.body, self.posts = status, body, 0

    def post(self, *a, **kw):
        self.posts += 1
        return _Resp(self.status, self.body)


def html_error():
    # what aiohttp's resp.json() raises on a text/html error page (a proxy 502, a gateway 401 page)
    return aiohttp.ContentTypeError(None, (), message="Attempt to decode JSON with unexpected mimetype: text/html")


async def pull(status, body):
    try:
        verdict, payload = await pm.pull_prices(_Session(status, body), {pm.CONF_TIBBER_TOKEN: "t"})
        return verdict
    except Exception as err:
        return f"raised:{type(err).__name__}"


def arms(status, body):
    b = asyncio.run(pull(status, body))
    with mock.patch.object(pm, "_tibber_post", MUT):
        m = asyncio.run(pull(status, body))
    return b, m


cases = {
    "401_html_body": (401, html_error()),
    "403_html_body": (403, html_error()),
    "502_html_body": (502, html_error()),
    "500_json_errors": (500, {"errors": [{"message": "internal"}]}),
    "401_json_errors": (401, {"errors": [{"message": "unauthorized"}]}),
    "200_no_homes(null)": (200, {"data": {"viewer": {"homes": []}}}),
}
moved = 0
for name, (st, body) in cases.items():
    b, m = arms(st, body)
    moved += int(b != m)
    print(f"RESULT pull_prices_{name} verdict baseline={b} mutant={m}")
print(f"RESULT cases_moved={moved} count (of {len(cases)})")
print(f"RESULT contenttypeerror_is_clienterror={int(issubclass(aiohttp.ContentTypeError, aiohttp.ClientError))}")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
