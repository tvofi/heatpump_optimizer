"""Clean fixture: every learned multiplier carries its anchor."""
DOMAINS = {
    "thermal_learning": {
        "house_heat_loss_anchor": 1, "house_heat_loss_scale": 1,
        "lower_floor_loss_anchor": 1, "lower_floor_loss_ratio": 1,
    },
}
