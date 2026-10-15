"""Reviewer's own runner: executes the D10-s1-51 census block from tests/features.py
with just the fixtures it needs (my instrument, not the fixer's)."""
import os, sys
root = os.path.abspath(sys.argv[1]); path = os.path.join(root, "tests/features.py")
sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
os.chdir(root)
src = open(path).read()
def cut(a, b):
    i = src.index(a); return src[i:src.index(b, i)]
header = src[: src.index('R = Results("Feature modules")')]
ns = {"__file__": path, "__name__": "census"}
exec(compile(header, path, "exec"), ns)
exec('R = Results("census")\nimport asyncio as _asyncio\nfrom harness import FakeHass, FakeEntry', ns)
exec(cut("from pathlib import Path as _Path\n\nimport heatpump_optimizer as _integ", "# #924: the fixed first refresh fetches through"), ns)
exec(cut("def _seed_prices(hass", "\n\n\n"), ns) if False else None
exec(cut("_OFFLINE_PRICES = {", "_LC_DATA = {"), ns)
exec(cut("_LC_DATA = {", "# The full lifecycle through"), ns)
exec(cut('_lc_catalog = set(', "R.check("), ns)
exec(cut("R.section(\"exception translations", "# A loaded entry, so the handlers"), ns)
sys.exit(ns["R"].close("CENSUS"))
