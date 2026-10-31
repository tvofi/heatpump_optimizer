import subprocess, sys
TM = "custom_components/heatpump_optimizer/thermal_model.py"
OP = "custom_components/heatpump_optimizer/optimizer.py"
MUTANTS = {
    "M1 terminal credit two-zone only": (OP, [("        if params.buffer_is_store:\n            # Only with a valve",
                                               "        if params.buffer_is_store and params.two_zone_enabled:\n            # Only with a valve")]),
    "M2 scalar valve branch off": (TM, [("        new_buf = state.buffer_tank_temperature\n        if throttled:",
                                        "        new_buf = state.buffer_tank_temperature\n        if False:")]),
    "M3 batch valve branch off": (TM, [("                    if throttled:\n                        target = (",
                                       "                    if False:\n                        target = (")]),
    "M4 scalar COP ignores the tank": (TM, [("                flow_temp=state.buffer_tank_temperature if throttled else None)",
                                            "                flow_temp=None)")]),
    "M5 batch COP ignores the tank": (TM, [("                    cop = self._batch_cop(out_i, hum_i, T_buf, throttled)\n                    thermal_power = cop * power_i + ext",
                                           "                    cop = self._batch_cop(out_i, hum_i, T_buf, False)\n                    thermal_power = cop * power_i + ext")]),
    "M6 energy bound dropped": (TM, [("    q_slab = _tank_bounded_draw(\n        drawn, thermal_power, q_buf_loss, c_buf, T_buf, T_slab, dt_hours\n    )",
                                     "    q_slab = drawn")]),
    "M7 stability count blind to the tank": (TM, [("                valve_row = ua_valve / c_buf\n",
                                                    "                valve_row = 0.0\n")]),
    "M8 no buffer_max_temp clamp": (TM, [("    return q_slab, np.minimum(dT_buf, dT_cap), refused", "    return q_slab, dT_buf, 0.0 * refused")]),
    # M9: the joint twin mutant -- both single-zone COP rows at once, which the
    # batch/scalar parity cannot see; only the value check kills it.
    "M9 both single-zone COP rows ignore the tank": (TM, [
        ("                flow_temp=state.buffer_tank_temperature if throttled else None)",
         "                flow_temp=None)"),
        ("                    cop = self._batch_cop(out_i, hum_i, T_buf, throttled)\n                    thermal_power = cop * power_i + ext",
         "                    cop = self._batch_cop(out_i, hum_i, T_buf, False)\n                    thermal_power = cop * power_i + ext"),
    ]),
    # M10/M11: the batch's own two-zone rows, which the scalar step cannot see
    # where the batch keeps its own copy. Since the batch now calls the shared
    # `_tank_bounded_draw`, M10 breaks the one expression every caller uses;
    # M11 is still the batch's private clamp, and only the bit-identical
    # batch/scalar parity check reaches it.
    "M10 shared energy bound dropped": (TM, [(
        "    return np.minimum(drawn, np.maximum(available, 0.0))",
        "    return drawn")]),
    "M11 batch cap not clamped": (TM, [(
        "                        dT_buf = np.where(over, dT_cap, dT_buf)",
        "                        dT_buf = np.where(over, dT_buf, dT_buf)")]),
}
for name, (path, edits) in MUTANTS.items():
    if sys.argv[2:] and not any(name.startswith(k) for k in sys.argv[2:]):
        continue
    src = open(path).read()
    mutated = src
    ok = True
    for old, new in edits:
        n = mutated.count(old)
        if n != 1:
            print(f"{name}: TARGET MISSING OR AMBIGUOUS ({n})")
            ok = False
            break
        mutated = mutated.replace(old, new, 1)
    if not ok:
        continue
    open(path, "w").write(mutated)
    try:
        run = subprocess.run([sys.executable, sys.argv[1]], capture_output=True,
                             text=True)
    finally:
        # Restore by writing back the bytes read before the edit: the trees
        # this runs in are scratch copies with no .git, and a checkout would
        # also revert an uncommitted change if one were ever present.
        open(path, "w").write(src)
    out = run.stdout
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    if not fails and run.returncode != 0:
        # A checker that dies must never read as a survivor: print why, and
        # say plainly that this mutant was not judged. (probe.py exits 1 on
        # a FAIL line, so a nonzero rc with no FAIL line is a crash.)
        tail = (run.stderr or "").strip().splitlines()[-6:]
        print(f"{name}: CHECKER FAILED rc={run.returncode} -- NOT JUDGED")
        for line in tail:
            print("   |", line[:160])
        continue
    print(f"{name}: {'KILLED' if fails else 'SURVIVED'}")
    for f in fails:
        print("   ", f[:160])
