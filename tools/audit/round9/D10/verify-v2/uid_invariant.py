"""D10 verify-v2 for D10-s1-01: does every identity write keep entry.unique_id == entry_identity(effective)?

Metric: over every (seam, identity key) pair -- the reauth confirm step (token)
and each options page field whose key is an identity key (enumerated at run
time from config_flow._OPTION_FIELDS against {token, price entity,
_IDENTITY_ENTITY_KEYS}) -- set up entry E through the real config flow, change
that one key through that seam, and count pairs where afterwards
entry.unique_id != config_flow.entry_identity({**data, **options}).
Count key: entry.unique_id as the production write left it, against the
production entry_identity of the effective config. Options pages are driven
twice: after_save=menu (production async_update_entry) and after_save=close
(the flow's async_create_entry data applied as options, as the real options
flow manager does).
Null controls: (a) a non-identity field (price_vat) on the entities page, both
save modes -> must stay 0; (b) the reconfigure seam with a new token -> 0.
Perturbation: --perturb restamp wraps HeatPumpOptimizerOptionsFlow._save_or_menu,
_save and async_step_reauth_confirm to set entry.unique_id = entry_identity(eff)
after the write (the seam-level fix) -> stale must go to 0.
Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v2/uid_invariant.py [--perturb restamp]
Expected baseline: stale_pairs = 2*15+1 = 31 (+-0), controls 0. restamp: 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 cores, CPython 3.14.0rc2.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time  # noqa: E402
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf, const  # noqa: E402
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402

PERTURB = "restamp" in sys.argv


class _R:
    def __init__(self, s, p): self.status, self._p = s, p
    async def json(self): return self._p
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


class _S:
    def post(self, *a, **k): return _R(200, {"data": {"viewer": {"name": "x"}}})


cf.async_get_clientsession = lambda hass, verify_ssl=True: _S()
IDS = {cf.CONF_TIBBER_TOKEN, cf.CONF_PRICE_ENTITY, *cf._IDENTITY_ENTITY_KEYS}
BASE = {"name": "HPO", const.CONF_TIBBER_TOKEN: "tok-a", const.CONF_WEATHER_ENTITY: "weather.home",
        const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.p", const.CONF_INDOOR_TEMP_ENTITY: "sensor.in"}


def eff(e): return {**e.data, **e.options}
def stale(e): return e.unique_id != cf.entry_identity(eff(e))


if PERTURB:
    OF = cf.HeatPumpOptimizerOptionsFlow
    _som, _sv, _rc = OF._save_or_menu, OF._save, cf.HeatPumpOptimizerConfigFlow.async_step_reauth_confirm
    async def som(self, ui):
        r = await _som(self, ui); self._entry.unique_id = cf.entry_identity(eff(self._entry)); return r
    def sv(self, ui):
        r = _sv(self, ui); self._stamp_after_close = True; return r
    async def rc(self, ui=None):
        r = await _rc(self, ui)
        if self._reauth_entry is not None:
            self._reauth_entry.unique_id = cf.entry_identity(eff(self._reauth_entry))
        return r
    OF._save_or_menu, OF._save = som, sv
    cf.HeatPumpOptimizerConfigFlow.async_step_reauth_confirm = rc


async def setup(hass):
    f = cf.HeatPumpOptimizerConfigFlow(); f.hass = hass
    first = {k: BASE[k] for k in ("name", const.CONF_TIBBER_TOKEN, const.CONF_WEATHER_ENTITY)}
    await f.async_step_user(dict(first))
    await f.async_step_user_sensors({k: v for k, v in BASE.items() if k not in first})
    e = FakeEntry(data=dict(BASE), entry_id="E", unique_id=f.unique_id)
    hass.config_entries.entries.append(e)
    assert not stale(e)
    return e


def newval(key):
    if key == cf.CONF_TIBBER_TOKEN: return "tok-new"
    dom = {"weather_entity": "weather", "heat_pump_switch_entity": "switch"}.get(key, "sensor")
    return f"{dom}.new_{key}"


async def options_write(key, val, mode):
    hass = FakeHass(); e = await setup(hass)
    of = cf.HeatPumpOptimizerOptionsFlow(e); of.hass = hass
    page = next(r[0] for r in cf._OPTION_FIELDS if r.key == key)
    await getattr(of, f"async_step_{page}")(None)
    keys = {r.key for r in cf._OPTION_FIELDS if r[0] == page}
    ui = {k: v for k, v in eff(e).items() if k in keys}
    ui[key] = val
    ui[cf.CONF_AFTER_SAVE] = cf.AFTER_SAVE_CLOSE if mode == "close" else cf.AFTER_SAVE_MENU
    try:
        res = await getattr(of, f"async_step_{page}")(ui)
    except AbortFlow as err:
        res = {"type": "abort", "reason": err.reason}
    if mode == "close" and res.get("type") == "create_entry":
        e.options = dict(res["data"])  # the real OptionsFlowManager applies the result as options
        if PERTURB: e.unique_id = cf.entry_identity(eff(e))
    applied = eff(e).get(key) == val
    return applied, stale(e), res.get("type")


async def main():
    stale_n = unapplied = pairs = 0
    fields = [r for r in cf._OPTION_FIELDS if r.key in IDS]
    for r in fields:
        for mode in ("menu", "close"):
            applied, st, typ = await options_write(r.key, newval(r.key), mode)
            pairs += 1; unapplied += (not applied); stale_n += (applied and st)
            print(f"seam=options:{r[0]:18s} key={r.key:28s} mode={mode:5s} result={typ:12s} applied={applied} stale={st}")
    hass = FakeHass(); e = await setup(hass)
    ra = cf.HeatPumpOptimizerConfigFlow(); ra.hass = hass; ra.context = {"source": "reauth", "entry_id": "E"}
    await ra.async_step_reauth(e.data)
    res = await ra.async_step_reauth_confirm({const.CONF_TIBBER_TOKEN: "tok-new"})
    st = stale(e); pairs += 1; stale_n += st
    print(f"seam=reauth_confirm key=tibber_token result={res.get('reason')} stale={st}")
    ctrl = 0
    for mode in ("menu", "close"):
        applied, st, typ = await options_write(const.CONF_PRICE_VAT, 1.07, mode)
        ctrl += st; print(f"control non-identity price_vat mode={mode} applied={applied} stale={st}")
    hass = FakeHass(); e = await setup(hass)
    rf = cf.HeatPumpOptimizerConfigFlow(); rf.hass = hass; rf.context = {"source": "reconfigure", "entry_id": "E"}
    await rf.async_step_reconfigure({"name": "HPO", const.CONF_TIBBER_TOKEN: "tok-new", const.CONF_WEATHER_ENTITY: "weather.home"})
    await rf.async_step_user_sensors({const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.p", const.CONF_INDOOR_TEMP_ENTITY: "sensor.in"})
    ctrl += stale(e); print(f"control reconfigure token applied={e.data.get(const.CONF_TIBBER_TOKEN)=='tok-new'} stale={stale(e)}")
    print(f"MODE {'restamp' if PERTURB else 'baseline'}")
    print(f"RESULT identity_fields_in_options={len(fields)} count")
    print(f"RESULT pairs={pairs} count")
    print(f"RESULT unapplied_pairs={unapplied} count")
    print(f"RESULT stale_pairs={stale_n} count")
    print(f"RESULT control_stale={ctrl} count")

t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + next(l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')))
except Exception:
    print("RESULT swapins=unknown")
