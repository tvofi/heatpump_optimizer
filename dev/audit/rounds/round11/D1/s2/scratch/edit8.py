p = "dev/audit/rounds/round11/D1/s2/store_fuzz.py"
s = open(p).read()
s = s.replace('''def healthy():
    L.dtu.freeze(L.T0)''', '''def _iso(h):
    from datetime import timedelta
    return (L.T0 + timedelta(hours=h)).isoformat()


#: finite_boundary's seeds leave these three empty (no boost, no plan, away
#: off), so a fuzz over them corrupts nothing (round-10 C1). Populated with a
#: running hold each, in the shape their savers write (boost._store_payload,
#: ManualOverride.to_dict, away._override_payload).
POPULATED = {
    "boost": {"dhw": {"until": _iso(2)}, "block_space": {"until": _iso(1)},
              "space_settle": {"until": _iso(3), "boosted_h": 1.5}},
    "manual_plan": {"space_slots": [{"start": _iso(1), "end": _iso(3)}, {"start": _iso(5), "end": _iso(6)}],
                    "dhw_slots": [], "expires_at": _iso(12), "created_at": _iso(-1)},
    "away": {"active": True, "return_time": _iso(24), "migrated_helpers": True},
}


def healthy():
    L.dtu.freeze(L.T0)''')
s = s.replace('''        out[name] = (key, payload, vers.get(key, 1))
    return out''', '''        out[name] = (key, POPULATED.get(name, payload), vers.get(key, 1))
    return out''')
open(p, "w").write(s)
