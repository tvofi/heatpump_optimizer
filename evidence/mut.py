import sys, pathlib
CARD="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
PT="custom_components/heatpump_optimizer/price_tiles.py"
CO="custom_components/heatpump_optimizer/coordinator.py"
M = {
 "MC1": (CARD, "if (save > 0 && cost > 0 && cost >= save - 1) {", "if (true) {"),
 "MC2": (CARD, "cost >= save - 1) {", "cost >= save) {"),
 "MC3": (CARD, '} else if (act === "open_options") {\n        openHaLink(host, "options", null);', '} else if (act === "open_options") {\n        navigateTo(SETTINGS_PATH);'),
 "MC4": (CARD, '  boost: "reasons.boost",\n', ''),
 "MB1": (PT, 'return {key: round(float(v) + step, 1) for key, v in levels.items() if v is not None}', 'return {"target_temp": round(float(levels["target_temp"]) + step, 1)}'),
 "MB2": (PT, 'key = "monthly_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"', 'key = "monthly_cost_delta"'),
 "MB3": (PT, 'days = _within(list(tile.get("days") or []), today)\n', 'days = _within(list(tile.get("days") or []), today)[-1:]\n'),
 "MB4": (PT, 'days = [d for d in tile["days"] if isinstance(d, dict) and admit(name, {"days": [d]})]', 'days = list(tile["days"]) if all(isinstance(d, dict) for d in tile["days"]) and admit(name, {"days": tile["days"]}) else []'),
 "MB5": (CO, 'simulated.baseline_cost - result.baseline_cost, horizon_hours), 2),', 'simulated.predicted_cost - result.predicted_cost, horizon_hours), 2),'),
 # reviewer's own class attack
 "MX1": (CO, '                    "price_tiles": price_tiles.book(self),\n', ''),
 "MX2": (CO, 'price_tiles.restore(price_tiles.book(self), stored.get("price_tiles"), lambda name, part: admitted(\n            "ledger", {"price_tiles": {name: part}}))\n', ''),
 "MX3": (CO, '    ("comfort_temp_day_weekend", float),\n    ("comfort_temp_night_weekend", float),\n    ("holiday_comfort_day", float),\n    ("holiday_comfort_night", float),\n', ''),
 "MX4": (PT, 'mean = sum(d["sum"] / d["count"] for d in days) / len(days)', 'mean = sum(d["sum"] for d in days) / sum(d["count"] for d in days)'),
 "MX5": (PT, 'kept = [d for d in _within(days, today) if d["day"] != key]', 'kept = [d for d in days if d["day"] != key]'),
 "MX6": (CARD, '  if (save === 0 && cost >= 0) return null;\n', ''),
}
name, root = sys.argv[1], pathlib.Path(sys.argv[2])
f, old, new = M[name]
p = root / f; s = p.read_text()
assert s.count(old) == 1, (name, s.count(old))
p.write_text(s.replace(old, new)); print("applied", name, f)
