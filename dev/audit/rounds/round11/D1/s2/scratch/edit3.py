p = 'dev/audit/rounds/round11/D1/s2/staleness_unread.py'
s = open(p).read()
s = s.replace('''    "CONF_HEAT_PUMP_SWITCH_ENTITY": lambda co, h, e: getattr(h.states.get(e), "state", None),
}''', '''    "CONF_HEAT_PUMP_SWITCH_ENTITY": lambda co, h, e: getattr(h.states.get(e), "state", None),
    # the pump-duty arbiter's own reader (pump_arbiter._reader), as _setpoint_limits_c reads them
    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": lambda co, h, e: _arb_read(co, h, C.CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY),
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": lambda co, h, e: _arb_read(co, h, C.CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY),
}


def _arb_read(co, h, key):
    from heatpump_optimizer import pump_arbiter as PA
    r = PA._reader(h, dict(co.entry.data)).read(key)
    return r.value if r.ok else None''')
s = s.replace('''    if res["new"] != S.DOMAIN_OF.get(slot, S.TEMP)[1] and val(res["r"]) == hv:''', '''    if res["new"] != (DOMAIN_OVERRIDE.get(slot) or S.DOMAIN_OF.get(slot, S.TEMP))[1] and val(res["r"]) == hv:''')
open(p, 'w').write(s)
