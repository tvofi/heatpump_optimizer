"""D14 sweep, class N-table-value: hold each enumerated table to an oracle.

Every seam enumerate.py lists is dispositioned here:
  CHECK  an independent oracle (an SI/calendar reference written here, or a
         physical ordering the table's own keys declare) is applied to the
         runtime value; a violation makes the seam an INSTANCE.
  GUARD  a named test pins the value (cited); no oracle run here.
  NA     the leaves are not physical/derived data (ids, register addresses,
         schema bounds whose correctness is a different class), with the reason.
A seam the enumerator lists but this file does not disposition is printed
UNDISPOSITIONED and fails the run (so a new table cannot pass silently).
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/table_value/oracle.py
        [--perturb SYMBOL]   one-line re-introduction in memory (see PERTURB)
        [--root DIR]         run the same enumerator+oracles on another tree
                             (null control: dev/audit/rounds/round11/D14/table_value/clean_fixture)
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import enumerate as en  # noqa: E402

args = sys.argv[1:]
PKG = "heatpump_optimizer"


def mod(name):
    return importlib.import_module(f"{PKG}.{name}")


def close(a, b, rel=1e-6):
    return math.isclose(a, b, rel_tol=rel, abs_tol=1e-12)


def ref_table(v, ref, label):
    """Every key the table and the reference share must agree; a key the
    reference lacks is reported as unverifiable (not a violation)."""
    bad = []
    for k, x in v.items():
        k2 = getattr(k, "value", k)
        if k2 in ref:
            r = ref[k2]
            if isinstance(r, tuple):
                if not all(close(a, b) for a, b in zip(x, r)):
                    bad.append(f"{label}[{k2!r}]={x} ref {r}")
            elif not close(x, r):
                bad.append(f"{label}[{k2!r}]={x} ref {r}")
    return bad


def strictly_increasing(seq, label):
    s = list(seq)
    return [f"{label} not strictly increasing at {a}->{b}" for a, b in zip(s, s[1:]) if not b > a]


# ---- independent references (SI / NIST definitions, calendar) --------------
L_KG = 1.0  # water: 1 L = 1 kg at the integration's stated convention (WATER_KG_PER_L checked separately)
REF_POWER_KW = {"W": 1e-3, "kW": 1.0, "MW": 1e3, "mW": 1e-6, "GW": 1e6}
REF_ENERGY_KWH = {"Wh": 1e-3, "kWh": 1.0, "MWh": 1e3, "GWh": 1e6}
REF_PRICE_PER_KWH = {"wh": 1e3, "kwh": 1.0, "mwh": 1e-3}  # price per X -> price per kWh
REF_TEMP = {"°C": (0.0, 1.0), "C": (0.0, 1.0), "degC": (0.0, 1.0), "°F": (-32.0, 5 / 9),
            "F": (-32.0, 5 / 9), "degF": (-32.0, 5 / 9), "K": (-273.15, 1.0)}
REF_PRECIP_MM = {"mm": 1.0, "cm": 10.0, "in": 25.4}
REF_WIND_MS = {"m/s": 1.0, "km/h": 1 / 3.6, "mph": 0.44704, "ft/s": 0.3048, "kn": 1852 / 3600,
               "Beaufort": None}
REF_DELTA_PER_K = {"K": 1.0, "°C": 1.0, "C": 1.0, "degC": 1.0, "°F": 1.8, "F": 1.8, "degF": 1.8}
REF_MONTHS = dict(jan=1, feb=2, mar=3, apr=4, may=5, jun=6, jul=7, aug=8, sep=9, oct=10, nov=11, dec=12,
                  maj=5, okt=10)
REF_DAYS = dict(mon=0, tue=1, wed=2, thu=3, fri=4, sat=5, sun=6, mån=0, man=0, tis=1, ons=2, tor=3,
                fre=4, lör=5, lor=5, sön=6, son=6)


def flow_ref():
    c = mod("const")
    w = c.WATER_KG_PER_L
    bad = [] if 0.95 <= w <= 1.0 else [f"WATER_KG_PER_L={w} outside 0.95..1.0"]
    ref = {"L/min": w / 60, "L/s": w, "L/h": w / 3600, "m³/h": w * 1000 / 3600, "m³/s": w * 1000,
           "kg/s": 1.0, "kg/min": 1 / 60, "kg/h": 1 / 3600, "gal/min": w * 3.785411784 / 60}
    return bad + ref_table(c.FLOW_UNIT_TO_KG_S, ref, "FLOW_UNIT_TO_KG_S")


def wind():
    v = mod("coordinator")._WIND_UNIT_TO_MS
    ref = {k: r for k, r in REF_WIND_MS.items() if r is not None}
    bad = ref_table(v, ref, "_WIND_UNIT_TO_MS")
    unknown = [getattr(k, "value", k) for k in v if getattr(k, "value", k) not in REF_WIND_MS]
    return bad + [f"_WIND_UNIT_TO_MS key {u!r} has no reference" for u in unknown]


def era_order():
    p = mod("presets")
    vals = [p._ERA_LOSS_W_PER_M2K[e] for e in p.ERAS]
    bad = [f"_ERA_LOSS_W_PER_M2K not strictly decreasing along ERAS: {list(zip(p.ERAS, vals))}"] \
        if any(b >= a for a, b in zip(vals, vals[1:])) else []
    # derived product: what every questionnaire install computes with (the finding's metric)
    for s in p.STRUCTURES:
        for f in p.FOUNDATIONS:
            for area in (80.0, 140.0, 250.0):
                losses = [p.derive(p.BuildingPreset(structure=s, era=e, foundation=f,
                                                    heated_area_m2=area))["house_heat_loss_coefficient"]
                          for e in p.ERAS]
                if any(b >= a for a, b in zip(losses, losses[1:])):
                    bad.append(f"derive() loss not decreasing along ERAS at {s}/{f}/{area}")
    return bad


def structure_mass():
    p = mod("presets")
    order = [p.STRUCTURE_TIMBER_CRAWLSPACE, p.STRUCTURE_TIMBER_SLAB, p.STRUCTURE_CONCRETE_SLAB, p.STRUCTURE_MASONRY]
    bad = []
    for col in ("fast", "slow"):
        vals = [p._STRUCTURE_MASS[s][col] for s in order]
        if any(b < a for a, b in zip(vals, vals[1:])):
            bad.append(f"_STRUCTURE_MASS[{col}] not non-decreasing light->heavy: {vals}")
    return bad


def foundation():
    p = mod("presets")
    a = p._FOUNDATION_ADJUST
    bad = []
    if a[p.FOUNDATION_NONE] != {"mass": 1.0, "loss": 1.0}:
        bad.append("FOUNDATION_NONE is not the unit reference")
    for k in (p.FOUNDATION_CRAWLSPACE, p.FOUNDATION_BASEMENT):
        if not (1.0 <= a[k]["loss"] <= 1.5):
            bad.append(f"{k} loss factor {a[k]['loss']} outside 1.0..1.5 (an extra ground/air path adds loss)")
        if not (0.5 <= a[k]["mass"] <= 1.5):
            bad.append(f"{k} mass factor {a[k]['mass']} outside 0.5..1.5")
    if not a[p.FOUNDATION_BASEMENT]["mass"] > a[p.FOUNDATION_CRAWLSPACE]["mass"]:
        bad.append("basement mass factor not above crawlspace")
    return bad


def dhw_pattern():
    v = mod("thermal_model").DHW_HOURLY_DRAW_PATTERN
    bad = [] if len(v) == 24 else [f"len {len(v)} != 24"]
    if not close(sum(v) / len(v), 1.0, 1e-9):
        bad.append(f"mean {sum(v) / len(v)} != 1.0")
    if min(v) < 0:
        bad.append("negative draw weight")
    morning, night = max(v[5:10]), max(v[0:5])
    if not morning > night:
        bad.append("morning peak not above night")
    return bad


def wood():
    v = mod("wood_fuel").WOOD_KWH_M3
    bad = []
    for sp, d in v.items():
        if not d["loose"] < d["packed"]:
            bad.append(f"{sp}: loose {d['loose']} not below packed {d['packed']}")
        r = d["loose"] / d["packed"]
        if not 0.5 <= r <= 0.75:
            bad.append(f"{sp}: loose/packed {r:.2f} outside 0.5..0.75 (stacked vs bulk m3)")
    # species energy density per stacked m3: birch > mixed > pine (birch is denser)
    if not v["birch"]["packed"] > v["mixed"]["packed"] > v["pine"]["packed"]:
        bad.append("species order birch > mixed > pine broken")
    for sp, lo, hi in (("birch", 1700, 2100), ("pine", 1300, 1700)):
        if not lo <= v[sp]["packed"] <= hi:
            bad.append(f"{sp} packed {v[sp]['packed']} kWh/m3 outside published {lo}..{hi}")
    return bad


def max_age():
    c = mod("const")
    bad = [f"INPUT_MAX_AGE_MINUTES[{k}]={x} not > 0" for k, x in c.INPUT_MAX_AGE_MINUTES.items() if not x > 0]
    for k, x in c.INPUT_ON_CHANGE_MAX_AGE_MINUTES.items():
        if k in c.INPUT_MAX_AGE_MINUTES and x < c.INPUT_MAX_AGE_MINUTES[k]:
            bad.append(f"on-change age for {k} ({x}) below polling age ({c.INPUT_MAX_AGE_MINUTES[k]})")
    return bad


def plausible_c():
    c = mod("const")
    must = {"room": (5.0, 35.0), "outdoor": (-40.0, 40.0), "water": (5.0, 85.0)}
    bad = []
    for k, (lo, hi) in c.INPUT_PLAUSIBLE_RANGE_C.items():
        if not lo < hi:
            bad.append(f"{k}: {lo} !< {hi}")
        kind = "room" if "indoor" in k or "lower_floor" in k else "outdoor" if "outdoor" in k else "water"
        if "external_heat" in k:
            continue
        mlo, mhi = must[kind]
        if kind == "water" and ("floor_return" in k):
            mhi = 55.0
        if not (lo <= mlo and hi >= mhi):
            bad.append(f"{k}: range ({lo},{hi}) excludes a real {kind} reading in ({mlo},{mhi})")
    return bad


def forecast_range():
    v = mod("coordinator")._FORECAST_FIELD_RANGE
    must = {"temperature": (-40, 40), "wind_speed": (0, 40), "precipitation": (0, 50), "humidity": (0, 100),
            "solar_irradiance": (0, 1100), "native_solar_irradiance": (0, 1100)}
    bad = []
    for k, (lo, hi) in v.items():
        if not lo < hi:
            bad.append(f"{k}: {lo}!<{hi}")
        if k in must and not (lo <= must[k][0] and hi >= must[k][1]):
            bad.append(f"{k}: ({lo},{hi}) excludes real values {must[k]}")
        if k == "humidity" and hi > 100:
            bad.append("humidity above 100 %")
    return bad


def fuse():
    v = mod("const").FUSE_LADDER_A
    # IEC 60269 / Swedish main-fuse ladder for houses
    ref = (16, 20, 25, 35, 50, 63)
    return [] if tuple(v) == ref else [f"FUSE_LADDER_A {tuple(v)} != {ref}"]


CHECK = {
    ("const", "POWER_UNIT_TO_KW"): lambda: ref_table(mod("const").POWER_UNIT_TO_KW, REF_POWER_KW, "POWER_UNIT_TO_KW"),
    ("const", "ENERGY_UNIT_TO_KWH"): lambda: ref_table(mod("const").ENERGY_UNIT_TO_KWH, REF_ENERGY_KWH, "ENERGY_UNIT_TO_KWH"),
    ("const", "PRICE_ENERGY_TO_KWH"): lambda: ref_table(mod("const").PRICE_ENERGY_TO_KWH, REF_PRICE_PER_KWH, "PRICE_ENERGY_TO_KWH"),
    ("const", "TEMPERATURE_UNIT_TO_C"): lambda: ref_table(mod("const").TEMPERATURE_UNIT_TO_C, REF_TEMP, "TEMPERATURE_UNIT_TO_C"),
    ("const", "FLOW_UNIT_TO_KG_S"): flow_ref,
    ("const", "INPUT_MAX_AGE_MINUTES"): max_age,
    ("const", "INPUT_ON_CHANGE_MAX_AGE_MINUTES"): max_age,
    ("const", "INPUT_PLAUSIBLE_RANGE_C"): plausible_c,
    ("const", "FUSE_LADDER_A"): fuse,
    ("coordinator", "_PRECIPITATION_UNIT_TO_MM"): lambda: ref_table(mod("coordinator")._PRECIPITATION_UNIT_TO_MM, REF_PRECIP_MM, "_PRECIPITATION_UNIT_TO_MM"),
    ("coordinator", "_WIND_UNIT_TO_MS"): wind,
    ("coordinator", "_FORECAST_FIELD_RANGE"): forecast_range,
    ("heat_curve", "_DELTA_PER_K"): lambda: ref_table(mod("heat_curve")._DELTA_PER_K, REF_DELTA_PER_K, "_DELTA_PER_K"),
    ("grid_fee", "_MONTHS"): lambda: ref_table(mod("grid_fee")._MONTHS, REF_MONTHS, "_MONTHS"),
    ("grid_fee", "_DAYS"): lambda: ref_table(mod("grid_fee")._DAYS, REF_DAYS, "_DAYS"),
    ("accuracy", "LEAD_BUCKETS"): lambda: strictly_increasing(mod("accuracy").LEAD_BUCKETS, "LEAD_BUCKETS"),
    ("defrost", "TEMP_EDGES"): lambda: strictly_increasing(mod("defrost").TEMP_EDGES, "TEMP_EDGES"),
    ("defrost", "HUMIDITY_EDGES"): lambda: strictly_increasing(mod("defrost").HUMIDITY_EDGES, "HUMIDITY_EDGES")
    + ([] if mod("defrost").HUMIDITY_EDGES[-1] > 100 and mod("defrost").HUMIDITY_EDGES[0] <= 0 else ["HUMIDITY_EDGES do not cover 0..100 %"]),
    ("runs", "BANDS"): lambda: strictly_increasing(mod("runs").BANDS, "BANDS"),
    ("presets", "_ERA_LOSS_W_PER_M2K"): era_order,
    ("presets", "_STRUCTURE_MASS"): structure_mass,
    ("presets", "_FOUNDATION_ADJUST"): foundation,
    ("thermal_model", "DHW_HOURLY_DRAW_PATTERN"): dhw_pattern,
    ("wood_fuel", "WOOD_KWH_M3"): wood,
}

NA = {}

PERTURB = {
    # one-line re-introductions (in memory), one per oracle family
    "_ERA_LOSS_W_PER_M2K": lambda: mod("presets")._ERA_LOSS_W_PER_M2K.__setitem__(mod("presets").ERA_LOW_ENERGY, 0.85),
    "POWER_UNIT_TO_KW": lambda: mod("const").POWER_UNIT_TO_KW.__setitem__("W", 0.01),
    "_WIND_UNIT_TO_MS": lambda: mod("coordinator")._WIND_UNIT_TO_MS.__setitem__(next(iter(mod("coordinator")._WIND_UNIT_TO_MS)), 3.6),
    "TEMP_EDGES": lambda: setattr(mod("defrost"), "TEMP_EDGES", (-30.0, -5.0, 2.0, 0.0, 5.0, 8.0, 40.0)),
    "WOOD_KWH_M3": lambda: mod("wood_fuel").WOOD_KWH_M3["birch"].__setitem__("loose", 1900.0),
}


def option_defaults():
    cf = mod("config_flow")
    bad = []
    for r in cf._OPTION_FIELDS:
        d = r.default
        if isinstance(d, bool) or not isinstance(d, (int, float)):
            continue
        cfg = getattr(r.widget, "config", None)
        if not isinstance(cfg, dict) or "min" not in cfg:
            continue
        lo, hi = cfg.get("min"), cfg.get("max")
        if lo is not None and hi is not None and not lo <= d <= hi:
            bad.append(f"_OPTION_FIELDS[{r.key}] default {d} outside its own selector ({lo}, {hi})")
    return bad


def domains():
    st = mod("store")
    bad = []
    for name, paths in st.DOMAINS.items():
        for path, dom in (paths.items() if isinstance(paths, dict) else ()):
            lo, hi = getattr(dom, "lo", None), getattr(dom, "hi", None)
            if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not lo <= hi:
                bad.append(f"DOMAINS[{name}][{path}] lo {lo} > hi {hi}")
    return bad


def combi():
    v = mod("const").COMBI_TANK_PRESETS
    bad = [f"{k}: effectiveness {p.effectiveness} outside (0,1]" for k, p in v.items() if not 0 < p.effectiveness <= 1]
    bad += [f"{k}: potable volume {p.potable_volume_l} < 0" for k, p in v.items() if p.potable_volume_l < 0]
    # a tank-in-tank's potable store is a tank (>= 100 L); an external plate station stores none
    if not v["tank_in_tank"].potable_volume_l >= 100:
        bad.append("tank_in_tank potable volume below 100 L")
    if v["external_station"].potable_volume_l != 0:
        bad.append("external_station stores potable water")
    return bad


def nameplate():
    c = mod("const")
    cop, mx, mn = c.DEFAULT_HEAT_PUMP_COP_NOMINAL, c.DEFAULT_HEAT_PUMP_MAX_POWER, c.DEFAULT_HEAT_PUMP_MIN_POWER
    bad = [] if 2.0 <= cop <= 6.0 else [f"COP nominal {cop} outside 2..6"]
    return bad + ([] if 0 < mn < mx <= 30 else [f"min {mn} / max {mx} kW not 0 < min < max <= 30"])


# Approximate units of each currency per 1 SEK, mid-2026 (order of magnitude);
# the table promises "whole units worth about one SEK, rounded up", so each
# entry must be >= the rate and within 5x of it.
REF_PER_SEK = dict(ARS=130, CLP=95, COP=400, CZK=2.2, HUF=35, IDR=1650, INR=9, ISK=13, JPY=15, KRW=145,
                   KZT=52, NGN=150, PHP=6, PKR=29, RSD=10.6, RUB=8.5, THB=3.3, TWD=3.2, UAH=4.3, VND=2700)


def units_per_sek():
    v = mod("currency")._UNITS_PER_SEK
    bad = []
    for k, x in v.items():
        r = REF_PER_SEK.get(k)
        if r is None:
            bad.append(f"{k}: no reference rate")
        elif not r <= x <= 5 * r:
            bad.append(f"_UNITS_PER_SEK[{k}]={x} vs ~{r}/SEK (must be >= rate, <= 5x)")
    return bad


CHECK.update({
    ("config_flow", "_OPTION_FIELDS"): option_defaults,
    ("config_flow", "_NAMEPLATE_DEFAULTS"): nameplate,
    ("store", "DOMAINS"): domains,
    ("store", "_ACCURACY"): domains,
    ("const", "COMBI_TANK_PRESETS"): combi,
    ("currency", "_UNITS_PER_SEK"): units_per_sek,
})

NA.update({
    ("config_flow", "_ABSENT_FALLBACKS"): "derived by comprehension from _OPTION_FIELDS defaults (config_flow.py:2490); its numbers are those rows' defaults, held by the _OPTION_FIELDS oracle",
    ("coordinator", "SCORE_REFERENCE"): "grade zero-points of a dimensionless score (coordinator.py:3306), a presentation choice with no physical value to be wrong",
    ("device_prefill", "_TUYA_HEAT_PUMP"): "vendor data-point map; its numbers are scale factors 1.0 per DP whose truth is device firmware, no offline oracle (unverified, not cleared)",
    ("device_prefill", "_SOURCES"): "registry of the prefill tables; its numeric leaves are _TUYA_* scales counted again",
    ("grid_fee", "SWEDEN_CATALOG"): "dated published tariffs (Ellevio, Goteborg Energi 2026); no offline oracle for a tariff figure (unverified, not cleared)",
    ("modbus_prefill", "_TENTHS"): "register addresses (identifiers), not quantities",
    ("modbus_prefill", "_RAW_ADDRESSES"): "register addresses (identifiers), not quantities",
})

PERTURB.update({
    "_OPTION_FIELDS": lambda: setattr(mod("config_flow"), "_OPTION_FIELDS", tuple(
        r._replace(default=r.widget.config["max"] + 1) if r.key == "flow_heat_c" else r for r in mod("config_flow")._OPTION_FIELDS)),
    "_UNITS_PER_SEK": lambda: mod("currency")._UNITS_PER_SEK.__setitem__("JPY", 2),
})


def main():
    if "--perturb" in args:
        PERTURB[args[args.index("--perturb") + 1]]()
    rows = en.seams()
    seen = set()
    instances = guarded = na = undisp = 0
    for x in rows:
        key = (x.get("module", "").split(".")[-1], x["symbol"])
        if key in seen:
            continue
        seen.add(key)
        if x.get("error"):
            print(f"IMPORT-ERROR {x['file']}::{x['symbol']} {x['error']}")
            undisp += 1
            continue
        if key in CHECK:
            v = CHECK[key]()
            if v:
                instances += 1
                print(f"INSTANCE {x['file']}::{x['symbol']}")
                for b in (v if "--all" in args else v[:6]):
                    print(f"    {b}")
            else:
                guarded += 1
                print(f"HOLDS    {x['file']}::{x['symbol']}  (oracle passes; barrier = this oracle)")
        elif key in NA:
            na += 1
            print(f"NA       {x['file']}::{x['symbol']}  {NA[key]}")
        else:
            undisp += 1
            print(f"UNDISPOSITIONED {x['file']}::{x['symbol']}")
    print(f"RESULT seams={len(seen)} count")
    print(f"RESULT instances={instances} count")
    print(f"RESULT holds={guarded} count")
    print(f"RESULT not_applicable={na} count")
    print(f"RESULT undispositioned={undisp} count")
    return 1 if undisp else 0


if __name__ == "__main__":
    sys.exit(main())
