

CLS = co.HeatPumpOptimizerCoordinator


def snapshot():
    """A learner snapshot whose three restorable learners differ from a fresh coordinator's in one field each."""
    src = coord()
    p = src._price_model.as_dict()
    p["shapes"][0][0], p["days"][0] = 1.3, 5
    cf = src._comfort_learner.as_dict()
    cf["learned_weight"], cf["evidence"] = 8.0, 2.0
    d = src._defrost.as_dict()
    d["factors"][0][0], d["counts"][0][0] = 0.8, 5
    return {"price_model": p, "comfort": cf, "defrost": d}


def restored(fn, learners):
    c = coord()
    fn(c, learners)
    return {
        "price_shape00": round(float(c._price_learner.model.as_dict()["shapes"][0][0]), 6),
        "comfort_learned_weight": float(c._comfort_learner.as_dict()["learned_weight"]),
        "defrost_factor00": float(c._defrost.as_dict()["factors"][0][0]),
        "defrost_published": c._thermal_params.defrost_derate is c._defrost,
    }


def run(old, field):
    mut = recompile(CLS, "_apply_learner_payloads", old, "if False:")
    snap = snapshot()
    b, m = restored(CLS._apply_learner_payloads, snap), restored(mut, snap)
    print(f"RESULT {field}_baseline={b[field]}")
    print(f"RESULT {field}_mutant={m[field]}")
    print(f"RESULT fields_moved={sum(int(b[k] != m[k]) for k in b)} count ({ {k: (b[k], m[k]) for k in b if b[k] != m[k]} })")
    for name, learners in (("non_dict_payload", {k: None for k in snap}), ("empty", {}), ("fresh_state", {
            "price_model": coord()._price_model.as_dict(), "comfort": coord()._comfort_learner.as_dict(),
            "defrost": coord()._defrost.as_dict()})):
        bb, mm = restored(CLS._apply_learner_payloads, learners), restored(mut, learners)
        print(f"RESULT null_{name}_delta={sum(int(bb[k] != mm[k]) for k in bb if k != 'defrost_published')} count")


run("if isinstance(defrost, dict):", "defrost_factor00")
tail()
