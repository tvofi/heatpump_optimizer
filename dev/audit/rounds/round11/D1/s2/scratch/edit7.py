p = "dev/audit/rounds/round11/D1/s2/config_fuzz.py"
s = open(p).read()
s = s.replace('''Expected: RESULT lines per version; healthy control vN -> migrate ok, cycles ok.''', '''Expected: RESULT lines per version; healthy control vN -> migrate ok, cycles ok.
--fix (perturbation, in memory): ``async_migrate_entry`` additionally drops every
option whose JSON type is not the type the config flow writes for it (the
healthy record's), so its reader falls back to the default -> build_fail and
permanent_cycle_fail fall to 0.''')
s = s.replace('''def run(version, data):
    L.reset_globals()
    ps = L.patches() + L.price_patches()''', '''FIX = {"on": False}


def _kind(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "num"
    return type(v).__name__


def fixed_migrate(real):
    async def migrate(hass, entry):
        ok = await real(hass, entry)
        for k in list(entry.data):
            if k in HEALTHY and _kind(entry.data[k]) != _kind(HEALTHY[k]):
                del entry.data[k]
        return ok
    return migrate


def run(version, data):
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    if FIX["on"]:
        ps.append(L.mock.patch.object(pkg, "async_migrate_entry", fixed_migrate(pkg.async_migrate_entry)))''')
s = s.replace('''    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()''', '''    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    FIX["on"] = a.fix''')
open(p, "w").write(s)
