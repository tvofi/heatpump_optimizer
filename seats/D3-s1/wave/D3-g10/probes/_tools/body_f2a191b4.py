NAME, OLD, NEW = "_update_external_heat_detection", "if state.active:", "if False:"


def drive(mutated, active):
    c = make_coord()
    real = c._external_heat.update

    def update(obs):
        real(obs)
        return SimpleNamespace(active=active, source="wood", evidence=["wood top rising 3.0 C/h"])

    with arm(NAME, OLD, NEW, mutated), mock.patch.object(c._external_heat, "update", update), \
            counting("External heat source active") as lg:
        c._update_external_heat_detection()
    return sum(1 for lv, _ in lg.hits if lv == "DEBUG"), bool(c._external_heat_active)


b, m = drive(False, True), drive(True, True)
print(f"RESULT active_baseline=(debugs,flag){b}")
print(f"RESULT active_mutant=(debugs,flag){m}")
print(f"RESULT null_moved={int(drive(False, False) != drive(True, False))} count (detector inactive)")
tail()
