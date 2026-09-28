"""H2: _record_quiet_comfort_period runs inside the away/economy envelope of
async_run_optimization, so its band = comfort_temp_day - min_temp is read off
the EFFECTIVE (set-back / widened) _opt_config, not the configured one.

Real coordinator, comfort learning on, real solve; ComfortLearner.
record_quiet_period is wrapped (not replaced) to capture its arguments and
the learner's evidence before/after. Each arm runs ONE async_run_optimization
from the same starting state; only the mode/away flag differs.
Arms: null/auto, probe/economy, probe/away(override, no return).
(open-window relax is not reachable here: _learning_frozen returns
"ventilation" while the latch is tripped, so the quiet period is skipped.)
Second table: the same arms over 12 consecutive cycles -> learned weight.
"""
import asyncio

import rig
from heatpump_optimizer.comfort_learning import ComfortLearner

CAP = []
_real = ComfortLearner.record_quiet_period


def _spy(self, now, span, band, days=1.0):
    ev0 = self.evidence
    _real(self, now, span, band, days=days)
    CAP.append({"span": round(span, 3), "band": round(band, 3), "flat_threshold": round(band * 0.25, 3), "counted": self.evidence != ev0})


ComfortLearner.record_quiet_period = _spy


async def arm(name, *, mode="auto", away=False, cycles=1):
    c = rig.make(f"h2_{name}", extra={"comfort_learning_enabled": True})
    if mode != "auto":
        await c.async_set_mode(mode, refresh=False)
    c._away_state.override_active = away
    CAP.clear()
    w0 = c._comfort_learner.learned_weight
    for _ in range(cycles):
        r = await c.async_run_optimization()
    return {
        "arm": name,
        "reason": r,
        "configured_band": c._opt_config.comfort_temp_day - c._opt_config.min_temp,
        "captured": CAP[0] if CAP else None,
        "n_calls": len(CAP),
        "n_counted": sum(1 for x in CAP if x["counted"]),
        "weight": (round(w0, 4), round(c._comfort_learner.learned_weight, 4)),
    }


async def main():
    print("one cycle each:")
    for a in ("null/auto", "probe/economy", "probe/away"):
        r = await arm(a, mode="economy" if "economy" in a else "auto", away="away" in a)
        print(f"  {r['arm']:15s} configured_band={r['configured_band']:.2f}  band_passed_to_learner={r['captured']}")
    print("\n12 consecutive cycles each (same inputs every cycle):")
    for a in ("null/auto", "probe/economy", "probe/away"):
        r = await arm(a, mode="economy" if "economy" in a else "auto", away="away" in a, cycles=12)
        print(f"  {r['arm']:15s} calls={r['n_calls']} counted_as_quiet={r['n_counted']} learned_weight(before,after)={r['weight']}")
    print("\nsynthetic span through the REAL ComfortLearner.record_quiet_period (fresh learner each),")
    print("band = configured 2.0 vs the effective bands captured above (economy 3.5, away 0.5):")
    from datetime import datetime, timezone
    for span in (0.3, 0.7):
        cells = []
        for label, band in (("configured", 2.0), ("economy", 3.5), ("away", 0.5)):
            L = ComfortLearner()
            ev0 = L.evidence
            _real(L, datetime(2026, 1, 15, tzinfo=timezone.utc), span, band, days=30 / 1440)
            cells.append(f"{label}(band {band}): counted={L.evidence != ev0}")
        print(f"  span={span}: " + "; ".join(cells))


if __name__ == "__main__":
    asyncio.run(main())
