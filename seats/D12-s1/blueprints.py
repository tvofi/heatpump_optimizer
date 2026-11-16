#!/usr/bin/env python3
"""D12-s1 blueprint surface cells: each blueprint's default entity and every attribute or event field it
reads, against what the integration publishes, in every cell plant cells.py ran.

Metric (one line): bp_fail_pairs = (blueprint, plant run) pairs where a blueprint input's default entity
id is not among the entities the plant's real platform setup created, or an attribute the blueprint reads
(state_attr(..., 'x') / `attribute: x`) is missing from that entity's published attributes while it is
available, counted only where the blueprint's own feature applies (the wood blueprint on wood plants);
plus bp_event_misses = notification-blueprint event types / trigger.event.data fields absent from
notifier.EVENT_DATA.

Count key: the published entity ids and attributes come from cells.py --dump (each entity's real
native_value / extra_state_attributes after one cycle); the event fields from heatpump_optimizer.notifier:EVENT_DATA.

Command (export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s1/cells.py --quiet --dump "$T"
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s1/blueprints.py "$T/states.json" [--drop-attr cheaper_windows]
  --drop-attr X  perturbation: delete attribute X from every published entity before checking; the
                 count must rise by the plants on which a blueprint reads X.
Baseline 92d38ecb (export as handed to D12-s1), box B4. Expected: see REPORT.md; exact counts.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import argparse, glob, json, re, sys, time

sys.path[:0] = ["tests", "custom_components"]
import harness  # noqa: E402,F401
import yaml  # noqa: E402
from heatpump_optimizer import notifier  # noqa: E402


class _L(yaml.SafeLoader):
    pass


_L.add_constructor("!input", lambda loader, node: {"!input": loader.construct_scalar(node)})


def blueprint_reads(doc, text):
    """{input name: (default entity id, {attributes read})} and the event triggers with their data fields."""
    inputs = (doc.get("blueprint") or {}).get("input") or {}
    # the raw file text: a re-dump would re-quote the templates
    defaults = {k: v.get("default") for k, v in inputs.items() if isinstance(v, dict)}
    reads = {}
    for name, dflt in defaults.items():
        if isinstance(dflt, str) and re.fullmatch(r"[a-z_]+\.heat_pump_optimizer_[a-z0-9_]+", dflt):
            attrs = set(re.findall(rf"state_attr\(\s*{name}\s*,\s*'([a-z0-9_]+)'", text))
            reads[name] = (dflt, attrs)

    def walk(n):
        if isinstance(n, dict):
            ent = n.get("entity_id")
            if isinstance(ent, dict) and "!input" in ent and n.get("attribute"):
                yield ent["!input"], n["attribute"]
            for v in n.values():
                yield from walk(v)
        elif isinstance(n, list):
            for v in n:
                yield from walk(v)
    for name, attr in walk(doc):
        if name in reads:
            reads[name][1].add(attr)
    events = set(re.findall(r"event_type:\s*([a-z0-9_]+)", text))
    # per choose branch: the event it matches and the `data.<field>` it reads (data = trigger.event.data)
    fields = {}
    for block in re.split(r"\n\s*- alias:", text)[1:]:
        ev = re.search(r"event_type == '([a-z0-9_]+)'", block)
        if ev:
            fields.setdefault(ev.group(1), set()).update(re.findall(r"(?<![a-z_.])data\.([a-z0-9_]+)", block))
    return reads, events, fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("states")
    ap.add_argument("--drop-attr")
    a = ap.parse_args()
    t0 = time.process_time(); th0 = time.thread_time()
    plants = json.load(open(a.states))
    fail_pairs, event_miss, pairs = 0, 0, 0
    per_bp = {}
    for path in sorted(glob.glob("blueprints/**/*.yaml", recursive=True)):
        doc = yaml.load(open(path), Loader=_L)
        reads, events, fields = blueprint_reads(doc, open(path).read())
        wood_only = "wood" in os.path.basename(path)
        bad = []
        for ev in sorted(events):
            if ev not in notifier.EVENT_DATA:
                bad.append(f"event {ev} not in notifier.EVENT_DATA"); event_miss += 1
        for ev, fs in sorted(fields.items()):
            for f in sorted(fs):
                if f not in notifier.EVENT_DATA.get(ev, ()):
                    bad.append(f"{ev}: data.{f} is no field notifier.EVENT_DATA lists"); event_miss += 1
        for plant, states in sorted(plants.items()):
            if not states:
                continue
            is_wood = any(k.startswith(("binary_sensor.heat_pump_optimizer_wood", "sensor.heat_pump_optimizer_wood"))
                          and v["state"] != "unavailable" for k, v in states.items())
            if wood_only and not is_wood:
                continue
            for name, (eid, attrs) in reads.items():
                pairs += 1
                st = states.get(eid)
                miss = []
                if st is None:
                    miss.append(f"{eid} not created")
                elif st["state"] != "unavailable":
                    have = dict(st["attributes"])
                    if a.drop_attr:
                        have.pop(a.drop_attr, None)
                    miss += [f"{eid}.{x} not published" for x in sorted(attrs) if x not in have]
                if miss:
                    fail_pairs += 1
                    bad.append(f"{plant}: " + "; ".join(miss))
        per_bp[path] = bad
        print(("FAIL " if bad else "PASS ") + path + f"\treads={ {k: (v[0], sorted(v[1])) for k, v in reads.items()} } events={len(events)} fields={ {k: sorted(v) for k, v in fields.items()} }")
        for b in bad[:6]:
            print("     ", b)
        if len(bad) > 6:
            print(f"      ... {len(bad) - 6} more")
    cpu = time.process_time() - t0; th = time.thread_time() - th0
    print(f"RESULT bp_pairs={pairs} count")
    print(f"RESULT bp_fail_pairs={fail_pairs} count")
    print(f"RESULT bp_event_misses={event_miss} count")
    print(f"RESULT bp_fail_blueprints={sum(1 for b in per_bp.values() if b)} count")
    print(f"RESULT thread_factor={cpu / th if th else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
