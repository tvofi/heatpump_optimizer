# Reviewer's own mutant table for PR 2572: (id, file, old, new, test)
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
PT = "custom_components/heatpump_optimizer/price_tiles.py"
CO = "custom_components/heatpump_optimizer/coordinator.py"
M = [
 ("MC1", CARD, "if (save > 0 && cost > 0 && cost >= save - 1) {", "if (true) {", "card"),
 ("MC2", CARD, "cost >= save - 1) {", "cost >= save) {", "card"),
 ("MC3", CARD, 'openHaLink(host, "options", null);', "navigateTo(SETTINGS_PATH);", "card"),
 ("MC4", CARD, '  boost: "reasons.boost",\n', "", "card"),
 ("MC5", CARD, "  if (save === 0 && cost >= 0) return null;\n", "", "card"),
 ("MC6", CARD, '<span class="adv-sub">${esc(L(`advisor.step_${ADVISOR_OPT_IN_STEP[id]}`))}</span>', "", "card"),
 ("MB1", PT, "        return {key: round(float(v) + step, 1) for key, v in levels.items() if v is not None}",
             '        return {"target_temp": round(float(config.target_temp) + step, 1)}', "features"),
 ("MB2", PT, 'key = "monthly_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"',
             'key = "monthly_cost_delta"', "features"),
 ("MB3", PT, 'days = _within(list(tile.get("days") or []), today)',
             'days = _within(list(tile.get("days") or []), today)[-1:]', "features"),
 ("MB4", PT, "        if days:\n            out[str(name)]",
             "        if days and len(days) == len(tile[\"days\"]):\n            out[str(name)]", "features"),
 ("MB5", CO, "simulated.baseline_cost - result.baseline_cost, horizon_hours), 2),",
             "simulated.predicted_cost - result.predicted_cost, horizon_hours), 2),", "features"),
 ("MX1", CO, '                    "price_tiles": price_tiles.book(self),\n', "", "features+fb"),
 ("MX2", CO, '        price_tiles.restore(price_tiles.book(self), stored.get("price_tiles"), lambda name, part: admitted(\n            "ledger", {"price_tiles": {name: part}}))\n', "", "features+fb"),
 ("MX3", CO, '    ("comfort_temp_day_weekend", float),\n', "", "features"),
]
