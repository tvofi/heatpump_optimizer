import sys, types, random
import numpy as np
sys.path[:0] = ["/tmp/hpo-rev-3869-delta/tests/hastub", "/tmp/hpo-rev-3869-delta/custom_components", "/tmp/hpo-rev-3869-delta/tests"]
import heatpump_optimizer.duty_legs as orig
src = open(orig.__file__).read()
M = {
 "5ba171ad": ("np.take_along_axis(codes, np.maximum(known, 0), axis=-1)", "np.take_along_axis(codes, known, axis=-1)"),
 "66bb4d09": ("np.maximum(s_idx - 1, 0)", "s_idx - 1"),
 "a4744748": ("right = np.where(e_idx < idx[-1]", "right = np.where(e_idx <= idx[-1]"),
 "a257ad19": ("short = two & (dhw_run < dhw_min)", "short = two & (dhw_run <= dhw_min)"),
 "463d143f": ("        if not (whole.any() or lengthen.any()):\n            break\n", "        if False:\n            break\n"),
 "CONTROL_killable": ("short = two & (dhw_run < dhw_min)", "short = two & (dhw_run < dhw_min + 1.0)"),
}
def load(name, s):
    m = types.ModuleType("heatpump_optimizer._mut_" + name); m.__package__ = "heatpump_optimizer"; m.__file__ = orig.__file__
    exec(compile(s, orig.__file__, "exec"), m.__dict__); return m
rng = random.Random(3869)
cases = []
for _ in range(4000):
    n = rng.randint(1, 8)
    def kw(): return [rng.choice([0.0, 0.0, 0.05, 0.3, 1.0, 2.0, 3.5, 6.0]) * rng.choice([1, rng.random() * 2]) for _ in range(n)]
    sp, dh = kw(), kw()
    rule = orig.LegRule(rng.choice(["dhw", "space"]), rng.choice([None, 0.5, 2.0, 5.0]),
                        rng.choice([0, 0, 2, 5, 7.5, 10, 15, 30, 45]), rng.choice([0, 0, 2, 5, 6, 7.5, 10, 15, 30, 45]),
                        rng.choice([orig.IDLE, orig.SPACE, orig.DHW]))
    cases.append((sp, dh, rule, rng.choice([0.0, 0.1, 0.5]), rng.choice([None, 0.5])))
def out(m, c):
    sp, dh, rule, lost, floor = c
    a = m.availability(np.array(sp), np.array(dh), lost, floor, rule)
    return (m.plan_legs(sp, dh, floor, rule), None if a is None else tuple(np.round(a, 12)))
base = [out(orig, c) for c in cases]
for k, (a, b) in M.items():
    assert src.count(a) == 1, k
    m = load(k, src.replace(a, b))
    diff = sum(1 for c, o in zip(cases, base) if out(m, c) != o)
    print(k, "differing", diff, "of", len(cases))
