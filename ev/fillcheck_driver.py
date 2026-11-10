"""Reviewer's driver: the head's two new memory-pass checks, on one scenario, via the tree's own functions."""
import importlib.util, json, os, sys
tree, label, reps = os.path.abspath(sys.argv[1]), sys.argv[2], int(sys.argv[3])
os.chdir(tree)
sys.path[:0] = [os.path.join(tree, p) for p in ("tests/hastub", "custom_components", "tests")]
sys.argv = ["stress.py"]
spec = importlib.util.spec_from_file_location("stress", "tests/stress.py")
st = importlib.util.module_from_spec(spec); sys.modules["stress"] = st; spec.loader.exec_module(st)
combos = {c["label"]: {k: v for k, v in c.items() if k != "label"} for c in st.sweep_combinations()}
env = st._memory_probe_env()
for i in range(reps):
    clean = float(st._run_memory_probe(["--memory-probe", json.dumps(combos[label])], env)["traced_mb"])
    f = st.intern_fill_readings(combos[label], env)
    lands = f["bare_mb"] - clean > st.INTERN_REBUILD_STEP_BYTES / 1048576
    indep = abs(f["filled_mb"] - clean) <= st.INTERN_FILL_TOLERANCE_MIB
    print(f"RESULT fillcheck tree={os.path.basename(tree)} label={label} clean={clean:.2f} filled={f['filled_mb']:.2f} bare={f['bare_mb']:.2f} interns={f['interns_to_rebuild']} perturbation_lands={'ok' if lands else 'FAIL'} independence={'ok' if indep else 'FAIL'}", flush=True)
