# PROBE-LG
import asyncio as _pa
from homeassistant.helpers.update_coordinator import UpdateFailed as _PUF
def _probe_failed_cycle(direct):
    p = _g5_control()
    _g5_tick(p, _LG_REASON)
    p._legionella.boost_started = dt_util.now() - timedelta(hours=_G5_MAX_H + 0.1)
    p._current_action = {"dhw_reason": _LG_REASON}
    async def _raise(*a, **k):
        raise _PUF("no published price covers now")
    p._fetch_tibber_prices = _raise
    err = None
    try:
        _pa.run(p._update_current_state() if direct else p._async_update_data())
    except BaseException as e:  # noqa
        err = e
    return _g5_writes(p), p._legionella.boost_active, err
_pw, _pact, _perr = _probe_failed_cycle(False)
print("PROBE full-cycle:", _pw, _pact, type(_perr).__name__, str(_perr)[:120])
R.check("PROBE: a cycle whose price fetch fails, past the boost bound, turns the switch OFF", _pw == [_ON, _OFF] and _pact is False, f"writes={_pw} active={_pact} err={type(_perr).__name__}")
_pw, _pact, _perr = _probe_failed_cycle(True)
print("PROBE observe-only:", _pw, _pact, type(_perr).__name__)
