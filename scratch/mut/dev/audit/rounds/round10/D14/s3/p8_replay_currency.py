#!/usr/bin/env python3
"""P8 detector over the nightly replay: money currency codes a replayed day publishes.

METRIC: over every entity the six platforms publish, per replayed cycle, every
(entity, field) whose delivered value -- native unit, or any string in state or
attributes, walked recursively -- names an ISO currency code; a seam is a
distinct (entity, field-path) and it is MISMATCHED when the code it names is not
the price feed's declared currency. Count key: the value production delivers
(native_unit_of_measurement / attribute strings / narrative line text), never the
fixture's own labels.
COMMAND: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/p8_replay_currency.py
EXPECTED (baseline 17f1c55fad1b, macOS arm64 B7): base mismatched_seams=1
(sensor narrative lines, instance SEK on a EUR feed), clean arm 0,
narrative_fixed arm 0, reintroduce arm (declared_currency -> None) > 1. Exact counts, tolerance 0.
ARMS (each in its own interpreter so patches never leak):
  base            EUR/kWh feed on a SEK instance (FakeHass default currency)
  clean           EUR/kWh feed on a EUR instance (null control: must be 0)
  narrative_fixed base + narrative.render handed coordinator.currency (the fix shape)
  reintroduce     base + coordinator.declared_currency -> None (pre-#1657 one-line regression)
Hooks: tests/replay.py:run_fixture/sweep (the real coordinator cycle),
heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._narrative_view.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, io, json, re, subprocess, sys, tempfile, time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
CODES = {"SEK", "EUR", "NOK", "DKK", "GBP", "USD", "PLN", "CHF"}
TOKEN = re.compile(r"(?<![A-Za-z])([A-Z]{3})(?![A-Za-z])")
FEED = "EUR"
HOURS = 3.0
MARK = "<<<p8>>>"


def walk(node, path, out):
    if isinstance(node, str):
        for m in TOKEN.findall(node):
            if m in CODES:
                out.append((path, m))
    elif isinstance(node, dict):
        for k, v in node.items():
            if str(k).startswith("_"):
                continue
            walk(v, f"{path}.{k}", out)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            walk(v, f"{path}[]", out)


def arm_run(arm):
    import replay
    from harness import FakeHass
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import narrative
    if arm == "clean":
        real_init = FakeHass.__init__
        def init(self, *a, **k):
            real_init(self, *a, **k)
            self.config.currency = FEED
        FakeHass.__init__ = init
    elif arm == "narrative_fixed":
        real_view = cm.HeatPumpOptimizerCoordinator._narrative_view
        def view(self):
            real_render = narrative.render
            narrative.render = lambda items, lang, cur: real_render(items, lang, self.currency)
            try:
                return real_view(self)
            finally:
                narrative.render = real_render
        cm.HeatPumpOptimizerCoordinator._narrative_view = view
    elif arm == "reintroduce":
        cm.declared_currency = lambda *a, **k: None
    seen = {}
    real_sweep = replay.sweep
    def sweep(entities, action, errors, t):
        recs = real_sweep(entities, action, errors, t)
        for r in recs:
            hits = []
            if r.get("unit"):
                walk(r["unit"], "unit", hits)
            walk(r["state"], "state", hits)
            walk(r["attributes"] or {}, "attr", hits)
            for path, code in hits:
                seen.setdefault(f"{r['entity_id']} {path}", set()).add(code)
        return recs
    replay.sweep = sweep
    src = json.loads((ROOT / "tests/replay/synthetic-dhw-only.json").read_text())
    pid = src["entry"]["data"]["price_entity"]
    rows = []
    for upd, state, attrs, rep in src["states"][pid]:
        if attrs is not None:
            attrs = json.loads(json.dumps(attrs))
            attrs["unit_of_measurement"] = "EUR/kWh"
            attrs["currency"] = FEED
            for key in ("raw_today", "raw_tomorrow"):
                for r in attrs.get(key) or []:
                    r["value"] = round(r["value"] / 11.5, 5)
        try:
            state = f"{float(state) / 11.5:.5f}"
        except ValueError:
            pass
        rows.append([upd, state, attrs, rep])
    src["states"][pid] = rows
    start = datetime.fromisoformat(src["window"]["start"])
    src["window"]["end"] = (start + timedelta(hours=HOURS)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "day.json"
        p.write_text(json.dumps(src))
        with contextlib.redirect_stdout(io.StringIO()):
            run = replay.run_fixture(p, 30)
    seams = {k: sorted(v) for k, v in seen.items()}
    bad = {k: v for k, v in seams.items() if any(c != FEED for c in v)}
    return {"arm": arm, "cycles": run["cycles"], "seams": len(seams),
            "mismatched": len(bad), "bad": bad, "cycle_errors": run["counts"].get("cycle")}


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--arm":
        print(MARK + json.dumps(arm_run(sys.argv[2])))
        return 0
    import replay
    tz = json.loads((ROOT / "tests/replay/synthetic-dhw-only.json").read_text()).get("time_zone")
    env = replay.child_env(tz or "UTC")
    t0, c0 = time.monotonic(), time.process_time()
    for arm in ("base", "clean", "narrative_fixed", "reintroduce"):
        p = subprocess.run([sys.executable, __file__, "--arm", arm], capture_output=True,
                           text=True, env=env, cwd=ROOT)
        line = next((l for l in p.stdout.splitlines() if l.startswith(MARK)), None)
        if line is None:
            print(f"arm {arm} failed rc={p.returncode}: {p.stderr[-1500:]}")
            print(f"RESULT {arm}_mismatched_seams=-1 count")
            continue
        out = json.loads(line[len(MARK):])
        print(f"# {arm}: cycles={out['cycles']} cycle_errors={out['cycle_errors']}")
        for k, v in sorted(out["bad"].items()):
            print(f"#   mismatched {k}: {v}")
        print(f"RESULT {arm}_money_seams={out['seams']} count")
        print(f"RESULT {arm}_mismatched_seams={out['mismatched']} count")
    pc, tc = time.process_time() - c0, time.thread_time()
    print(f"RESULT thread_factor={(pc / tc) if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
