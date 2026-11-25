OLD, NEW = "if not weather_entity:", "if False:"
MUT = mutant_method("_fetch_weather_forecast", OLD, NEW)
moved = 0
for name, ent, resp in (("unset_empty", "", ...), ("unset_none", None, ...), ("unset_with_service", "", {})):
    b, m = fetch(CLS._fetch_weather_forecast, ent, resp), fetch(MUT, ent, resp)
    moved += int(b != m)
    print(f"RESULT {name} baseline(calls,rows,outages,warn)={b} mutant={m}")
nb = fetch(CLS._fetch_weather_forecast, WE, {WE: {"forecast": []}})
nm = fetch(MUT, WE, {WE: {"forecast": []}})
print(f"RESULT null_configured baseline={nb} mutant={nm}")
print(f"RESULT moved_cases={moved} count")
tail()
