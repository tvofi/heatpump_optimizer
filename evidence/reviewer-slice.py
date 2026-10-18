"""Reviewer's own slice driver (not the fixer's): header + the coordinator _Coord/_FakeEntry imports + pump-arbiter
fixtures (to _pa_run) + the early cut-off section, via features_block's block()."""
import os, sys
sys.path.insert(0, "tools/audit/seat")
from features_block import block
path = "tests/features.py"
root = os.getcwd()
sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
src = open(path, encoding="utf-8").read()
ns = {"__file__": os.path.abspath(path), "__name__": "features_block"}
exec(compile(src[: src.index('R = Results("Feature modules")')], path, "exec"), ns)
exec('R = Results("slice")', ns)
exec(compile(block(src, "import asyncio as _asyncio\n\nfrom harness import FakeEntry as _FakeEntry", "def _zone_coord(states"), path + "[coord]", "exec"), ns)
exec(compile(block(src, 'R.section("pump-duty arbiter', "def _pa_run(coord, minutes):"), path + "[pa]", "exec"), ns)
exec(compile(block(src, 'R.section("early cut-off', 'R.section("°F set-points'), path + "[ec]", "exec"), ns)
sys.exit(ns["R"].close("SLICE"))
