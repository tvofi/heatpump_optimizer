OLD = "if bool(np.all(joint_temps <= joint_limit + 1e-9)):"
NEW = "if False:"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# Cost, not behaviour: simulate_dhw_step calls per repair over the joint-shortcut fixtures, baseline vs mutant.
from custom_components.heatpump_optimizer.thermal_model import ThermalModel as _TM  # noqa: E402
cnt = {"n": 0}
_orig = _TM.simulate_dhw_step


def _counted(self, *a, **k):
    cnt["n"] += 1
    return _orig(self, *a, **k)


# the fixtures that take the joint shortcut on the baseline (no per-slot _dhw_raise_fits call)
shortcut = []
_fits = DhwPlanner._dhw_raise_fits
_calls = {"n": 0}


def _cf(self, *a, **k):
    _calls["n"] += 1
    return _fits(self, *a, **k)


with mock.patch.object(DhwPlanner, "_dhw_raise_fits", _cf):
    for seed in range(12):
        for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
            for n, nw in ((24, 3), (96, 24), (48, 10)):
                plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                _calls["n"] = 0
                run(plan, **kw)
                if _calls["n"] == 0:
                    shortcut.append((plan, kw))
steps = {}
with mock.patch.object(_TM, "simulate_dhw_step", _counted):
    for arm, fn in (("baseline", None), ("mutant", MUT)):
        cnt["n"] = 0
        for plan, kw in shortcut:
            run(plan, fn, **kw)
        steps[arm] = cnt["n"]
print(f"RESULT dhw_steps_baseline={steps['baseline']} count  ({len(shortcut)} joint-shortcut fixtures)")
print(f"RESULT dhw_steps_mutant={steps['mutant']} count")
footer()
