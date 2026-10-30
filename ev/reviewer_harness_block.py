

# ---- REVIEWER harness (fix-review seat, PR #3015): the reviewer's own, not the fixer's ----
_rv_disk: dict = {}
_rv_hold = {"ev": None, "raise": False}


async def _rv_load(store, what):
    if "away" not in what:
        return None
    if _rv_hold["ev"] is not None:
        await _rv_hold["ev"].wait()
    if _rv_hold["raise"]:
        raise RuntimeError("store read failed")
    return dict(_rv_disk) if _rv_disk else None


async def _rv_save(coord, state):
    _rv_disk.update(away_mode._override_payload(state))


async def _rv_noop(*a, **k):
    return None


def _rv_coord(hass, **kw):
    c = Coord(hass, _LsEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                                   "away_temperature": 15.0}), **kw)
    for n in ("_update_current_state", "_fetch_tibber_prices", "_fetch_weather_forecast",
              "_fetch_solar_forecast", "_async_learn_price_shape"):
        setattr(c, n, _rv_noop)
    return c


async def _rv_held(handover_kind):
    """Store read held on an event: the setup refresh and a resolve start inside it."""
    _rv_disk.clear()
    ret = (dt_util.now() + timedelta(hours=10)).isoformat()
    _rv_disk.update(active=True, return_time=ret, migrated_helpers=True)
    ev = _ls_aio.Event()
    _rv_hold["ev"] = ev
    hass = _LsRestoreHass()
    handover = None
    if handover_kind:
        # A handover built under a home state (the pre-switch plan).
        tmp = _rv_coord(_LsHass())
        handover = tmp._build_data_dict()
        handover["last_optimization"] = dt_util.now() - timedelta(minutes=3)
    c = _rv_coord(hass, skip_first_solve=True, reload_handover=handover)
    t1 = _ls_aio.ensure_future(c._async_update_data())
    t2 = _ls_aio.ensure_future(c._resolve_away())
    for _ in range(50):
        await _ls_aio.sleep(0)
    pending = (not t1.done(), not t2.done())
    ev.set()
    first = await _ls_aio.wait_for(t1, 5)
    await _ls_aio.wait_for(t2, 5)
    _rv_hold["ev"] = None
    return pending, first is handover, first.get("away_override_active"), \
        first.get("away_override_return_time") == ret, c._away_state.active


async def _rv_cold(mode):
    """No stored override, or a read that raises: the gate must still open."""
    _rv_disk.clear()
    _rv_disk.update(migrated_helpers=True) if mode == "empty-migrated" else None
    _rv_hold["raise"] = mode == "raise"
    try:
        c = _rv_coord(_LsRestoreHass(), skip_first_solve=True)
        first = await _ls_aio.wait_for(c._async_update_data(), 5)
        await _ls_aio.wait_for(c._resolve_away(), 5)
        return True, bool(first.get("away_override_active")), c._away_state.active
    except _ls_aio.TimeoutError:
        return False, None, None
    finally:
        _rv_hold["raise"] = False


async def _rv_same_override():
    """Away on before and after the reload, same return: the handover is republished."""
    _rv_disk.clear()
    ret = (dt_util.now() + timedelta(hours=10)).isoformat()
    _rv_disk.update(active=True, return_time=ret, migrated_helpers=True)
    hass = _LsRestoreHass()
    old = _rv_coord(hass)
    await hass.restores[0]
    pub = old._build_data_dict()
    pub["last_optimization"] = dt_util.now() - timedelta(minutes=3)
    new = _rv_coord(hass, skip_first_solve=True, reload_handover=pub)
    first = await new._async_update_data()
    return first is pub, first.get("away_override_active")


async def _rv_no_spawn():
    """A coordinator whose restore was never spawned (task None): no wait."""
    c = _rv_coord(_LsHass(), skip_first_solve=True)
    first = await _ls_aio.wait_for(c._async_update_data(), 5)
    await _ls_aio.wait_for(c._resolve_away(), 5)
    return True


_rv_saved = (away_mode.load_mapping, away_mode.persist_override)
away_mode.load_mapping, away_mode.persist_override = _rv_load, _rv_save
try:
    _rv_h_none = _ls_aio.run(_rv_held(False))
    _rv_h_ho = _ls_aio.run(_rv_held(True))
    _rv_c_empty = _ls_aio.run(_rv_cold("empty-migrated"))
    _rv_c_none = _ls_aio.run(_rv_cold("none"))
    _rv_c_raise = _ls_aio.run(_rv_cold("raise"))
    _rv_same = _ls_aio.run(_rv_same_override())
    _rv_ns = _ls_aio.run(_rv_no_spawn())
finally:
    away_mode.load_mapping, away_mode.persist_override = _rv_saved
print("RV-RESULT held/no-handover", _rv_h_none)
print("RV-RESULT held/home-handover", _rv_h_ho)
print("RV-RESULT cold empty", _rv_c_empty, "none", _rv_c_none, "raise", _rv_c_raise)
print("RV-RESULT same-override", _rv_same, "no-spawn", _rv_ns)
R.check("RV held read, no handover: refresh and resolve wait, then carry the override",
        _rv_h_none[0] == (True, True) and _rv_h_none[2] is True and _rv_h_none[3] and _rv_h_none[4] is True,
        str(_rv_h_none))
R.check("RV held read, home handover: waits, drops the handover, carries the override",
        _rv_h_ho[0] == (True, True) and not _rv_h_ho[1] and _rv_h_ho[2] is True and _rv_h_ho[4] is True,
        str(_rv_h_ho))
R.check("RV cold start: gate opens with an empty, a missing (migrating) and a raising read",
        _rv_c_empty[0] and _rv_c_none[0] and _rv_c_raise[0] and _rv_c_empty[1] is False,
        f"{_rv_c_empty} {_rv_c_none} {_rv_c_raise}")
R.check("RV null: same override across the reload republishes the handover",
        _rv_same[0] is True and _rv_same[1] is True, str(_rv_same))
R.check("RV no restore spawned: no wait", _rv_ns is True)
