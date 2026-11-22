

CLS = co.HeatPumpOptimizerCoordinator
MID = co.dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)


def drive(fn, solar, n_steps, covered):
    """_apply_open_meteo with an Open-Meteo stub that publishes irradiance for the first `covered` steps only."""
    c = coord()
    starts = list(co.utc_step_starts(MID, n_steps, co.FORECAST_STEP, 0))
    known = {s: 100.0 + i for i, s in enumerate(starts[:covered])}
    c._open_meteo = SimpleNamespace(available=True, irradiance_for=lambda start, step: known.get(start))
    records = []
    h = logging.Handler(logging.DEBUG)
    h.emit = records.append
    lg = logging.getLogger(co.__name__)
    old = lg.level
    logging.disable(logging.NOTSET)
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    try:
        out = fn(c, list(solar), n_steps, MID, 0)
    except Exception as err:  # the mutant's out-of-range read
        out = type(err).__name__
    finally:
        lg.removeHandler(h)
        lg.setLevel(old)
        logging.disable(logging.CRITICAL)
    n_log = sum(1 for r in records if "Open-Meteo irradiance covered" in r.getMessage())
    return out, n_log


MUT = recompile(CLS, "_apply_open_meteo", "value = solar[i] if i < len(solar) else 0.0",
                "value = solar[i] if i <= len(solar) else 0.0")
b, m = drive(CLS._apply_open_meteo, [5.0, 6.0, 7.0], 6, 2)[0], drive(MUT, [5.0, 6.0, 7.0], 6, 2)[0]
print(f"RESULT short_solar_baseline={b}")
print(f"RESULT short_solar_mutant={m}")
for solar, n, cov in (([], 4, 0), ([5.0, 6.0, 7.0], 6, 3), ([5.0, 6.0, 7.0], 6, 4), ([5.0, 6.0, 7.0], 3, 0)):
    print(f"RESULT inputs solar={solar} n={n} covered={cov}: baseline={drive(CLS._apply_open_meteo, solar, n, cov)[0]} "
          f"mutant={drive(MUT, solar, n, cov)[0]}")
nulls = (([5.0] * 6, 6, 2), ([5.0, 6.0, 7.0], 6, 6))
print(f"RESULT null_delta={sum(int(drive(CLS._apply_open_meteo, *a)[0] != drive(MUT, *a)[0]) for a in nulls)} count")
tail()
