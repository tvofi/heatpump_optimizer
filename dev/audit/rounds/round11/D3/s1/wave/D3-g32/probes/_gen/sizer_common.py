from custom_components.heatpump_optimizer import sysid

SID = sysid.SystemIdentification
HOUSES = {  # (ua kW/K, capacity kWh/K, gains kW, slab_mass, slab_transfer); the first is tests/features.py's D2-s4-02 cell
    "features_heavy": sysid.HousePlant(ua=0.20, capacity=8.0, gains=0.3),
    "light": sysid.HousePlant(ua=0.15, capacity=4.0, gains=0.2),
    "leaky": sysid.HousePlant(ua=0.35, capacity=8.0, gains=0.5),
    "slab": sysid.HousePlant(ua=0.20, capacity=6.0, gains=0.3, slab_mass=8.0, slab_transfer=0.5),
}
ARGS = [  # (max_power_kw, cop, baseline, outdoor)
    (6.0, 3.0, 21.0, 2.0), (3.0, 2.5, 20.0, -5.0), (8.0, 4.0, 21.5, 8.0), (1.5, 3.0, 21.0, 2.0),
    (4.0, 1.0, 20.0, 0.0), (2.0, 2.0, 22.0, 10.0),
]


def call(fn, max_power_kw, cop, baseline, outdoor, house):
    s = SID(sysid.SysIdConfig(enabled=True))
    try:
        r = fn(s, max_power_kw, cop, baseline, outdoor, house)
        return None if r is None else round(float(r), 9)
    except Exception as err:  # noqa: BLE001
        return f"raised {type(err).__name__}"


def scan(mut, args=ARGS, houses=HOUSES, show=6):
    moved, n, shown = 0, 0, 0
    for hname, house in houses.items():
        for a in args:
            b, m = call(SID._size_step_power, *a, house), call(mut, *a, house)
            n += 1
            if b != m:
                moved += 1
                if shown < show:
                    shown += 1
                    print(f"RESULT moved_{hname}_{a}: baseline={b} mutant={m}")
    return moved, n
