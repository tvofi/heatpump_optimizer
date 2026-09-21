"""Sweep the buffer-coupling substep margin: for a target substep count N,
insert a buffer coupling term choosing the ratio so ceil(ratio/1.5) == N, then
run a focused bump scan on the shipped 35 L valved config and report the worst
cooling delta. Each N runs in a FRESH interpreter (the module is not reloadable
in-process). Restores the file at exit.

Run from the worktree root:
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/seat-a/sweep_substeps.py
"""
import os
import subprocess
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.path.abspath(os.getcwd())
TM = os.path.join(ROOT, "custom_components/heatpump_optimizer/thermal_model.py")
RATIOS = {  # target n_sub -> buffer ratio injected (worst contribution * dt)
    1: 0.0, 6: 8.5, 7: 10.0, 8: 11.5, 9: 13.0, 10: 14.5, 12: 17.5,
}
BLOCK = (
    "        # EXPERIMENT buffer coupling\n"
    "        if p.two_zone_enabled and mixing_valve.is_throttling(\n"
    "            p.mixing_valve_mode\n"
    "        ):\n"
    "            worst = max(worst, {r} / dt_hours)\n"
)


def patch(ratio):
    rel = os.path.relpath(TM, ROOT)
    base = subprocess.check_output(["git", "show", "HEAD:" + rel], cwd=ROOT, text=True)
    if ratio <= 0.0:
        txt = base
    else:
        marker = "        ratio = worst * dt_hours\n"
        assert marker in base, "marker missing"
        txt = base.replace(marker, BLOCK.format(r=ratio) + marker, 1)
    with open(TM, "w") as fh:
        fh.write(txt)


def scan():
    import numpy as np
    from dataclasses import replace
    sys.path.insert(0, ROOT)
    import tests.golden as g
    sys.path.insert(0, os.path.join(ROOT, "tools/audit/round5/D2/seat-a"))
    import d2a_common as C

    b = g.make(
        two_zone=True, dhw=False,
        config_overrides={"mixing_valve_mode": "manual",
                          "buffer_tank_volume": 35.0,
                          "buffer_max_temperature": 70.0},
        state_overrides={"buffer_tank_temperature": 32.0},
    )
    m = b["optimizer"].model
    n = 96
    base = np.random.default_rng(99).uniform(0, m.params.max_electrical_power, n)
    ext = C.ext_forecast(n)

    def run(sched):
        return m.simulate_trajectory_with_dhw(
            replace(b["state"]), sched, np.zeros(n), b["outdoor"], b["wind"],
            b["rain"], b["solar"], dt_hours=0.25, external_heat_kw=ext,
            humidity=np.full(n, 55.0), start_hour=6.5)

    buf0 = np.asarray(run(base)[5], dtype=float)
    out = []
    for bump in (1e-3, 0.1, 1.0):
        worst, at = 0.0, None
        for i in range(0, n, 3):
            s = base.copy()
            s[i] += bump
            d = np.asarray(run(s)[5], dtype=float)[i + 1:] - buf0[i + 1:]
            mn = float(d.min())
            if mn < worst:
                worst, at = mn, i
        out.append((bump, worst, at))
    n_sub = m._stability_substeps(0.0, 0.0, 0.25)
    print("RESULT n_sub_measured=%d  %s" % (
        n_sub, " ".join("b=%g:%.4e@%s" % (b2, w, a) for b2, w, a in out)), flush=True)


def main():
    if sys.argv[1:] == ["--run"]:
        scan()
        return
    ns = [int(x) for x in sys.argv[1:]] or [1, 6, 7, 8, 9, 10, 12]
    try:
        for N in ns:
            patch(RATIOS[N])
            subprocess.run([sys.executable, os.path.abspath(__file__), "--run"],
                           cwd=ROOT, check=True)
    finally:
        patch(0.0)
        print("restored pristine file", flush=True)


if __name__ == "__main__":
    main()
