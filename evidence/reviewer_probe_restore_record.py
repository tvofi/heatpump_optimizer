# Reviewer's own probe (not the finder's, not the fixer's): inserted into a copy of
# tests/features.py at the end of the R10-GENERIC-HEAT-CURVE block and run through
# features_block.py. It drives the production paths: async_publish_ecl110_command,
# async_set_mode (the off rule's mode hook) and the entity's read-back state.
_rp = _ghc_coord()
_ghc_pub(_rp, 2.0)                                   # written 2
_rp.hass.states.set(_GHC_ENT, _ghc_state("2", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))
_asyncio.run(_rp.async_set_mode(_ghc_off))           # the off rule writes 0
_rp.hass.states.set(_GHC_ENT, _ghc_state("0", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))
_asyncio.run(_rp.async_set_mode(_ghc_auto))
_ghc_pub(_rp, 2.0)                                   # back on, same plan, < 90 s after the write
print("RESULT probe-A off->on inside the grace: writes=%r (2 re-sent expected after the 0 the restore wrote)" % (_ghc_writes(_rp),))
_rq = _ghc_coord()
_ghc_pub(_rq, 2.0)                                   # written 2, entity lags at 0
_ghc.state_for(_rq.entry).written_at -= _ghc.HELD_GRACE_S + 1
_ghc_pub(_rq, 2.0)                                   # first miss: rewritten once (misses=1)
_rq.hass.states.set(_GHC_ENT, _ghc_state("2", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))  # the rewrite held
_rn = _ghc_coord()                                   # null control: same history, no off/on
_ghc_pub(_rn, 2.0); _ghc.state_for(_rn.entry).written_at -= _ghc.HELD_GRACE_S + 1; _ghc_pub(_rn, 2.0)
_rn.hass.states.set(_GHC_ENT, _ghc_state("2", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))
_ghc.state_for(_rn.entry).written_at -= _ghc.HELD_GRACE_S + 1
_rn_warn = _ghc_logged(lambda: _ghc_pub(_rn, 2.0))
print("RESULT probe-B-null no off/on, the rewrite held: writes=%r warn=%r" % (_ghc_writes(_rn), _rn_warn))
_asyncio.run(_rq.async_set_mode(_ghc_off))           # restore 0
_rq.hass.states.set(_GHC_ENT, _ghc_state("0", unit="K", attributes={"step": 0.5, "min": -20.0, "max": 20.0}))  # the restore held
_asyncio.run(_rq.async_set_mode(_ghc_auto))
_ghc.state_for(_rq.entry).written_at -= _ghc.HELD_GRACE_S + 1
_rq_warn = _ghc_logged(lambda: _ghc_pub(_rq, 2.0))   # next cycle, same target
print("RESULT probe-B off->on after a first miss: writes=%r warn=%r" % (_ghc_writes(_rq), _rq_warn))
