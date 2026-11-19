#!/usr/bin/env python3
"""D12-s1 focused harness: a single-zone install publishes an upper/lower floor in its space plan.

Metric (one line): zone_plants = single-zone plants (two_zone_enabled published False) whose published
space plan (`data['space_plan']['forecast']`, what sensor.heat_pump_optimizer_plan_space_heating and the
card read) carries a non-null `upper` or `lower` on any row; zone_rows = such rows summed over plants.
Count key: the PUBLISHED payload after one real cycle (coordinator._async_update_data ->
_build_plan_views), compared with the model's own published `two_zone_enabled`; nothing reads the config.

Command (export root, or the root of any checkout of the tree under test):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s1/plan_zone.py [--gate]
  --gate  perturbation (in memory, the one-line production change): HeatPumpOptimizerCoordinator.
          _build_plan_views decides `two_zone` from the model's params.two_zone_enabled instead of from
          the result carrying both trajectories; zone_plants must fall to 0 and the two-zone null
          control must keep its rows.
Second metric (one line): invented_zone_plants = plants storing no zone key (CONF_UPPER/LOWER_FLOOR_THERMAL_MASS,
CONF_INTER_ZONE_TRANSFER, CONF_RADIATOR_POWER_FRACTION) and no two_zone_mode 'on' whose cycle PUBLISHES
two_zone_enabled=True (a second zone the config omits, with the lower floor's default parameters).
  --presence-rule  perturbation (in memory): ThermalParameters.from_config decides two_zone_mode 'auto' (the
          default) by the presence of a zone key, the rule thermal_model.py's own comment and const.py's
          TWO_ZONE_MODE comment state; invented_zone_plants must fall to 0, the control keep two zones.
Null control: the two-zone plant (zone keys stored, two_zone_enabled published True) is printed apart
(`control_two_zone_rows`); it must carry rows on both arms, with upper != lower.
Leave-one-out: printed over the single-zone plants (PLANTS below, 8 cells).
Expected: at git archive 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 zone_plants=8 (exact), zone_rows=768
(8 x 96, exact); --gate: zone_plants=0. In the export handed to D12-s1 (which carries a changed
thermal_model.py two-zone rule), the default plants publish two_zone_enabled=True and are therefore not
counted here as single-zone; see REPORT.md.
Machine: box B4 (4 vCPU container, shared), Python 3.14, numpy/scipy per tests/requirements-ci.txt.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import argparse, asyncio, sys, time, tempfile
from datetime import timedelta

os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d12s1_pz_"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells  # noqa: E402  (the plant builders and the network-free patches; cells.py's main is guarded)
from cells import C, Spec  # noqa: E402

# Single-zone plants: no zone key stored and two_zone_mode explicitly 'off' where the plant also stores
# zone keys; the model reads single zone in each (checked below, not assumed).
PLANTS = {
    "minimal": Spec(),
    "dhw": Spec(feats={"dhw"}),
    "dhw+pv": Spec(feats={"dhw", "pv"}),
    "wood": Spec(feats={"wood"}, ents={C.CONF_WOOD_TANK_TOP_ENTITY}),
    "valve": Spec(feats={"valve"}),
    "dhw+valve+pv": Spec(feats={"dhw", "valve", "pv"}),
    "zone keys, mode off": Spec(feats={"dhw"}, extra={**cells.FEATURE_KEYS["zone"], C.CONF_TWO_ZONE_MODE: "off"}),
    "minimal, mode off": Spec(extra={C.CONF_TWO_ZONE_MODE: "off"}),
}
CONTROL = Spec(feats={"dhw", "zone"}, ents={C.CONF_LOWER_FLOOR_TEMP_ENTITY}, extra={C.CONF_TWO_ZONE_MODE: "on"})


async def one(spec):
    cfg = spec.config()
    hass = cells.make_hass(spec, cfg)
    entry = cells.FakeEntry(data=cfg)
    await cells.integ.async_setup_entry(hass, entry)
    coord = entry.runtime_data
    data = await coord._async_update_data()
    rows = (data.get("space_plan") or {}).get("forecast") or []
    zrows = sum(1 for r in rows if r.get("upper") is not None or r.get("lower") is not None)
    split = sum(1 for r in rows if r.get("upper") is not None and r.get("lower") is not None and r["upper"] != r["lower"])
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    return bool(data.get("two_zone_enabled")), zrows, len(rows), split


ZONE_KEYS = (C.CONF_UPPER_FLOOR_THERMAL_MASS, C.CONF_LOWER_FLOOR_THERMAL_MASS, C.CONF_INTER_ZONE_TRANSFER,
             C.CONF_RADIATOR_POWER_FRACTION)


def run(spec, gate, presence=False):
    ps = cells.patches(spec)
    if presence:
        ps.append(cells._zone_presence_rule())
    if gate:
        cells.FIX_PLAN_ZONE = True
        ps.append(cells._plan_zone_gate())
    for p in ps:
        p.start()
    cells.dt_util.freeze(cells.START + timedelta(hours=6))
    try:
        return asyncio.run(one(spec))
    finally:
        cells.dt_util.freeze(None)
        for p in reversed(ps):
            p.stop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--presence-rule", action="store_true")
    a = ap.parse_args()
    cells.logging.basicConfig(level=cells.logging.CRITICAL)
    t0, th0 = time.process_time(), time.thread_time()
    per, invented = {}, []
    for name, spec in PLANTS.items():
        tz, zrows, n, split = run(spec, a.gate, a.presence_rule)
        per[name] = (tz, zrows, n)
        cfg = spec.config()
        if tz and not any(k in cfg for k in ZONE_KEYS) and cfg.get(C.CONF_TWO_ZONE_MODE) != C.TWO_ZONE_MODE_ON:
            invented.append(name)
        print(f"PLANT {name}\ttwo_zone_enabled={tz}\tzone_rows={zrows}/{n}\tsplit_rows={split}")
    single = {k: v for k, v in per.items() if not v[0]}
    vals = [1 if v[1] else 0 for v in single.values()]
    rows = [v[1] for v in single.values()]
    tz, crow, cn, csplit = run(CONTROL, a.gate, a.presence_rule)
    print(f"CONTROL two-zone\ttwo_zone_enabled={tz}\tzone_rows={crow}/{cn}\tsplit_rows={csplit}")
    print(f"RESULT arm={'gate' if a.gate else 'baseline'}{'+presence_rule' if a.presence_rule else ''}")
    print(f"RESULT invented_zone_plants={len(invented)} count ({', '.join(invented) or '-'})")
    print(f"RESULT single_zone_plants={len(single)} count")
    print(f"RESULT zone_plants={sum(vals)} count")
    print(f"RESULT zone_rows={sum(rows)} count")
    if len(rows) >= 5:
        print(f"RESULT loo_cells={len(rows)} range={min(rows)}..{max(rows)} drop_most_favourable={sum(rows) - max(rows)} rows")
    print(f"RESULT control_two_zone_enabled={tz}")
    print(f"RESULT control_two_zone_rows={crow} count")
    print(f"RESULT control_split_rows={csplit} count")
    cpu, th = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / th if th else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = int([ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1])
    except Exception:  # noqa: BLE001
        sw = 0
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
