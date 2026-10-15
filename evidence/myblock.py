"""Reviewer's runner: header of tests/features.py + a prelude + one marker-delimited block.
usage: python myblock.py <repo root> <A|B|C|D>  -> rc 0 when every check in the block passed"""
import os, sys
root, which = sys.argv[1], sys.argv[2]
os.chdir(root)
sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
path = "tests/features.py"
src = open(path, encoding="utf-8").read()
PRE = {
 "A": "",
 "B": "import asyncio as _asyncio\nfrom harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass\n"
      "_LC_DATA = {'price_source': 'entity', 'price_entity': 'sensor.prices', 'weather_entity': 'weather.home'}\n",
 "C": "from datetime import datetime as _SavDT\n"
      "from heatpump_optimizer.optimizer import HeatPumpOptimizer as _PvOpt, OptimizationConfig as _PvOptCfg, OptimizationResult as _SavOR\n"
      "from heatpump_optimizer.thermal_model import ThermalModel as _PvModel, ThermalParameters as _PvParams\n"
      "_bl_opt = _PvOpt(_PvModel(_PvParams()), _PvOptCfg(target_temp=21.0))\n"
      "_ts_sav = [_SavDT(2026, 2, 10, 12, 0) + timedelta(minutes=15 * i) for i in range(4)]\n",
 "D": "",
}
MARK = {
 "A": ("# R10 D3-s2-01: the two store loaders", "_r7 = SnapshotRing()"),
 "B": ('R.section("Weather staleness is surfaced (M2)")', "# R5-D1-07 (#1298): the success"),
 "C": ("# R10 D3-s1-02: every optional", "# #1499: Heat Pump Action"),
 "D": ("# R10 I1 sweep: every per-step", "# The seam rule, as a barrier"),
}
s, e = MARK[which]
i = src.index(s); j = src.index(e, i)
ns = {"__file__": os.path.abspath(path), "__name__": "rev_block"}
exec(compile(src[: src.index('R = Results("Feature modules")')], path, "exec"), ns)
exec('R = Results("rev block")', ns)
exec(PRE[which], ns)
exec(compile(src[i:j], path + "[block " + which + "]", "exec"), ns)
sys.exit(ns["R"].close("REV BLOCK " + which))
