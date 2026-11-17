"""D0-s2 M4 plant property (round 11): does manual-valve-buffer's plan differ from the plan with no buffer?

D0.md step 4: `manual-valve-buffer` -- "the plan differs from the plan with no buffer". The exact
counterpart is the SAME cell config (manual valve, same house, prices, weather, zones, DHW, horizon) with
the buffer below the store threshold (buffer_tank_volume 35 L = DEFAULT_BUFFER_TANK_VOLUME, under
const.BUFFER_STORE_MIN_VOLUME = 100 L), so ThermalParameters.buffer_is_store is False and only the store
is removed (the valve stays).
Metric (one line): l1_kwh = sum_k |P_store[k] - P_nostore[k]| * dt over the shipped space plans
  (OptimizationResult.power_schedule); beside it the energy SEK of each shipped plan at the cell's prices
  and each plan's charge share (energy in the cheapest third of steps / total energy).
Count key: the shipped OptimizationResult.power_schedule the production seam returns.
A cell is "identical" when l1_kwh < 1e-3 kWh.
Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalParameters.buffer_is_store
  (read by the production solve), HeatPumpOptimizer.optimize (driven).
Perturbation: STORE_MIN=10000 patches thermal_model.BUFFER_STORE_MIN_VOLUME so the 200 L buffer is no store
  either: l1_kwh must move DOWN (the store's share leaves; the two volumes' modelled thermal mass stays, so not
  to 0). Measured on winter_extreme/winter_cold/single-zone/no-dhw/manual-valve-buffer/24h: 16.08 -> 15.03 kWh.
Null control: --price flat (the store's value comes from a price spread; at flat prices the charge share
  difference must shrink).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s2/mvb_nobuffer.py \
           [--price flat] [--out F.jsonl] [--all]     (--all: every manual-valve-buffer cell of enum_cells.py)
Expected: values in results/mvb_*.jsonl; tolerance +-1e-3 kWh (solver floats).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B2, 4 vCPU, shared.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
import subprocess
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells  # noqa: E402
import numpy as np  # noqa: E402
import heatpump_optimizer.thermal_model as tm  # noqa: E402


def solve(line, volume, price_override):
    price, weather, topo, dhw, plant, h = cells.parse_cell(line)
    cfg = cells.cell_config(topo, dhw, plant)
    cfg["buffer_tank_volume"] = volume
    rec, _ = cells.build_record(cfg, price_override or price, weather, h)
    opt = rec.optimizer()
    res = opt.optimize(inputs=rec.inputs)
    pw = np.asarray(res.power_schedule, float)
    pr = np.asarray(rec.inputs.forecast.prices, float)[:pw.size]
    dt = float(rec.config.dt_hours)
    e = float(pw.sum() * dt)
    cheap = pr <= np.quantile(pr, 1 / 3.0)
    return {"plan": pw, "energy_sek": float(np.sum(pr * pw) * dt), "kwh": e,
            "charge_share": float(pw[cheap].sum() * dt / e) if e > 1e-9 else float("nan"),
            "J": float(res.objective_value), "store": bool(rec.params.buffer_is_store) if hasattr(rec.params, "buffer_is_store") else None}


def one(line, price_override):
    a = solve(line, 200.0, price_override)
    b = solve(line, 35.0, price_override)
    dt = 0.25
    return {"cell": line, "price_arm": price_override or "cell",
            "l1_kwh": float(np.abs(a["plan"] - b["plan"]).sum() * dt),
            "store_kwh": a["kwh"], "nostore_kwh": b["kwh"],
            "store_sek": a["energy_sek"], "nostore_sek": b["energy_sek"],
            "store_charge_share": a["charge_share"], "nostore_charge_share": b["charge_share"],
            "store_flag": a["store"], "nostore_flag": b["store"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cells", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--price")
    ap.add_argument("--out")
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    lines = list(a.cells)
    if a.all:
        allc = subprocess.run([sys.executable, os.path.join(HERE, "enum_cells.py")], capture_output=True,
                              text=True, check=True).stdout.split()
        lines += [l for l in allc if not l.startswith("coord/") and l.split("/")[4] == "manual-valve-buffer"]
        if a.price:
            lines = sorted({a.price + "/" + "/".join(l.split("/")[1:]) for l in lines})
    i, k = (int(x) for x in a.shard.split("/"))
    lines = [l for j, l in enumerate(lines) if j % k == i]
    done = set()
    if a.out and os.path.exists(a.out):
        for l in open(a.out):
            try:
                done.add(json.loads(l)["cell"])
            except Exception:
                pass
    patch = mock.patch.object(tm, "BUFFER_STORE_MIN_VOLUME", float(os.environ["STORE_MIN"])) \
        if os.environ.get("STORE_MIN") else mock.patch.object(tm, "BUFFER_STORE_MIN_VOLUME", tm.BUFFER_STORE_MIN_VOLUME)
    c0, t0 = time.process_time(), time.thread_time()
    with patch:
        for line in lines:
            if line in done:
                continue
            try:
                r = one(line, None)
            except Exception as err:
                r = {"cell": line, "error": repr(err)}
            print(f"RESULT l1_kwh[{line}]={r.get('l1_kwh', 'nan')} kWh", flush=True)
            if a.out:
                with open(a.out, "a") as f:
                    f.write(json.dumps(r) + "\n")
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin"):
                sw = int(l.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
