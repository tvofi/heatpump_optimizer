

def drive(frac, step):
    """Restore a store whose house_heat_loss_anchor was fitted against a nameplate frac away from today's."""
    c = coord()
    c._house_heat_loss_scale, c._house_heat_loss_samples = 1.2, 200
    stored = dict(c._heat_loss_anchors())
    stored["house_heat_loss_anchor"] = float(stored["house_heat_loss_anchor"]) * (1.0 + frac)
    with mock.patch.object(co, "HOUSE_LOSS_MAX_STEP", step):
        changed = c._reanchor_house_heat_loss_scale(stored)
    return bool(changed), round(float(c._house_heat_loss_scale), 6)


b, m = drive(0.07, 0.05), drive(0.07, 0.1)
print(f"RESULT reanchor_7pct_baseline={b}")
print(f"RESULT reanchor_7pct_mutant={m}")
for f in (0.049, 0.051, 0.099, 0.101, -0.07):
    print(f"RESULT inputs frac={f}: baseline={drive(f, 0.05)} mutant={drive(f, 0.1)}")
print(f"RESULT null_delta={sum(int(drive(f, 0.05) != drive(f, 0.1)) for f in (0.03, 0.12))} count")
tail()
