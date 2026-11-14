R.section("REVIEWER PROBE: supply_hold boundaries one tick either side")
def _rv_at(minute, value, since_min, state, mode="auto", boosts=None, **kw):
    held = _sa_pa.ArbiterState()
    inp = _sh_inputs(minute, state=state, **kw)
    base = inp()
    base.hass.states.set("switch.hp", FakeState(state, last_updated=_SA_T0 + timedelta(minutes=since_min)))
    inputs = (lambda: _sa_pa.ArbiterInputs(**{**vars(base), "mode": mode}))
    got = _sh.hold_supply(held, inputs, boosts or _sh_none, value, _SA_T0 + timedelta(minutes=minute))
    return got, held.supply_held
# MIN_RUN: an OFF at minute 12 to a run of age 9, 10, 11 minutes
for _a, _w in ((9, (None, True)), (10, (False, False)), (11, (False, False))):
    _g = _rv_at(12, False, 12 - _a, "on")
    R.check(f"probe MIN_RUN: OFF to a run {_a} min old -> {_w}", _g == _w, f"{_g}")
# MIN_PAUSE: an ON at minute 2 (13 min before boundary, rule three idle) to a pause of age 9, 10, 11
for _a, _w in ((9, (None, True)), (10, (True, False)), (11, (True, False))):
    _g = _rv_at(2, True, 2 - _a, "off")
    R.check(f"probe MIN_PAUSE: ON to a pause {_a} min old -> {_w}", _g == _w, f"{_g}")
# rule three: an ON at minute 4, 5, 6, 14 before an OFF step, pause an hour old
for _m, _w in ((4, (True, False)), (5, (True, False)), (6, (None, True)), (14, (None, True))):
    _g = _sh_start(_m)
    R.check(f"probe rule three: ON at minute {_m} -> {_w}", _g == _w, f"{_g}")
# rule three: a 'both' step with a cold tank is exempt
def _rv_both(cold):
    held = _sa_pa.ArbiterState()
    inp = _sh_inputs(7, dhw=True, cold=cold)
    base = inp()
    base.plan.power_schedule[0] = 1.5
    got = _sh.hold_supply(held, lambda: base, _sh_none, True, _SA_T0 + timedelta(minutes=7))
    return got, held.supply_held, _sa_pa.step_duty(base.plan, _SA_T0 + timedelta(minutes=7))
_g = _rv_both(True); R.check("probe rule three: a both step, tank cold, exempt", _g[:2] == (True, False), f"{_g}")
_g = _rv_both(False); R.check("probe rule three: null: a both step, tank warm, skipped", _g[:2] == (None, True), f"{_g}")
# modes: economy is a plan mode (held); any other mode passes
_g = _rv_at(12, False, 9, "on", mode="economy"); R.check("probe: economy holds an OFF 3 min into a run", _g == (None, True), f"{_g}")
_g = _rv_at(12, False, 9, "on", mode="comfort"); R.check("probe: a non-plan mode passes an OFF 3 min into a run", _g == (False, False), f"{_g}")
# boosts pass
_rv_bs = lambda ch: SimpleNamespace(active=lambda c, _n: c == ch)
from heatpump_optimizer.boost import CHANNEL_DHW as _rv_D, CHANNEL_SPACE as _rv_S
_g = _rv_at(2, True, -1, "off", boosts=_rv_bs(_rv_S)); R.check("probe: a live space boost passes an ON 3 min into a pause", _g == (True, False), f"{_g}")
_g = _rv_at(2, True, -1, "off", boosts=_rv_bs(_rv_D)); R.check("probe: a live DHW boost passes an ON 3 min into a pause", _g == (True, False), f"{_g}")
_g = _rv_at(2, True, -1, "off"); R.check("probe: null: no boost holds that ON", _g == (None, True), f"{_g}")
# step tick retry: released, stale plan, economy
async def _rv_tick(**over):
    held = _sa_pa.ArbiterState(supply=(_SA_T0, False), supply_held=True)
    inp = _sh_inputs(3, state="on")()
    inp = _sa_pa.ArbiterInputs(**{**vars(inp), "plan": None, "action": {"heat_pump_on": False}, **over})
    wrote = []
    async def _write(on):
        wrote.append(on)
    await _sa_pa.supply_tick(held, _sa_pa.SupplyWiring(lambda: inp, _sh_none, _write), _SA_T0 + timedelta(minutes=3))
    return wrote, held.supply_held
for _n, _o, _w in (("entry released: no write, hold dropped", {"entry_released": True}, ([], False)),
                   ("stale plan: no write, hold dropped", {"plan_stale": True}, ([], False)),
                   ("economy, no plan: retries the action's OFF", {"mode": "economy"}, ([False], True))):
    _g = _asyncio.run(_rv_tick(**_o)); R.check(f"probe step tick: {_n}", _g == _w, f"{_g}")
