"""Probes for the class-P2 seams the round-11 sweep dispositions as instances beyond a finding.

Each probe asks the seam and the fact's owner (or the sibling that holds the guard) the
same question and FAILS when the answers differ. `--perturb` gives each seam its sibling's
guard in memory, so every probe must then pass: the probe detects the divergence and
nothing else.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P2/probes_p2.py [--perturb]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components"),
                str(ROOT / "dev/audit/rounds/round11/D17/s3")]
from harness import FakeHass, FakeEntry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod, const  # noqa: E402
from heatpump_optimizer import boost, pump_schedule, replay_doc  # noqa: E402
from heatpump_optimizer.const import finite_float  # noqa: E402
from heatpump_optimizer.dhw_schedule import windows_for_day, hour_in_windows  # noqa: E402
from heatpump_optimizer.dhw_draws import window_label  # noqa: E402

PERTURB = "--perturb" in sys.argv
RESULTS: list[tuple[str, bool, str]] = []


def record(name, failed, detail):
    RESULTS.append((name, failed, detail))
    print(f"{'FAIL' if failed else 'pass'} {name} -- {detail}")


# -- F14: the hot-water window at an instant, flat union vs the weekday's ---------------
SPEC = "weekdays 06:00-08:30, weekend 08:00-09:30"
SAT_0700 = datetime(2026, 1, 17, 7, 0, tzinfo=timezone.utc)  # a Saturday


def _params(spec=SPEC):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
           "outdoor_temp_entity": "sensor.outdoor", "dhw_enabled": True, "dhw_schedule_enabled": True,
           "dhw_windows": spec}
    c = coord_mod.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))
    return getattr(c, "_ctx", c)._thermal_params


def _day(params, when):
    return windows_for_day(params.dhw_weekly_windows, when.weekday(), list(params.dhw_windows))


def probe_flat_windows():
    p = _params()
    truth = hour_in_windows(7.0, _day(p, SAT_0700))
    hour = SAT_0700.hour + SAT_0700.minute / 60.0
    # boost._window_open with no plan (its fallback is params.dhw_demand_windows)
    snap = SimpleNamespace(plan=None, params=p)
    if PERTURB:
        snap = SimpleNamespace(plan=None, params=SimpleNamespace(dhw_demand_windows=_day(p, SAT_0700)))
    got = boost._window_open(snap, SAT_0700)
    record("boost._window_open", got != truth, f"Saturday 07:00: seam open={got}, weekday's window open={truth}")
    # _async_drive_pumps hands vvc_should_run list(params.dhw_windows) (coordinator.py:4507-4515)
    windows = _day(p, SAT_0700) if PERTURB else list(p.dhw_windows)
    run, _ = pump_schedule.vvc_should_run(hour, windows, 0.0)
    want, _ = pump_schedule.vvc_should_run(hour, _day(p, SAT_0700), 0.0)
    record("coordinator._async_drive_pumps (VVC)", run != want,
           f"Saturday 07:00: circulation pump run={run}, on the weekday's windows run={want}")
    # dhw_learning.async_fold_draw_stats labels a draw by params.dhw_demand_windows
    windows = _day(p, SAT_0700) if PERTURB else p.dhw_demand_windows
    lab, want = window_label(hour, windows), window_label(hour, _day(p, SAT_0700))
    record("DhwProfileLearner.async_fold_draw_stats (draw label)", lab != want,
           f"Saturday 07:00 draw labelled {lab!r}, the weekday's window says {want!r}")


# -- F16: `a finite number or nothing` against finite_float ----------------------------
def probe_finite():
    probes = (float("nan"), float("inf"), -float("inf"))
    owner = [finite_float(v) is None for v in probes]
    fn = replay_doc._number
    if PERTURB:
        def fn(v):
            out = replay_doc._number(v)
            return replay_doc._DROP if isinstance(out, float) and not math.isfinite(out) else out
    seam = [fn(v) in (None, replay_doc._DROP) for v in probes]
    bad = sum(a != b for a, b in zip(owner, seam))
    record("replay_doc._number", bad > 0, f"{bad} of {len(probes)} non-finite probes kept where finite_float refuses")


# -- F04: zone fact on an install whose model is single-zone ---------------------------
async def _single_zone_install(extra):
    import rig
    rig.freeze()
    inst = rig.Install(entry_id="p2sz", data=rig.base_config(two_zone_mode="off", **extra))
    await inst.setup()
    return inst


def probe_zone():
    import rig

    async def go():
        inst = await _single_zone_install({})
        d = await inst.cycle()
        assert d.get("two_zone_enabled") is False, d.get("two_zone_enabled")
        rows = d.get("schedule") or []
        if PERTURB:  # the published columns gated on the model's mode, as the plan views should be
            rows = [{**r, "upper_temp": None, "lower_temp": None} for r in rows]
        zoned = sum(1 for r in rows if r.get("upper_temp") is not None or r.get("lower_temp") is not None)
        record("coordinator._apply_result_payload (schedule upper/lower)", zoned > 0,
               f"single-zone (two_zone_enabled=False): {zoned} of {len(rows)} schedule rows publish a zone temperature")
        # min_room_temperature: _sim_coldest over upper/lower/room against the room trajectory alone
        plan = getattr(inst.coord, "_last_result", None) or getattr(getattr(inst.coord, "_ctx", inst.coord), "_last_result", None)
        if plan is None:
            plan = getattr(inst.coord, "_optimization_result", None)
        if plan is not None and getattr(plan, "room_temp_trajectory", None):
            seam = coord_mod._sim_coldest(plan) if not PERTURB else round(min(plan.room_temp_trajectory), 2)
            owner = round(min(plan.room_temp_trajectory), 2)
            record("coordinator._sim_coldest (single-zone)", seam != owner,
                   f"min over zone+room trajectories {seam} vs the single-zone room trajectory's {owner}")
        else:
            print("  _sim_coldest: no plan object found on the coordinator")
    asyncio.run(go())

    # set_thermal_parameters with a two-zone-only field on a single-zone install (mode off),
    # one fresh install per field; --perturb asks the field the single-zone model reads
    for field, value in (("upper_floor_thermal_mass", 40.0), ("lower_floor_thermal_mass", 40.0),
                         ("inter_zone_heat_transfer", 1.5)):
        async def one(field=field, value=value):
            inst = await _single_zone_install({})
            d = await inst.cycle()
            before = sum(float(r.get("power") or 0) for r in d.get("schedule") or [])
            asked, val = ("house_thermal_mass", 40.0) if PERTURB else (field, value)
            err = None
            try:
                await inst.call("set_thermal_parameters", {asked: val})
            except Exception as exc:  # noqa: BLE001 - a refusal is the guarded answer
                err = exc
            after = sum(float(r.get("power") or 0) for r in (await inst.cycle()).get("schedule") or [])
            await inst.restart()
            rd = await inst.cycle()
            restarted = sum(float(r.get("power") or 0) for r in rd.get("schedule") or [])
            inert = err is None and abs(after - before) < 0.05 and abs(restarted - before) < 0.05
            record(f"coordinator._THERMAL_PARAM_FIELDS.{field} (single-zone)", inert,
                   f"asked {asked}={val}: accepted={err is None}; plan delta {abs(after - before):.3f} kW-steps, "
                   f"after restart {abs(restarted - before):.3f} (two_zone after restart={rd.get('two_zone_enabled')})")
        asyncio.run(one())


# -- F03: reauth writes the token into data; a saved Entities page shadows it ----------
def probe_reauth():
    from heatpump_optimizer import config_flow
    from homeassistant.data_entry_flow import AbortFlow
    from harness import FakeState
    sys.path.insert(0, str(ROOT / "dev/audit/rounds/round11/D10/s2"))
    from golden import _presented_fields

    data = {config_flow.CONF_NAME: "Heat Pump Optimizer", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_TIBBER,
            const.CONF_TIBBER_TOKEN: "token-old", const.CONF_WEATHER_ENTITY: "weather.home",
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"}

    async def go():
        hass = FakeHass()
        hass.states.set("sensor.indoor_a", FakeState("21.0"))
        hass.states.set("weather.home", FakeState("cloudy"))
        entry = FakeEntry(data=dict(data), entry_id="e1", unique_id=config_flow.entry_identity(data))
        hass.config_entries.entries.append(entry)
        opts = config_flow.HeatPumpOptimizerOptionsFlow(entry)
        opts.hass = hass
        form = await opts.async_step_entities(None)
        answers = {}
        for key, _v in _presented_fields(form["data_schema"]):
            name = str(getattr(key, "schema", key))
            sv = (getattr(key, "description", None) or {}).get("suggested_value")
            dv = key.default() if callable(getattr(key, "default", None)) else None
            val = sv if sv is not None else dv
            if val is not None:
                answers[name] = val
        answers[config_flow.CONF_AFTER_SAVE] = config_flow.AFTER_SAVE_CLOSE
        res = await opts.async_step_entities(answers)
        if res.get("type") == "create_entry":
            entry.options = dict(res["data"])
        saved = entry.options.get(const.CONF_TIBBER_TOKEN, "<absent>")
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = hass
        flow.context = {"source": "reauth", "entry_id": "e1"}
        if PERTURB:  # the reauth write drops the key from options in the same update, as data+options writers do
            orig = hass.config_entries.async_update_entry

            def upd(e, **kw):
                if "data" in kw and "options" not in kw:
                    kw["options"] = {k: v for k, v in e.options.items() if k not in kw["data"]}
                return orig(e, **kw)
            hass.config_entries.async_update_entry = upd
        with mock.patch.object(config_flow, "validate_tibber_token", new=mock.AsyncMock(return_value="ok")):
            try:
                await flow.async_step_reauth(dict(entry.data))
                out = await flow.async_step_reauth_confirm({const.CONF_TIBBER_TOKEN: "token-new"})
            except AbortFlow as err:
                out = {"type": "abort", "reason": err.reason}
        effective = {**entry.data, **entry.options}.get(const.CONF_TIBBER_TOKEN)
        print(f"  reauth out: { {k: out.get(k) for k in ('type', 'step_id', 'errors', 'reason')} } options_keys={sorted(entry.options)[:8]}")
        record("config_flow.async_step_reauth_confirm", out.get("reason") == "reauth_successful" and effective != "token-new",
               f"Entities page saved token {saved!r}; reauth -> {out.get('type')}/{out.get('reason')}; "
               f"effective token {effective!r}")
    asyncio.run(go())


def main():
    for p in (probe_flat_windows, probe_finite, probe_zone, probe_reauth):
        try:
            p()
        except Exception as exc:  # noqa: BLE001 - a probe that cannot run is reported, never passed
            record(p.__name__, True, f"PROBE-ERROR {type(exc).__name__}: {exc}")
    failed = sum(f for _, f, _ in RESULTS)
    print(f"RESULT probes={len(RESULTS)}")
    print(f"RESULT probes_failed={failed} of {len(RESULTS)}{' (--perturb)' if PERTURB else ''}")


if __name__ == "__main__":
    main()
