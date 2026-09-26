"""D10 verify-v2 for D10-s1-03: is a Tibber auth refusal distinguishable from a transient failure at the HA boundary?

Metric (auth_indistinct): over the auth arms {401, 403}, driven through the full
steady-cycle wrapper coordinator:HeatPumpOptimizerCoordinator._async_update_data
(not _fetch_tibber_prices alone), count arms whose escaping exception type is
the same type the HTTP-500 control arm delivers (i.e. HA cannot tell auth from
transient). Also: tibber_posts_after_verdict = Tibber POSTs in cycles 2..4 of
four consecutive 401 cycles (upstream HA stops scheduling refreshes after
ConfigEntryAuthFailed, so the correct value there is 0); and
wrapper_rewraps = whether an auth-class exception raised inside the fetch
leaves _async_update_data as some other type (1 = re-wrapped).
Count key: type(exc) escaping the production wrapper; session.post call count.
Also: static raise-site census of ConfigEntryAuthFailed in the integration (AST).
Perturbation: --perturb authraise patches _tibber_fetch_failed (in memory) to raise a
local ConfigEntryAuthFailed(IntegrationError) once reauth started, and wraps
_async_update_data to pass it through -> auth_indistinct must go 2 -> 0.
Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v2/auth_class.py [--perturb authraise]
Expected baseline: auth_indistinct=2, posts_after_verdict=3, wrapper_rewraps=1, authfailed_raise_sites=0 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 cores, CPython 3.14.0rc2.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, asyncio, logging, pathlib, sys, time  # noqa: E402
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const, coordinator as cm  # noqa: E402
from homeassistant import exceptions as ha_exc  # noqa: E402
logging.disable(logging.CRITICAL)
PERTURB = "authraise" in sys.argv
AuthFailed = getattr(ha_exc, "ConfigEntryAuthFailed", None) or type("ConfigEntryAuthFailed", (ha_exc.IntegrationError,), {})
C = cm.HeatPumpOptimizerCoordinator


class _R:
    def __init__(self, s): self.status = s
    async def json(self): return {"data": {}}
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


class Sess:
    def __init__(self, s): self.s, self.posts = s, 0
    def post(self, *a, **k): self.posts += 1; return _R(self.s)


def make(status):
    sess = Sess(status)
    cm.async_get_clientsession = lambda hass, verify_ssl=True: sess
    hass = FakeHass(); hass.states.set("sensor.indoor", FakeState("21.0"))
    e = FakeEntry(data={const.CONF_TIBBER_TOKEN: "tok", const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"})
    e.async_start_reauth = lambda h: None
    c = C(hass, e); c._skip_solve_once = False
    return c, sess


if PERTURB:
    _ff, _ud = C._tibber_fetch_failed, C._async_update_data
    def ff(self, reason, *, exc_info=False):
        if self._tibber_reauth_started:
            raise AuthFailed(reason)
        return _ff(self, reason, exc_info=exc_info)
    async def ud(self):
        try:
            return await _ud(self)
        except Exception as err:
            e = err
            while e is not None:
                if isinstance(e, AuthFailed): raise e
                e = e.__cause__ or e.__context__
            raise
    C._tibber_fetch_failed, C._async_update_data = ff, ud


async def cycle(c):
    try:
        await c._async_update_data(); return None
    except Exception as err:  # the delivered type is the metric
        return type(err)


async def main():
    ctrl_c, _ = make(500); ctrl = await cycle(ctrl_c)
    indistinct = 0
    for st in (401, 403):
        c, s = make(st); t = await cycle(c)
        indistinct += int(t is ctrl)
        print(f"arm=steady_{st} delivered={t.__name__ if t else None} control_500={ctrl.__name__} reauth_started={c._tibber_reauth_started} posts={s.posts}")
    c, s = make(401); await cycle(c); first = s.posts
    for _ in range(3): await cycle(c)
    after = s.posts - first
    # wrapper re-wrap probe: an auth-class error from inside the fetch
    c2, _ = make(200)
    async def boom(self): raise AuthFailed("probe")
    orig = C._fetch_tibber_prices; C._fetch_tibber_prices = boom
    try:
        t = await cycle(c2)
    finally:
        C._fetch_tibber_prices = orig
    rewraps = int(t is not AuthFailed)
    print(f"probe: AuthFailed raised in fetch escapes _async_update_data as {t.__name__ if t else None}")
    sites = 0
    for p in pathlib.Path("custom_components/heatpump_optimizer").rglob("*.py"):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.Raise) and n.exc is not None and "ConfigEntryAuthFailed" in ast.unparse(n.exc):
                sites += 1
    print(f"MODE {'authraise' if PERTURB else 'baseline'}")
    print(f"RESULT auth_indistinct={indistinct} arms (of 2)")
    print(f"RESULT tibber_posts_after_verdict={after} posts (cycles 2..4)")
    print(f"RESULT wrapper_rewraps={rewraps} count")
    print(f"RESULT authfailed_raise_sites={sites} count")

t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + next(l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')))
except Exception:
    print("RESULT swapins=unknown")
