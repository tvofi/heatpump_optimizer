"""V3 leads sub-seat, round 9: D12-s3-81 (grid-fee bounds are SEK numbers) driven
through REAL Home Assistant options-flow schema validation, not a direct call
to ``config_flow._page_schema`` (the lead harness's approach) and not
tests/hastub.

METRIC (one line): with ``hass.config.currency`` set to each of HUF, ISK, JPY,
KRW (the lead's blocked set) plus the null-control currencies SEK/EUR/NOK/DKK,
a 0.05 EUR/kWh fee (converted at the lead's stated table) is posted to the REAL
``OptionsFlow.async_step_grid_fees`` two ways: (a) as ``grid_fee_fixed`` through
the real ``FlowManager.async_configure``, which applies the page's real
``vol.Schema``/``NumberSelector`` -- a value over the selector's ``max`` is a
real ``vol.Invalid`` the frontend would show as a form error, not a Python
attribute read directly; (b) as the ``grid_fee_rules`` text, read by the flow's
own ``spec_problem`` call exactly as production runs it, through the real
step. RESULT counts are real schema-validation outcomes.

RUN (from repo root; NOT PYTHONPATH=tests/hastub):
  PYTHONPATH=<scratch numpy/scipy dir> /home/claude/havenv/bin/python \
    tools/audit/round9/D12/verify-v3/leads/realha_fee_currency.py [--perturb]

Perturbation (--perturb): grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH 10 -> 1e6 in
  memory (both the module's own copy and config_flow's, which imports the
  module and reads the attribute live). Expected: rules-refusal seam drops to
  0 for all four currencies; the fixed-fee selector's ``max=5`` is a distinct,
  unpatched constant and keeps refusing (matches the lead's own finding that
  the perturbation does not zero seam (b)).

EXPECTED at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact):
  real_rules_refused=2 of 4 (HUF, KRW) -- vs the lead's non-real spec_problem() count
  real_fixed_selector_invalid=4 of 4 (HUF, ISK, JPY, KRW) -- a REAL vol.Invalid
    from FlowManager.async_configure, not a bare comparison against .config["max"]
  real_null_blocked=0 of 4 (SEK, EUR, NOK, DKK)
  --perturb: real_rules_refused -> 0 of 4; real_fixed_selector_invalid unchanged (4 of 4)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence, 96b89163).
Machine: G2-leads verify-v3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import shutil
import sys
import tempfile
import time

REPO = os.getcwd()
assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"

import abc as _abc  # noqa: E402
import typing as _typing  # noqa: E402
if not hasattr(_typing, "ByteString"):
    class _ByteString(_abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    _typing.ByteString = _ByteString

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import area_registry as ar  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers import floor_registry as fr  # noqa: E402
from homeassistant.helpers import config_validation as cv  # noqa: E402
from homeassistant.helpers import label_registry as lr  # noqa: E402
import voluptuous as vol  # noqa: E402
import voluptuous_serialize  # noqa: E402

assert "hastub" not in homeassistant.__file__, homeassistant.__file__
PERTURB = "--perturb" in sys.argv
DOMAIN = "heatpump_optimizer"

FX = {"EUR": 1.0, "SEK": 11.2, "NOK": 11.7, "DKK": 7.46, "HUF": 395.0,
      "ISK": 145.0, "JPY": 160.0, "KRW": 1450.0}
NULL = ("SEK", "EUR", "NOK", "DKK")
BLOCKED_EXPECT = ("HUF", "ISK", "JPY", "KRW")
FEE_EUR = 0.05


async def make_hass(tmp, currency):
    hass = core.HomeAssistant(tmp)
    hass.config.skip_pip = True
    hass.config.currency = currency
    hass.config.language = "en"
    await hass.config.async_set_time_zone("Europe/Stockholm")
    loader.async_setup(hass)
    for reg in (ar, fr, lr, dr, er):
        await reg.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    hass.config.components.add("http")
    return hass


def add_entry(hass, data=None, options=None, title="HPO"):
    entry = config_entries.ConfigEntry(
        data=data or {}, discovery_keys={}, domain=DOMAIN, minor_version=1,
        options=options or {}, source="user", subentries_data=None, title=title,
        unique_id=None, version=1,
    )
    hass.config_entries._entries[entry.entry_id] = entry
    return entry


BASE_CONFIG = {"name": "HPO", "price_source": "entity", "price_entity": "sensor.nordpool",
               "weather_entity": "weather.home"}


def initial_data(fields):
    """The frontend's computeInitialHaFormData over a serialised schema (the
    same rule the D4/D12 verify-v3 flow harnesses use)."""
    out = {}
    for f in fields:
        desc = f.get("description") or {}
        if desc.get("suggested_value") is not None:
            out[f["name"]] = desc["suggested_value"]
        elif "default" in f:
            out[f["name"]] = f["default"]
        elif f.get("type") == "expandable":
            out[f["name"]] = initial_data(f.get("schema", []))
        elif not f.get("required"):
            continue
        elif "selector" in f:
            sel = f["selector"]
            if "boolean" in sel:
                out[f["name"]] = False
            elif "number" in sel:
                out[f["name"]] = sel["number"].get("min", 0)
            elif "select" in sel:
                o = sel["select"]["options"][0]
                out[f["name"]] = o["value"] if isinstance(o, dict) else o
            else:
                out[f["name"]] = ""
    return out


def untouched(schema, overrides=None):
    ser = voluptuous_serialize.convert(schema, custom_serializer=cv.custom_serializer)
    data = initial_data(ser)
    data.update(overrides or {})
    return data


async def grid_fees_form(hass, entry):
    """Drive the REAL OptionsFlowManager to the grid_fees page, the way the
    frontend would: init (menu) > advanced (menu) > grid_fees (form). Calling
    ``async_step_grid_fees`` directly, bypassing the FlowManager, leaves its
    ``cur_step`` unchanged (still ``init``), so a later ``async_configure``
    validates the submission against the WRONG page's schema -- caught the
    hard way while building this harness (a bug in the harness, not in HPO)."""
    mgr = hass.config_entries.options
    res = await mgr.async_init(entry.entry_id)
    assert res["type"] == "menu", res
    res = await mgr.async_configure(res["flow_id"], {"next_step_id": "advanced"})
    assert res["type"] == "menu", res
    res = await mgr.async_configure(res["flow_id"], {"next_step_id": "grid_fees"})
    assert res["type"] == "form" and res["step_id"] == "grid_fees", res
    return mgr, res, mgr._progress[res["flow_id"]]


async def rules_refused(hass, entry, fee):
    mgr, res, flow = await grid_fees_form(hass, entry)
    post = untouched(res["data_schema"], {"grid_fee_rules": f"= {fee}"})
    res2 = await mgr.async_configure(res["flow_id"], post)
    refused = bool((res2.get("errors") or {}).get("grid_fee_rules"))
    if res2["type"] in ("form", "menu"):
        mgr.async_abort(res["flow_id"])
    return refused, (res2.get("errors") or {})


async def fixed_selector_invalid(hass, entry, fee):
    """Post the fixed-fee field through the REAL FlowManager.async_configure,
    which applies the page's real vol.Schema (NumberSelector) itself -- a
    genuine vol.Invalid on an over-max value, the frontend's own refusal path,
    not a Python comparison against the selector's .config["max"]."""
    mgr, res, flow = await grid_fees_form(hass, entry)
    post = untouched(res["data_schema"], {"grid_fee_fixed": fee})
    invalid = False
    try:
        res2 = await mgr.async_configure(res["flow_id"], post)
        if res2["type"] in ("form", "menu"):
            mgr.async_abort(res["flow_id"])
    except Exception as exc:  # noqa: BLE001
        # data_entry_flow.InvalidData wraps the real vol.Invalid/MultipleInvalid
        # the FlowManager raised while applying the page's real vol.Schema.
        invalid = "InvalidData" in type(exc).__name__ or isinstance(exc, vol.Invalid)
        if not invalid:
            print(f"#   unexpected {type(exc).__name__}: {exc}")
        try:
            mgr.async_abort(res["flow_id"])
        except Exception:  # noqa: BLE001
            pass
    return invalid


async def main():
    tmp = tempfile.mkdtemp(prefix="realha_d12v3_")
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(tmp, "custom_components"))
    sys.path.insert(0, tmp)
    from custom_components.heatpump_optimizer import grid_fee  # noqa: E402

    if PERTURB:
        grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH = 1e6

    rules_n, fixed_n, null_blocked = 0, 0, 0
    blocked_currencies = []
    for cur, fx in FX.items():
        fee = round(FEE_EUR * fx, 2)
        hass = await make_hass(tmp, cur)
        entry = add_entry(hass, data=dict(BASE_CONFIG))
        refused, errs = await rules_refused(hass, entry, fee)
        invalid = await fixed_selector_invalid(hass, entry, fee)
        rules_n += int(refused)
        fixed_n += int(invalid)
        blocked_here = refused or invalid
        if blocked_here:
            blocked_currencies.append(cur)
        if cur in NULL and blocked_here:
            null_blocked += 1
        print(f"CUR {cur} fee={fee:g} {cur}/kWh real_rules_refused={int(refused)} "
              f"errors={errs} real_fixed_invalid={int(invalid)}")
        await hass.async_stop(force=True)

    print(f"RESULT fee_eur_per_kwh={FEE_EUR:g} assumed")
    print(f"RESULT real_rules_refused={rules_n} of {len(FX)}")
    print(f"RESULT real_fixed_selector_invalid={fixed_n} of {len(FX)}")
    print(f"RESULT real_blocked_currencies={len(blocked_currencies)} of {len(FX)} "
          f"({','.join(blocked_currencies)})")
    print(f"RESULT real_null_blocked={null_blocked} of {len(NULL)}")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT ha_version={HA_VERSION}")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    t0, tt0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={(pc / tc) if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
