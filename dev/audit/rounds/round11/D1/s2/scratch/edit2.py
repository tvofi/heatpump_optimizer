p = 'dev/audit/rounds/round11/D1/s2/staleness_unread.py'
s = open(p).read()
s = s.replace('''    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp"},
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp"},
}''', '''    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp",
                                              "pump_duty_mode": "control"},
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": {"space_setpoint_unit": "flow", "space_setpoint_entity": "number.sp",
                                             "pump_duty_mode": "control"},
    "CONF_PRICE_ENTITY": {"price_source": "entity"},
}
#: A healthy state that exercises the consumer (a calendar that is on).
DOMAIN_OVERRIDE = {
    "CONF_HOLIDAY_CALENDAR_ENTITY": ("calendar", "on", {"start_time": "2026-01-20 00:00:00",
                                                        "end_time": "2026-01-23 00:00:00", "message": "holiday"}),
}''')
s = s.replace('''    dom, st, attrs = S.DOMAIN_OF.get(slot, S.TEMP)
    eid = f"{dom}.probe_{key}"
    t0 = L.T0''', '''    dom, st, attrs = DOMAIN_OVERRIDE.get(slot) or S.DOMAIN_OF.get(slot, S.TEMP)
    eid = f"{dom}.probe_{key}"
    t0 = L.T0''')
s = s.replace('''DECLARED_LIMIT = {"CONF_PV_PRODUCTION_ENTITY": C.INPUT_MAX_AGE_MINUTES[C.CONF_PV_PRODUCTION_ENTITY],
                  "CONF_DHW_INLET_ENTITY": getattr(CM, "DHW_INLET_MAX_AGE_MINUTES", None)}''', '''DECLARED_LIMIT = {"CONF_PV_PRODUCTION_ENTITY": C.INPUT_MAX_AGE_MINUTES[C.CONF_PV_PRODUCTION_ENTITY],
                  "CONF_DHW_INLET_ENTITY": getattr(CM, "DHW_INLET_MAX_AGE_MINUTES", None)}
#: Minutes since the last report in phase (s): a slot whose limit is longer is not past it there.
S_AGE = 420''')
s = s.replace('''    if DECLARED_LIMIT.get(slot) is not None or res["s"]["reader"] is not None:
        for t in ("f", "s"):''', '''    lim = DECLARED_LIMIT.get(slot)
    if (lim is not None and lim < S_AGE) or (res["s"]["reader"] is not None and slot not in DECLARED_LIMIT):
        for t in ("f", "s"):''')
open(p, 'w').write(s)
