"""L4 lead (raised by D14-s2) for D12-s3 / D12.M4 -- the grid-fee layer's bounds are SEK numbers.

Metric (one line): blocked_verdicts = seam verdicts (3 seams x 12 currencies) in which a transfer fee of 0.05 EUR/kWh,
  expressed in that currency, is refused or cannot be entered; blocked_currencies = currencies with any such verdict. Seams: (a) grid_fee.spec_problem on the rules text "= <fee>" (config/options flow
  refusal, ERROR_IMPLAUSIBLE); (b) the fixed-fee NumberSelector config_flow._page_schema builds for
  the `grid_fees` page with hass.config.currency set (its max); (c) the coordinator's warn-only
  repair (coordinator._audit_grid_fee raising `grid_fee_magnitude`) for an entity-mode fee sensor
  publishing that value. Count key: the verdicts production returns for the delivered fee value.
ASSUMPTION (stated, not measured): exchange rates per EUR, rounded (EUR 1, SEK 11.2, NOK 11.7,
  DKK 7.46, GBP 0.85, CHF 0.94, PLN 4.3, CZK 25, HUF 395, ISK 145, JPY 160, KRW 1450) and a
  0.05 EUR/kWh fee as an ordinary distribution-fee magnitude; --fee changes the latter.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/leads/l4_fee_bound.py [--perturb] [--fee 0.05]
Perturbation (--perturb): grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH (and the coordinator's imported copy)
  10 -> 1e6 in memory. Expected: blocked_verdicts down (seams (a) and (c) to 0; (b) is the selector max and stays).
Null control: SEK/EUR/NOK/DKK rows (the currencies the constants were sized for): 0 blocked.
Expected: blocked_verdicts=8, blocked_currencies=4 of 12 (HUF,ISK,JPY,KRW), null 0 of 4; --perturb 4.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container. Exact counts.
Instrumented: grid_fee:spec_problem, config_flow:_page_schema (grid_fee_fixed selector),
  coordinator:HeatPumpOptimizerCoordinator._audit_grid_fee.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import grid_fee  # noqa: E402

FX = {"EUR": 1.0, "SEK": 11.2, "NOK": 11.7, "DKK": 7.46, "GBP": 0.85, "CHF": 0.94, "PLN": 4.3,
      "CZK": 25.0, "HUF": 395.0, "ISK": 145.0, "JPY": 160.0, "KRW": 1450.0}
NULL = ("SEK", "EUR", "NOK", "DKK")
FEE_EUR = float(sys.argv[sys.argv.index("--fee") + 1]) if "--fee" in sys.argv else 0.05
PERTURB = "--perturb" in sys.argv
if PERTURB:
    grid_fee.IMPLAUSIBLE_FEE_SEK_PER_KWH = 1e6
    cm.IMPLAUSIBLE_FEE_SEK_PER_KWH = 1e6
ISSUES = []
cm._create_issue = lambda hass, domain, issue_id, **kw: ISSUES.append(issue_id)


def fixed_max(currency):
    h = FakeHass({})
    h.config.currency = currency
    for key, sel in cf._page_schema("grid_fees", {}, h).schema.items():
        if str(key) == "grid_fee_fixed":
            return float(sel.config["max"])
    raise RuntimeError("grid_fee_fixed not on the grid_fees page")


def repair_raised(currency, fee):
    coord = object.__new__(cm.HeatPumpOptimizerCoordinator)
    coord.hass = FakeHass({})
    coord.currency = currency
    coord._grid_fee_issue_value = None
    before = len(ISSUES)
    coord._audit_grid_fee(grid_fee.GridFeeSchedule(mode=grid_fee.MODE_ENTITY), fee)
    return int(any(i == "grid_fee_magnitude" for i in ISSUES[before:]))


def main():
    t0, th0 = time.process_time(), time.thread_time()
    blocked, a_n, b_n, c_n, null_blocked = [], 0, 0, 0, 0
    for cur, fx in FX.items():
        fee = round(FEE_EUR * fx, 2)
        a = int(grid_fee.spec_problem(f"= {fee}") == grid_fee.ERROR_IMPLAUSIBLE)
        b = int(fee > fixed_max(cur))
        c = repair_raised(cur, fee)
        a_n, b_n, c_n = a_n + a, b_n + b, c_n + c
        if a or b or c:
            blocked.append(cur)
            null_blocked += int(cur in NULL)
        print(f"CUR {cur} fee={fee:g} {cur}/kWh rules_refused={a} fixed_over_selector_max={b} "
              f"repair_raised={c}", flush=True)
    print(f"RESULT fee_eur_per_kwh={FEE_EUR:g} assumed")
    print(f"RESULT blocked_verdicts={a_n + b_n + c_n} count")
    print(f"RESULT blocked_currencies={len(blocked)} of {len(FX)} ({','.join(blocked)})")
    print(f"RESULT rules_refused={a_n} count")
    print(f"RESULT fixed_over_selector_max={b_n} count")
    print(f"RESULT repair_raised={c_n} count")
    print(f"RESULT null_blocked={null_blocked} of {len(NULL)}")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
