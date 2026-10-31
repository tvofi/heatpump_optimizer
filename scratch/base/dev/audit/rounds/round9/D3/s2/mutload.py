"""Shared loader for D3-s2's witness harnesses (not a harness itself).

`pair(mutant_id)` returns (original_module, mutant_module): the production module imported
normally, and a fresh module object executing the same source with pool.json's one-line
mutation (from pool.json, pool2.json or storeguards.json) applied -- the in-memory perturbation README.md asks for (no on-disk edit).
"""
from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path

ROOT = Path.cwd()
for p in ("tests/hastub", "tests", "custom_components"):
    if p not in sys.path:
        sys.path.insert(0, p)
HERE = Path(__file__).resolve().parent


POOLS = ("pool.json", "pool2.json", "storeguards.json")


def mutant(mid: str) -> dict:
    for name in POOLS:
        path = HERE / name
        if not path.exists():
            continue
        for m in json.loads(path.read_text())["pool"]:
            if m["id"] == mid:
                return m
    raise KeyError(mid)


def pair(mid: str):
    m = mutant(mid)
    stem = Path(m["file"]).stem
    name = f"heatpump_optimizer.{stem}"
    orig = importlib.import_module(name)
    lines = (ROOT / m["file"]).read_text().splitlines(True)
    assert lines[m["line"] - 1].rstrip("\n") == m["old"], "line moved"
    lines[m["line"] - 1] = m["new"] + "\n"
    mod = types.ModuleType(name)
    mod.__package__ = "heatpump_optimizer"
    mod.__file__ = str(ROOT / m["file"])
    exec(compile("".join(lines), m["file"], "exec"), mod.__dict__)
    return orig, mod, m
