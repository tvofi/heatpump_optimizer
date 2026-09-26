
# ---------------------------------------------------------------------------
# P6 arm S (round-9 class barrier): a solve seed is a producer's, not the
# constructor's. D12-s1-01 is this shape: with no tank probe every solve
# started from ThermalState's 55 degC and nothing ever advanced it; #368 had
# named it in the comment above _D801_IN_SCOPE and scoped it out. The rule,
# over the install the flow produces with the clock moving one plan step per
# cycle: a numeric ThermalState field whose seed equals its constructor
# default at EVERY solve had no producer on this install. Each such field is
# either fixed (a producer advances it) or declared below with its reason;
# a declaration that stops matching is refused, so the list only shrinks.
import dataclasses as _p6_dc

P6_SEED_DEFAULTS_DECLARED = {}
_p6_seed_log = []


def _p6_seed_run(cycles=2, *, stand_in=None):
    hass, entry, coord = _d801_coordinator(_FLOW_CONFIG)
    snap = coord._solve_snapshot

    def recording_snapshot():
        state, optimizer = snap()
        _p6_seed_log.append(
            {f.name: getattr(state, f.name) for f in _p6_dc.fields(state)}
        )
        return state, optimizer

    coord._solve_snapshot = recording_snapshot

    async def run():
        for cycle in range(cycles):
            dt_util.freeze(_D801_START + timedelta(minutes=15 * cycle))
            await coord._update_current_state()
            if stand_in is not None:
                stand_in(coord, cycle)
            await coord.async_run_optimization()

    try:
        asyncio.run(run())
    finally:
        dt_util.freeze(None)
    return coord


def _p6_seed_seams(log):
    defaults = ThermalState()
    seams = []
    for f in _p6_dc.fields(ThermalState):
        d = getattr(defaults, f.name)
        if isinstance(d, bool) or not isinstance(d, (int, float)):
            continue  # None is an honest "unknown"; flags are not seeds
        if len(log) >= 2 and all(seed[f.name] == d for seed in log):
            seams.append(f.name)
    return seams
