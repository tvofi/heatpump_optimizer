"""Reviewer: charge at the span's first and last step, with an unobserved read elsewhere."""
import sys
sys.argv = ["x"]
exec(open(__file__.replace("edge_attack.py", "unobs_attack.py")).read().split("cases = [")[0])
for ca in (1, 11):
    for unobs in ((), (6,), (ca - 1,)):
        ev = run(set(unobs), True, charge_at=ca)
        if ev is None or ev.energy is None:
            print(f"RESULT charge@{ca} unobs={unobs}: no span closed"); continue
        sh = he.span_heat(ev, 3.0)
        print(f"RESULT charge@{ca} unobs={unobs}: heat_kw={sh.heat_kw:.3f} space_kw={sh.space_kw} dhw_kwh={ev.energy.dhw_kwh} "
              f"dhw_seen={getattr(ev.energy,'dhw_seen','n/a')} observed={ev.attribution.observed}")
