

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


MUT = recompile(CLS, "_apply_open_meteo", "if missing:", "if False:")
args = ([5.0] * 6, 6, 2)
(bs, bl), (ms, ml) = drive(CLS._apply_open_meteo, *args), drive(MUT, *args)
print(f"RESULT partial_cover_log_baseline={bl} count")
print(f"RESULT partial_cover_log_mutant={ml} count")
print(f"RESULT series_delta={int(bs != ms)} count")
for a in (([], 4, 0), ([5.0] * 6, 6, 5)):
    print(f"RESULT inputs {a}: baseline={drive(CLS._apply_open_meteo, *a)} mutant={drive(MUT, *a)}")
nb, nm = drive(CLS._apply_open_meteo, [5.0] * 6, 6, 6), drive(MUT, [5.0] * 6, 6, 6)
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
