import custom_components.heatpump_optimizer.heat_curve as hc  # noqa: E402

NAME = "async_publish_ecl110_command"
OLD = "np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max)"
NEW = "(displace_value)"


def drive(mutated, value, bias=None):
    """One publish: (displace_int handed to heat_curve.publish, the coordinator's _ecl110_current_displace)."""
    c = make_coord({"curve_learning_enabled": bias is not None})
    if bias is not None:
        c._curve_learner.bias = bias
    sent = []

    async def publish(hass, entry, config, displace_int, legacy_payload, *, mode_off=False):
        sent.append(displace_int)

    with arm(NAME, OLD, NEW, mutated), mock.patch.object(co.heat_curve, "publish", publish):
        asyncio.run(c.async_publish_ecl110_command(value, True))
    return sent[-1], c._ecl110_current_displace


c0 = make_coord()
print(f"RESULT range=[{c0._ecl110_displace_min}, {c0._ecl110_displace_max}] K (the configured clamp, defaults)")
for label, args in CASES.items():
    b, m = drive(False, *args), drive(True, *args)
    print(f"RESULT {label}_baseline=(sent,current){b}")
    print(f"RESULT {label}_mutant=(sent,current){m}")
moved = sum(int(drive(False, *a) != drive(True, *a)) for a in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} in-range inputs {NULLS}")
tail()
