"""Reviewer-built probe (not the finder's, not the fixer's): the degree tiles as
production samples them -- ONE tile per scheduled solve, cursor rotating over the
three specs (coordinator._maybe_refresh_price_tile), at the default 30-minute
cadence -- folded with price_tiles.record and published with price_tiles.published,
then judged by the card's degreeRow predicate (round; save>0, cost>0, cost>=save-1).
The solver is stubbed: baseline_cost (the thermostat's) does not depend on it.
Weather/price days are r10_advisor_degree.py's `days` sequence, concatenated."""
import copy, sys, types
from datetime import timedelta
import numpy as np
sys.path.insert(0, "dev/audit/harnesses")
import r10_advisor_degree as H
from heatpump_optimizer import optimizer as O, price_tiles
from profiles import solve_inputs

def _stub(objective, starts, bounds, maxiter=200, **kw):
    x = np.asarray(starts[0], float)
    return types.SimpleNamespace(x=x, fun=float(objective(x)), success=True, nit=0, status=0, message="stub")
O._multi_start_minimize = _stub

CADENCE = int(sys.argv[1]) if len(sys.argv) > 1 else 30   # minutes
DAYS = int(sys.argv[2]) if len(sys.argv) > 2 else 40
BOTH = len(sys.argv) > 3 and sys.argv[3] == "both"  # control: both tiles priced at every solve
opt, model = H._optimizer()
hours = opt.config.horizon_hours
specs = price_tiles.specs(opt.config, 6.0)
shadows = {n: H._shadow(opt, model, ov) for n, ov in specs[:2]}
pr = []; wx = [[], [], [], []]
for k in range(DAYS + 2):
    p, w, _ = H._day(k); pr.append(p)
    for i in range(4): wx[i].append(w[i])
pr = np.concatenate(pr); wx = [np.concatenate(a) for a in wx]
step = CADENCE // 15
book, cursor, rows = {}, 0, []
def card(down, up):
    save, cost = -round(down), round(up)
    if save > 0 and cost > 0 and cost >= save - 1: return "shown"
    if save == 0 and cost >= 0: return "no-row"
    return "NOT-SHOWN"
for j in range(0, DAYS * 96, step):
    t = H.START + timedelta(hours=j * 0.25)
    sl = slice(j, j + 96)
    room, slab = H.STARTS[(j // 96) % 3]
    st = H._state(room, slab, float(wx[0][j]))
    kw = dict(prices=pr[sl], outdoor_temps=wx[0][sl], wind_speeds=wx[1][sl], precipitation=wx[2][sl],
              solar_radiation=wx[3][sl], start_time=t)
    name, ov = specs[cursor % 3]; cursor += 1
    for name, ov in (specs[:2] if BOTH else [(name, ov)]):
      if name != "power_cap_75":
        live = opt.optimize(inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
        sim = shadows[name].optimize(inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
        ans = {"monthly_held_cost_delta": price_tiles.per_month(sim.baseline_cost - live.baseline_cost, hours)}
        price_tiles.record(book, name, ov, ans, t)
    nxt = t + timedelta(minutes=CADENCE)
    if nxt.date() != t.date():   # end of a local day: what the card shows tonight
        v = price_tiles.published(book, t.date())
        if "target_minus_1" in v and "target_plus_1" in v:
            d, u = v["target_minus_1"]["monthly_cost_delta"], v["target_plus_1"]["monthly_cost_delta"]
            rows.append((t.date(), d, u, card(d, u)))
            print(f"RESULT rotation day {len(rows)-1:2d} {t.date()} published {d:+7.2f} {u:+7.2f} "
                  f"asym {u + d:+5.2f} card {rows[-1][3]}", flush=True)
bad = [r for r in rows if r[3] != "shown"]
late = rows[29:]
print(f"RESULT {'both-every-solve' if BOTH else 'rotation'} cadence {CADENCE} min: card NOT shown on {len(bad)}/{len(rows)} days "
      f"({sum(1 for r in late if r[3] != 'shown')}/{len(late)} from day 30); "
      f"asym (up+down) range {min(r[1]+r[2] for r in rows):+.2f}..{max(r[1]+r[2] for r in rows):+.2f}")
