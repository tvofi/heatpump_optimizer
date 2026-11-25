"""D12-s2 surfaces: the card and the blueprints on the minimal and the fully mapped plant (D12.M4).

Metric: per surface cell, the usable bar on what a real setup + cycle publishes:
  blueprint -- dangling = default/entity_id ids the blueprint names that no platform built on
               that plant (key: the entity ids async_setup_entry built, as tests/entities.py
               _p6_built_ids derives them); card -- pages that throw or render empty, and the
               setup page's drawn "Lower floor" boxes on a plant with no lower zone configured
               (key: the card's own rendered markup from the published setup_topology).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s2/surfaces.py [--perturb two_zone]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export as handed to the seat): see REPORT.md.
Perturbation: --perturb two_zone (cells.py's: absent/auto two_zone_mode takes the presence rule):
  min_setup_two_zone and card_lower_zone_min go to zero.
Machine: box B5, shared; counts are contention-immune.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import datetime as _dt
import json
import logging
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells as C  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
PKG = Path("custom_components/heatpump_optimizer")
_ID = re.compile(r"\b(sensor|binary_sensor|switch|climate|button|datetime)\.heat_pump_optimizer_[a-z0-9_]+\b")


def _js(v):
    if isinstance(v, (_dt.datetime, _dt.date)):
        return v.isoformat()
    if isinstance(v, float) and v != v:
        return None
    if isinstance(v, dict):
        return {str(k): _js(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_js(x) for x in v]
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    return str(v)


def states_of(entities):
    st = {}
    for e in entities:
        mod = type(e).__module__.rsplit(".", 1)[-1]
        eid = getattr(e, "entity_id", None)
        tkey = getattr(e, "_attr_translation_key", None)
        if not eid and tkey:
            eid = f"{mod}.heat_pump_optimizer_{tkey}"
        if not eid:
            continue
        try:
            if mod in ("binary_sensor", "switch"):
                state = "on" if e.is_on else "off"
            elif mod == "climate":
                state = str(e.hvac_mode)
            else:
                state = e.native_value
            attrs = getattr(e, "extra_state_attributes", None) or {}
        except Exception:  # noqa: BLE001
            continue
        st[str(eid)] = {"state": "unknown" if state is None else str(_js(state)), "attributes": _js(attrs)}
    return st


def blueprint_refs(path: Path):
    text = "\n".join(l for l in path.read_text(errors="replace").splitlines()
                     if re.match(r"\s*(-\s*)?(default|entity_id)\s*:", l))
    return sorted(set(m.group(0) for m in _ID.finditer(text)))


async def measure(perturbed: bool):
    async def solve(hass, opt, inputs):
        return optimize_in_process(opt, inputs)
    cm._await_optimize = solve
    C.dt_util.now = lambda *a, **k: C.NOW
    C.dt_util.utcnow = lambda *a, **k: C.NOW
    out = {}
    for plant, cfg in (("min", C.min_plant()), ("ref", C.ref_plant())):
        res = await C.run_cell(cfg)
        ents = res["entity_objs"]
        st = states_of(ents)
        built = set(st)
        topo = res["coord"].describe_setup()
        out[plant] = {"built": built, "states": st, "two_zone": bool(topo.get("two_zone")),
                      "bar": C.bar(cfg, res)}
    return out


def main() -> int:
    perturbed = "--perturb" in sys.argv and "two_zone" in sys.argv
    logging.disable(logging.CRITICAL)
    if perturbed:
        C.PERTURB["two_zone"](True)
    t0p, t0t = time.process_time(), time.thread_time()
    res = asyncio.run(measure(perturbed))
    tmp = Path(tempfile.mkdtemp(prefix="d12s2-surf-"))
    fails = 0
    # blueprints
    for bp in sorted(Path("blueprints").rglob("*.yaml")):
        refs = blueprint_refs(bp)
        for plant in ("min", "ref"):
            dangling = [r for r in refs if r not in res[plant]["built"]]
            print(f"SURFACE blueprint {bp}\t{plant}\trefs={len(refs)} dangling={dangling}")
        if any(r not in res["ref"]["built"] for r in refs):
            fails += 1
    # cards: every .js under www/ the enumerator lists
    card_lower = {}
    for card in sorted((PKG / "www").glob("*.js")):
        for plant in ("min", "ref"):
            sp = tmp / f"{plant}.json"
            sp.write_text(json.dumps(res[plant]["states"]))
            proc = subprocess.run(["node", str(HERE / "card_surface.mjs"), str(card), str(sp)],
                                  capture_output=True, text=True, timeout=300)
            line = (proc.stdout.strip().splitlines() or ["{}"])[-1]
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                r = {"load_error": (proc.stderr or line)[-300:]}
            bad = [p for p, v in r.get("pages", {}).items() if not v.get("ok")]
            lz = r.get("pages", {}).get("setup", {}).get("lower_zone", 0)
            card_lower[(card.name, plant)] = lz
            print(f"SURFACE card {card}\t{plant}\tload_error={r.get('load_error')!r} bad_pages={bad} "
                  f"setup_lower_floor_boxes={lz}")
            for p in bad:
                print(f"   {p}: {r['pages'][p].get('error')}")
    pt, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"arm={'perturbed' if perturbed else 'baseline'}")
    print(f"RESULT min_setup_two_zone={int(res['min']['two_zone'])} count")
    print(f"RESULT ref_setup_two_zone={int(res['ref']['two_zone'])} count")
    print(f"RESULT card_lower_zone_min={card_lower.get(('heatpump-optimizer-card.js', 'min'), -1)} count")
    print(f"RESULT card_lower_zone_ref={card_lower.get(('heatpump-optimizer-card.js', 'ref'), -1)} count")
    print(f"RESULT blueprint_dangling_on_ref={fails} count")
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
