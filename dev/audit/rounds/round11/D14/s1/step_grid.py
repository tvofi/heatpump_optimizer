"""D14-s1 detector for class N-step-grid: a number selector whose minimum,
maximum or default is not on its own step grid (base = min, as the frontend's
<input type=number>/ha-slider read it), so a legal value is unreachable.

Metric: count of off-grid seams over every NumberSelector the package declares:
(a) each config_flow._OPTION_FIELDS number widget (slider: max and constant
default checked against min + k*step; box with step "any": guarded),
(b) each number selector in services.yaml (HA's default mode is slider: max and
example checked), (c) config_flow._widen_to_fit applied to each slider field
with a stored value 0.3 below its min (the widened min becomes the grid base:
the field's own default is re-checked against it). Key = the delivered selector
config (the value the production seam returns), never the declaration text.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/step_grid.py [--tree DIR] [--perturb-widen|--perturb-min|--perturb-svc]
Expected at 92d38ecb: seams_options=0, seams_widen=28, seams_services=12, seams_total=40,
           box_pinned=0 (exact counts). --tree <export of 26704a4e9f> (the R9 D4-s2-05 pre-fix
           parent of 1938fc88de) re-finds the box-mode instance: box_pinned>0.
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer.config_flow:_OPTION_FIELDS,
           config_flow:_number (the delivered config), config_flow:_widen_to_fit.
Perturbations (in memory, one per flag):
  --perturb-svc   services.yaml number selectors read with step "any"/box (the #1679
                  config-flow fix carried to the service surface) -> seams_services 12 -> 0 (to_zero)
  --perturb-widen config_flow._widen_to_fit snaps the widened min down onto the field's
                  own grid (min - ceil((min-v)/step)*step) -> seams_widen 28 -> 0 (to_zero)
  --perturb-min   the target-temperature slider rebuilt with min 15.2 -> seams_options 0 -> 2 (up)
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math
import sys
import time

argv = sys.argv[1:]
TREE = argv[argv.index("--tree") + 1] if "--tree" in argv else os.getcwd()
PERTURB = "--perturb-widen" in argv
PERTURB_MIN = "--perturb-min" in argv
PERTURB_SVC = "--perturb-svc" in argv
sys.path[:0] = [os.path.join(TREE, "tests", "hastub"), TREE]

import yaml  # noqa: E402
from custom_components.heatpump_optimizer import config_flow as cf  # noqa: E402
from homeassistant.helpers import selector  # noqa: E402

EPS = 1e-9


def on_grid(value, base, step):
    if step in (None, "any") or value is None or base is None:
        return True
    k = (float(value) - float(base)) / float(step)
    return abs(k - round(k)) < 1e-6


def check_cfg(cfg, default):
    """Return a list of off-grid reasons for one delivered selector config."""
    mode = str(cfg.get("mode", "slider"))
    step = cfg.get("step", 1)
    if step == "any":
        return []
    reasons = []
    lo, hi = cfg.get("min"), cfg.get("max")
    if hi is not None and not on_grid(hi, lo, step):
        reasons.append(f"max {hi} off grid {lo}+k*{step} ({mode})")
    if isinstance(default, (int, float)) and not isinstance(default, bool) and not on_grid(default, lo, step):
        reasons.append(f"default {default} off grid {lo}+k*{step} ({mode})")
    return reasons


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    if PERTURB:
        orig = cf._widen_to_fit

        def snapped(number, values):
            out = orig(number, values)
            if out is None:
                return out
            cfg = dict(out.config)
            step = cfg.get("step")
            old = number.config.get("min")
            if step not in (None, "any") and old is not None and cfg.get("min", old) < old:
                n = math.ceil((old - cfg["min"]) / step - 1e-9)
                cfg["min"] = old - n * step
            return selector.NumberSelector(selector.NumberSelectorConfig(**cfg))
        cf._widen_to_fit = snapped

    fields = list(cf._OPTION_FIELDS)
    if PERTURB_MIN:
        fields = [f._replace(widget=cf._number(15.2, 28, 0.5, "°C", slider=True))
                  if f.key == cf.CONF_TARGET_TEMP else f for f in fields]
    numbers = 0; box_pinned = 0; seams_opt = []; seams_widen = []; guarded = 0
    for f in fields:
        w = f.widget
        if not isinstance(w, selector.NumberSelector):
            continue
        numbers += 1
        cfg = dict(w.config)
        default = f.default if isinstance(f.default, (int, float)) else None
        if str(cfg.get("mode")) == "box" and cfg.get("step") != "any":
            box_pinned += 1
            if default is not None and not on_grid(default, cfg.get("min"), cfg.get("step")):
                seams_opt.append(f"options:{f.step}:{f.key}: box default {default} off grid {cfg.get('min')}+k*{cfg.get('step')}")
        if cfg.get("step") == "any":
            guarded += 1
            continue
        for r in check_cfg(cfg, default):
            seams_opt.append(f"options:{f.step}:{f.key}: {r}")
        # (c) a stored value below min widens the field: re-check its own default.
        if cfg.get("min") is not None and default is not None:
            widened = cf._widen_to_fit(w, [float(cfg["min"]) - 0.3])
            if widened is not None:
                wcfg = dict(widened.config)
                for r in check_cfg(wcfg, default):
                    if r.startswith("default"):
                        seams_widen.append(f"widen:{f.step}:{f.key}: stored {cfg['min'] - 0.3:g} -> {r}")
    # (b) services.yaml
    seams_svc = []; svc_numbers = 0
    with open(os.path.join(TREE, "custom_components/heatpump_optimizer/services.yaml"), encoding="utf-8") as fh:
        svcs = yaml.safe_load(fh) or {}
    if PERTURB_SVC:  # the R9 #1679 fix applied to the service surface: step "any"
        for spec in svcs.values():
            for field in ((spec or {}).get("fields") or {}).values():
                num = ((field or {}).get("selector") or {}).get("number")
                if num is not None:
                    num["step"] = "any"; num["mode"] = "box"
    for sname, spec in svcs.items():
        for fname, field in ((spec or {}).get("fields") or {}).items():
            num = ((field or {}).get("selector") or {}).get("number")
            if num is None:
                continue
            svc_numbers += 1
            cfg = {"mode": num.get("mode", "slider"), "step": num.get("step", 1),
                   "min": num.get("min"), "max": num.get("max")}
            dflt = field.get("default", field.get("example"))
            for r in check_cfg(cfg, dflt if isinstance(dflt, (int, float)) else None):
                seams_svc.append(f"services:{sname}.{fname}: {r.replace('default', 'example/default')}")
    for s in seams_opt + seams_widen + seams_svc:
        print("SEAM", s)
    print(f"RESULT option_number_fields={numbers} fields")
    print(f"RESULT option_box_any_guarded={guarded} fields")
    print(f"RESULT box_pinned={box_pinned} fields")
    print(f"RESULT seams_options={len(seams_opt)} seams")
    print(f"RESULT seams_widen={len(seams_widen)} seams")
    print(f"RESULT service_number_fields={svc_numbers} fields")
    print(f"RESULT seams_services={len(seams_svc)} seams")
    print(f"RESULT seams_total={len(seams_opt) + len(seams_widen) + len(seams_svc)} seams")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
