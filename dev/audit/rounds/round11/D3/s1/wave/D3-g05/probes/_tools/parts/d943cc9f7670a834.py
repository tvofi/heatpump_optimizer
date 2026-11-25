OLD, NEW = "if result and weather_entity in result:", "if result or weather_entity in result:"
MUT = mutant_method("_fetch_weather_forecast", OLD, NEW)
moved = 0
cases = (
    ("other_entity_only_no_held", {"weather.other": {"forecast": [{"temperature": 1.0}]}}, None),
    ("response_none_no_held", None, None),
    ("response_empty_dict_no_held", {}, None),
)
for name, resp, held in cases:
    b, m = fetch(CLS._fetch_weather_forecast, WE, resp, held), fetch(MUT, WE, resp, held)
    moved += int(b[1] != m[1])
    print(f"RESULT {name} baseline(calls,rows,outages,warn)={b} mutant={m}")
nb = fetch(CLS._fetch_weather_forecast, WE, {"weather.other": {}}, held=[{"temperature": 3.0}])
nm = fetch(MUT, WE, {"weather.other": {}}, held=[{"temperature": 3.0}])
print(f"RESULT null_forecast_held baseline={nb} mutant={nm}")
print(f"RESULT moved_held_rows={moved} count")
tail()
