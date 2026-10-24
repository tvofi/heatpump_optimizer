"""D14-s1 N-step-grid detector: every NumberSelector field whose min, max or
static default is off its own step grid.

Metric: count of fields in config_flow._OPTION_FIELDS whose widget is a
NumberSelector with a numeric step (step != "any") and where
(default - min) / step, or (max - min) / step, is not an integer (1e-9 tol).
Keyed on the selector config production builds (config_flow._number), not on a
literal. Box fields carry step "any" (#1679) and are counted as guarded.
Computed defaults (_Computed) are evaluated against an empty current config.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s1/stepgrid_seams.py [--perturb]
--perturb: one-line re-introduction of the R9 D4-s2-05 shape -- _number's box
branch keeps the numeric step (as before #1679); off_grid must rise.
Expected baseline: off_grid=0 (tolerance 0); --perturb: off_grid=8. Baseline 17f1c55fad1b, B7.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, importlib, sys, time


def on_grid(v, base, step):
    q = (float(v) - float(base)) / float(step)
    return abs(q - round(q)) < 1e-9


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0 = time.process_time(); tt0 = time.thread_time()
    sys.path.insert(0, "tests")
    import harness  # noqa: F401  (stub wiring)
    from homeassistant.helpers import selector
    cf = importlib.import_module("heatpump_optimizer.config_flow")
    if a.perturb:
        def _number(minimum, maximum, step, unit=None, *, slider=False):
            cfg = {"min": minimum, "max": maximum, "step": step,
                   "mode": selector.NumberSelectorMode.SLIDER if slider else selector.NumberSelectorMode.BOX}
            if unit is not None:
                cfg["unit_of_measurement"] = unit
            return selector.NumberSelector(selector.NumberSelectorConfig(**cfg))
        cf._number = _number
        src = open(cf.__file__).read()
        ns = dict(vars(cf))
        start = src.index("_OPTION_FIELDS: Final")
        end = src.index("\n)\n", start) + 3
        exec(compile("\n" * src[:start].count("\n") + src[start:end], cf.__file__, "exec"), ns)
        fields = ns["_OPTION_FIELDS"]
    else:
        fields = cf._OPTION_FIELDS
    numeric, guarded, off = 0, 0, []
    for f in fields:
        w = f.widget
        if not isinstance(w, selector.NumberSelector):
            continue
        c = dict(getattr(w, "config", {}) or {})
        step = c.get("step")
        if step in (None, "any"):
            guarded += 1
            continue
        numeric += 1
        lo, hi = c.get("min"), c.get("max")
        d = f.default
        if isinstance(d, cf._Computed):
            try:
                d = d.of({}, None)
            except Exception:  # noqa: BLE001
                d = None
        bad = []
        if lo is not None and hi is not None and not on_grid(hi, lo, step):
            bad.append(f"max {hi}")
        if lo is not None and isinstance(d, (int, float)) and not isinstance(d, bool) and not on_grid(d, lo, step):
            bad.append(f"default {d}")
        if bad:
            off.append(f"{f.step}:{f.key} min={lo} step={step} " + ", ".join(bad))
    print(f"RESULT number_fields={numeric + guarded} fields")
    print(f"RESULT box_any_guarded={guarded} fields")
    print(f"RESULT stepped_fields={numeric} fields")
    print(f"RESULT off_grid={len(off)} fields")
    for o in off:
        print("  off-grid", o)
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
