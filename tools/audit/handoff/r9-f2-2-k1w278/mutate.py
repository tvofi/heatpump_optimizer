"""F2.2 mutation proof: each mutant is one textual edit of a production line in
a copy of the head tree (git archive of HEAD_SHA), run through the whole of
tests/features.py; prints every FAIL line. Usage: mutate.py HEAD_SHA OUTDIR [M..]
"""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

REPO = "/home/claude/heatpump_optimizer"
OPT = "custom_components/heatpump_optimizer/optimizer.py"
TM = "custom_components/heatpump_optimizer/thermal_model.py"
PY = "/home/claude/venv314/bin/python"
MUTANTS = {
    # Null control: no edit at all; the whole suite from the same archive.
    "M0": (OPT, "_DHW_MIN_RUN_CHUNK = 8", "_DHW_MIN_RUN_CHUNK = 8"),
    # D9-s1-01: the batched comfort terms back on a per-row loop (single zone).
    "M1": (OPT, "        room_t = room_temps[:, 1:]\n        undershoot = np.maximum(0, temp_min_bounds - room_t)",
           "        if room_temps.shape[0] > 1:\n"
           "            _rows = [self._comfort_terms_batch(room_temps[b:b + 1], upper_temps[b:b + 1], lower_temps[b:b + 1], comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band) for b in range(room_temps.shape[0])]\n"
           "            return np.array([r[0][0] for r in _rows]), np.array([r[1][0] for r in _rows])\n"
           "        room_t = room_temps[:, 1:]\n        undershoot = np.maximum(0, temp_min_bounds - room_t)"),
    # RC-sw1: cycling_penalty_batch back on a per-row loop.
    "M2": (OPT, "    swing = _row_sums(np.abs(np.diff(np.asarray(power_matrix, dtype=float), axis=1)))",
           "    swing = np.concatenate([_row_sums(np.abs(np.diff(np.asarray(power_matrix[b:b + 1], dtype=float), axis=1))) for b in range(shape[0])])"),
    # D9-s1-02: the fused value+gradient line deleted from the multi-start.
    "M3": (OPT, "                fun = _fused_value_and_gradient(\n                    batch_objective, bounds, fd_eps, remember,\n                )\n                jac = True\n",
           "                pass\n"),
    # D9-s1-04: the early exit gone -- one chunk spans the whole suffix.
    "M4": (OPT, "            end = min(pos + _DHW_MIN_RUN_CHUNK, size)", "            end = size"),
    # D9-s1-71: the three memo hits deleted.
    "M5": (TM, "        if cached is not None and cached[0] == key:\n            return cached[1]\n        rate = float(",
           "        rate = float("),
    "M6": (TM, "        if cached is not None and cached[0] == key:\n            return cached[1]\n        current = self.dhw_inlet_current",
           "        current = self.dhw_inlet_current"),
    "M7": (TM, "        if cached is None or cached[0] != key:\n            cached = (key, self._windowed_draw_pattern())",
           "        if True:\n            cached = (key, self._windowed_draw_pattern())"),
    # _row_sums' combine tree flattened into a running sum: a different order.
    "M8": (OPT, "    total = (\n        (partial[:, 0] + partial[:, 1]) + (partial[:, 2] + partial[:, 3])\n    ) + ((partial[:, 4] + partial[:, 5]) + (partial[:, 6] + partial[:, 7]))",
           "    total = partial[:, 0] + partial[:, 1] + partial[:, 2] + partial[:, 3] + partial[:, 4] + partial[:, 5] + partial[:, 6] + partial[:, 7]"),
    # _row_sums replaced by numpy's own axis-1 reduction (the #948 shape).
    "M9": (OPT, "    n = rows.shape[1]\n    if n > _PAIRWISE_BLOCK:", "    return np.sum(rows, axis=1)\n    n = rows.shape[1]\n    if n > _PAIRWISE_BLOCK:"),
}


def run(name, head, outdir):
    path, old, new = MUTANTS[name]
    d = tempfile.mkdtemp(prefix=f"f22_{name}_")
    subprocess.run(f"git -C {REPO} archive {head} | tar -x -C {d}", shell=True, check=True)
    p = os.path.join(d, path)
    s = open(p).read()
    assert s.count(old) == 1, (name, s.count(old))
    open(p, "w").write(s.replace(old, new))
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    r = subprocess.run([PY, "tests/features.py"], cwd=d, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if l.lstrip().startswith("FAIL")]
    tail = [l for l in out.splitlines() if "FEATURE CHECKS" in l]
    with open(os.path.join(outdir, f"{name}.log"), "w") as fh:
        fh.write(f"{name} rc={r.returncode} {tail}\n" + "\n".join(fails) + "\n")
    subprocess.run(["rm", "-rf", d])
    return name


if __name__ == "__main__":
    head, outdir = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or list(MUTANTS)
    with ThreadPoolExecutor(3) as ex:
        for n in ex.map(lambda m: run(m, head, outdir), names):
            print("done", n, flush=True)
