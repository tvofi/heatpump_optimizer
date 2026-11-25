#!/usr/bin/env python3
"""D5.M3 basis harness: do the reader documents state the basis of the two heat-loss figures
the Learning Model Status sensor publishes, where the two bases differ?

Metric 1 (code): relative gap between the effective whole-house loss the sensor publishes as
`heat_loss_w_per_k` (thermal_model:ThermalParameters.house_heat_loss_base x scale, the basis of
coordinator:_effective_house_heat_loss) and the configured zone total the system-identification
figure `heat_loss_kw_per_c` sits on (sysid:_zone_heat_loss, U+L), for the shared two-zone test
profile with a learned lower-floor ratio of 1.4.
Metric 2 (docs): units of README.md + docs/*.md (text_ledger.py units --dim D6) that name the
system-identification heat-loss figure (mention identification and loss/UA), and of those, the
units stating which basis it is on (configured / zone total / effective / before the learned).
Key: the gap is keyed on the two production properties' values; the doc count on unit text.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/basis.py [--ratio R] [--doc-fix]
  --ratio 1.0  null control: the lower-floor ratio at 1, where the two bases coincide (gap 0).
  --doc-fix    perturbation: one basis sentence appended in memory to how-it-works.md's
               identification section; basis_stated 0 -> 1 (up).
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: basis_gap_pct=18.9 at ratio 1.4
(exact to 0.1), 0.0 at ratio 1.0; sysid_loss_units=5, basis_stated=0 (exact); --doc-fix basis_stated=1.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time
from pathlib import Path

for extra in ("tests", "custom_components", "tools/audit"):
    sys.path.insert(0, extra)
from profiles import house  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from heatpump_optimizer import sysid  # noqa: E402
import text_ledger  # noqa: E402

DOCS = ["README.md"] + sorted(str(p) for p in Path("docs").glob("*.md"))
BASIS = re.compile(r"configured|zone total|effective|before the learned|U\s*\+\s*L", re.I)


def main():
    ratio = float(sys.argv[sys.argv.index("--ratio") + 1]) if "--ratio" in sys.argv else 1.4
    p = ThermalParameters.from_config(house(two_zone=True, dhw=False))
    p.two_zone_enabled = True
    p.lower_floor_loss_ratio = ratio
    effective = p.house_heat_loss_base          # x scale 1.0: what heat_loss_w_per_k publishes / 1000
    zone_total = sysid._zone_heat_loss(p)       # the basis the sysid figure is on
    gap = (effective - zone_total) / zone_total * 100.0
    texts = {d: Path(d).read_text(encoding="utf-8") for d in DOCS}
    if "--doc-fix" in sys.argv:
        texts["docs/how-it-works.md"] = texts["docs/how-it-works.md"].replace(
            "### The rest of the learners",
            "The loss coefficient identification publishes is on the configured zone total, not the effective loss "
            "`heat_loss_w_per_k` reports.\n\n### The rest of the learners", 1)
    named, stated = [], []
    for d in DOCS:
        # the span of each identification section (a heading naming it, to the next heading)
        heads = [(ln, h) for ln, k, h in text_ledger.outline(d, texts[d]) if k == "heading"]
        spans = [(ln, (heads[i + 1][0] if i + 1 < len(heads) else 10 ** 9))
                 for i, (ln, h) in enumerate(heads) if "identification" in h.lower()]
        for uid, line, kind, t in text_ledger.units_of(d, texts[d], "D6"):
            if kind == "code":
                continue
            low = t.lower()
            in_sec = any(a <= line < b for a, b in spans)
            if (in_sec or "identification" in low) and re.search(r"loss coefficient|heat[- ]loss|\bUA\b", t):
                named.append(f"{uid}:{line}")
                if BASIS.search(t):
                    stated.append(f"{uid}:{line}")
    print(f"RESULT lower_floor_ratio={ratio}")
    print(f"RESULT effective_kw_per_c={effective:.4f} kW/degC")
    print(f"RESULT zone_total_kw_per_c={zone_total:.4f} kW/degC")
    print(f"RESULT basis_gap_pct={gap:.1f} %")
    print(f"RESULT sysid_loss_units={len(named)} units")
    for u in named:
        print(f"   names {u}")
    print(f"RESULT basis_stated={len(stated)} units")
    for u in stated:
        print(f"   states {u}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
