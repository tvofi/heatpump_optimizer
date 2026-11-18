#!/usr/bin/env python3
"""D3.M2/M3 pre-screen table for seat D3-s3's local relaunch (source-only).

Metric (one line): per pool mutant, the closure drivers whose run on the
mutated tree named more failing checks than the unmutated baseline
(tests/mutation_table.py:killed, as prescreen.py logged it), from the final
record prescreen_local.json or, while the run is still going, the crash-safe
per-pair log prescreen_local.progress.jsonl.
Verdicts: KILLED by <drivers>; LIVES = every driver of its closure ran (or was
reach-skipped by mutation_table.reach_skip) and none killed; OPEN = started,
not finished; NOT-RUN = never started; CHEAP-SURVIVED = the
cheap-subset screen (prescreen_cheap.json) ran every driver it allows and none
killed; features/entities/env_drift/boost_drift_replay were not run.
Command:  python3 dev/audit/rounds/round11/D3/s3/prescreen_table.py \
          [--survivors] [--json]
Perturbation: the record's null control (away.py:57 NULL_COMMENT) must read
killed by none; prescreen.py refuses the lane otherwise.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Exact (counts).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    pool_lines = [ln.split("#")[0].strip()
                  for ln in (HERE / "selection_local.txt").read_text().splitlines()
                  if ln.split("#")[0].strip()]
    final = HERE / "prescreen_local.json"
    outc: dict[str, dict] = {}
    verd: dict[str, str] = {}
    drivers: dict[str, list] = {}
    if final.exists():
        d = json.loads(final.read_text())
        outc, verd = d["outcomes"], d["verdicts"]
        for m in d["pool"]:
            drivers[f"{m['file']}:{m['line']} {m['kind']}"] = m["drivers"]
    else:
        prog = HERE / "prescreen_local.progress.jsonl"
        if prog.exists():
            for ln in prog.read_text().splitlines():
                r = json.loads(ln)
                outc.setdefault(r["mutant"], {})[r["driver"]] = r["hit"]
    # The cheap-subset screen (prescreen.py --only <all but features, entities,
    # env_drift, boost_drift_replay>): a kill there is a kill; a site it
    # finished without a kill is CHEAP-SURVIVED, never LIVES.
    cheap: dict[str, dict] = {}
    cverd: dict[str, str] = {}
    cf = HERE / "prescreen_cheap.json"
    if cf.exists():
        d = json.loads(cf.read_text())
        cheap, cverd = d["outcomes"], d["verdicts"]
    else:
        cp = HERE / "prescreen_cheap.progress.jsonl"
        if cp.exists():
            for ln in cp.read_text().splitlines():
                r = json.loads(ln)
                cheap.setdefault(r["mutant"], {})[r["driver"]] = r["hit"]
    for k, o in cheap.items():
        for s, v in o.items():
            outc.setdefault(k, {}).setdefault(s, v)
            if v is True:
                outc[k][s] = True
    for k, v in cverd.items():
        if k not in verd:
            verd[k] = ("CHEAP-SURVIVED" if str(v).startswith("LIVES")
                       else str(v))
    return pool_lines, outc, verd, drivers


def main() -> int:
    pool, outc, verd, drivers = load()
    rows = []
    for short in pool:
        key = "custom_components/heatpump_optimizer/" + short
        o = outc.get(key, {})
        killers = sorted(s for s, v in o.items() if v is True)
        ran = sorted(s for s, v in o.items() if v in (True, False))
        skipped = sorted(s for s, v in o.items() if v == "reach-skip")
        timed = sorted(s for s, v in o.items() if v is None)
        v = verd.get(key)
        if killers:
            state = "KILLED"
        elif v:
            state = str(v).split()[0]
        elif o:
            state = "OPEN"
        else:
            state = "NOT-RUN"
        rows.append({"site": short, "state": state, "verdict": v,
                     "killers": killers, "ran": ran, "reach_skipped": skipped,
                     "timed_out": timed, "drivers": drivers.get(key, [])})
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return 0
    for r in rows:
        if "--survivors" in sys.argv and not r["state"].startswith("LIVES"):
            continue
        print(f"{r['state']}\t{r['site']}\tkillers="
              f"{','.join(k.split('/')[-1] for k in r['killers']) or '-'}\t"
              f"ran={len(r['ran'])} reach_skipped={len(r['reach_skipped'])}"
              f" timed_out={len(r['timed_out'])}")
    from collections import Counter
    c = Counter(r["state"] for r in rows)
    for k, v in sorted(c.items()):
        print(f"RESULT {k}={v} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
