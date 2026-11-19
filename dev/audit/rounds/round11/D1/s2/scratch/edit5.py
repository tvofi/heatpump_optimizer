p = "dev/audit/rounds/round11/D1/s2/hold_restore.py"
s = open(p).read()
s = s.replace('''        if key == "dhw_blocked":
            active = "dhw" in held.blocked''', '''        if key == "dhw_blocked":
            active = "dhw" in held.blocked
        elif key in ("boost_dhw_active", "boost_space_active"):
            # the boost module's own held state (boost.held_for); it publishes through its entities
            active = key.split("_")[1] in held.until''')
open(p, "w").write(s)
