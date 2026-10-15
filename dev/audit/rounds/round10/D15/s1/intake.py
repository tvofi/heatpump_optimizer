#!/usr/bin/env python3
"""D15-s1 harness: D15.M1-M4 over a live "Download diagnostics" file.

Metrics (one line each):
  M1 rows_per_version: cycle rows attributed to the newest tag dated before the
     restart gap (>1 h) preceding them; bundle_unwrapped=1 when data.debug found.
  M2 bundle_violations: export.violations over the debug bundle (whole, and with
     a planted-credential arm, which must be > 0).
  M3 ingest_fails_wrapped / ingest_fails_unwrapped: debug_ingest.ingest fails on the
     download as handed vs on data.debug; bias_delta_tail vs bias_delta_by_t: the
     stage-4 re-derivation as written (last N rows, rows repeat the latest sample)
     vs rows deduplicated by sample t and matched to the store window.
     Count key: the |store bias - rows bias| the stage-4 check gates on (< 0.05).
  M4 store_off_domain / store_sanitize_dirty / store_refused_version per store.
Command (export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
    dev/audit/rounds/round10/D15/s1/intake.py --bundle <diag.json> [--perturb dedupe]
Perturbations: dedupe (M3 stage 4), unwrap (M3 wrapper), nonempty (M3 stage 2),
  boolkey (M2 credential rule), declare (M4 DOMAINS); each named finding's number moves.
Expected (baseline fe01b938f71b, live bundle 2026-10-14): ingest_fails_wrapped=6,
  ingest_fails_unwrapped=1, bias_delta_tail=0.115 +-0.001, bias_delta_by_t=0.000
  +-0.001; --perturb dedupe makes ingest's stage-4 use by-t rows: fails_unwrapped -> 0.
Machine: B11 macOS arm64 (counts only, contention-immune).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, copy, io, json, subprocess, sys, time
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.cwd()
for p in ("tests/hastub", "tests", "custom_components", "tools/replay"):
    sys.path.insert(0, str(ROOT / p))
PERTURB = ""
import debug_ingest as di  # tools/replay/debug_ingest.py
from heatpump_optimizer import store as store_mod
from heatpump_optimizer.accuracy import AccuracyTracker, AccuracySample

TAGS = [  # git for-each-ref refs/tags at fe01b938f71b (r10-repo), newest last
    ("v6.7.16", "2026-10-04T11:06:22+02:00"), ("v6.7.17", "2026-10-08T17:07:03+02:00"),
    ("v7.0.0", "2026-10-14T15:27:06+02:00")]


def tag_list():
    try:
        out = subprocess.run(["git", "for-each-ref", "--sort=creatordate",
                              "--format=%(refname:short) %(creatordate:iso-strict)", "refs/tags"],
                             capture_output=True, text=True, cwd=os.environ.get("HPO_TAG_REPO", ROOT)).stdout
        tags = [l.split() for l in out.splitlines() if l.startswith("v")]
        if tags:
            return [(a, b) for a, b in tags]
    except Exception:
        pass
    return TAGS


def m1(dbg):
    rows = dbg["cycle_rows"]
    ts = [datetime.fromisoformat(r["t"]) for r in rows]
    tags = [(n, datetime.fromisoformat(d)) for n, d in tag_list()]
    seg_start = ts[0]
    per = {}
    for i, t in enumerate(ts):
        if i and (t - ts[i - 1]) > timedelta(hours=1):
            seg_start = t
        # restart at seg_start: newest tag dated before it
        v = max(((d, n) for n, d in tags if d < seg_start), default=(None, "untagged"))[1]
        per[v] = per.get(v, 0) + 1
    gaps = sum(1 for a, b in zip(ts, ts[1:]) if b - a > timedelta(hours=1))
    for v, n in sorted(per.items()):
        print(f"RESULT rows_version_{v}={n} count")
    print(f"RESULT restart_gaps={gaps} count")
    print(f"RESULT manifest_version={dbg['manifest'].get('integration_version')} tag")


def m2(dbg):
    import replay as tests_replay  # tests/replay.py: LEAK_PROBES controls
    probes = tests_replay.leak_probes()
    print(f"RESULT leak_probe_controls_green={sum(ok for _n, ok, _d in probes)}/{len(probes)} count")
    exp = di.load_export()
    if PERTURB == "boolkey":  # credential-key rule skips a bool, as it skips None
        orig = exp._walk
        def _walk(node, path, found):
            n = len(found); orig(node, path, found)
            found[n:] = [f for f in found[n:] if not f.endswith("credential-named key carries a value")
                         or not isinstance(_get(dbg, f.split(":")[0]), bool)]
        exp._walk = _walk
    whole = exp.violations(dbg)
    cred = [v for v in whole if "credential-named key" in v]
    secretish = sum(1 for v in whole if "credential" in v or "decimals" in v)
    print(f"RESULT bundle_credential_key_violations={len(cred)} count")
    print(f"RESULT bundle_text_allowlist_violations={sum(1 for v in whole if 'text outside the allowlist' in v)} count")
    print(f"RESULT bundle_violations={len(whole)} count")
    for v in whole[:5]:
        print("  violation:", v[:120])
    planted = copy.deepcopy(dbg)
    planted.setdefault("replay", None)
    planted["stores"]["x_api_key"] = di.PLANTED_SECRET
    print(f"RESULT planted_arm_violations={len(exp.violations(planted)) - len(whole)} count")
    print(f"RESULT replay_half_present={int(bool(dbg.get('replay')))} bool")


def bias_by_t(dbg, tracker):
    seen = {}
    for r in dbg["cycle_rows"]:
        s = r.get("accuracy_sample")
        if s:
            seen[_st(s)] = s
    window = {s.when.isoformat() for s in tracker.samples}
    rt = AccuracyTracker()
    for t, s in seen.items():
        if t in window:
            rt.samples.append(AccuracySample(
                when=datetime.fromisoformat(t), predicted_temp=s.get("predicted_temp"),
                actual_temp=s.get("actual_temp"), predicted_power_kw=s.get("predicted_power_kw"),
                actual_power_kw=s.get("actual_power_kw"), outdoor_temp=s.get("outdoor_temp")))
    sub = AccuracyTracker()
    sub.samples.extend(x for x in tracker.samples if x.when.isoformat() in seen)
    return sub.temperature_bias(), rt.temperature_bias(), len(seen)


def _st(sample):
    return sample.get("t") or sample.get("when")


def _get(root, dotted):
    node = root
    for part in dotted.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def m3(download, dbg, perturb):
    def run(b):
        buf = io.StringIO()
        with redirect_stdout(buf):
            r = di.ingest(copy.deepcopy(b))
        return r, buf.getvalue()
    if perturb == "dedupe":
        # rows hand the store-window re-derivation each sample once, by its t
        seen, rows = set(), []
        for r in dbg["cycle_rows"]:
            s = r.get("accuracy_sample")
            if s and _st(s) not in seen:
                seen.add(_st(s)); rows.append(r)
        acc = next(k for k in dbg["stores"] if k.endswith("_accuracy"))
        d2 = copy.deepcopy(dbg)
        d2["cycle_rows"] = rows
        d2["manifest"]["cycles"] = len(rows)
        keep = {_st(r["accuracy_sample"]) for r in rows}
        d2["stores"][acc]["accuracy"]["samples"] = [
            s for s in d2["stores"][acc]["accuracy"]["samples"] if _st(s) in keep]
        dbg = d2
    if perturb == "unwrap":  # ingest unwraps the download's data.debug itself
        download = (download.get("data") or {}).get("debug") or download
    if perturb == "nonempty":  # stage 2 refuses an absent replay half
        orig = di.load_export
        def strict():
            e = orig(); v = e.violations
            e.violations = lambda p, conf=None: (["replay: absent"] if not p else v(p, conf))
            return e
        di.load_export = strict
    rw, _ = run(download)
    ru, out = run(dbg)
    print(f"RESULT replay_clean_passed_on_absent_replay={int('replay-clean' not in ru.fails and not dbg.get('replay'))} bool")
    print(f"RESULT ingest_fails_wrapped={len(rw.fails)} count")
    print(f"RESULT ingest_fails_unwrapped={len(ru.fails)} count  ({','.join(ru.fails)})")
    for line in out.splitlines():
        if "bias" in line and line.startswith("RESULT"):
            print("  ingest", line)
    acc = next(k for k in dbg["stores"] if k.endswith("_accuracy"))
    doc = dbg["stores"][acc]
    tracker = AccuracyTracker.from_dict(doc.get("accuracy", doc))
    rows = dbg["cycle_rows"]
    tail = [r for r in rows if r.get("accuracy_sample")][-len(tracker.samples):]
    distinct_tail = len({_st(r["accuracy_sample"]) for r in tail})
    print(f"RESULT tail_rows={len(tail)} count distinct_samples_in_tail={distinct_tail}")
    m = [l for l in out.splitlines() if l.startswith("RESULT accuracy_bias_delta=")]
    print(f"RESULT bias_delta_tail={m[0].split('=')[1].split()[0] if m else 'NA'} celsius")
    sb, rb, n = bias_by_t(dbg, tracker)
    d = abs(sb - rb) if sb is not None and rb is not None else None
    print(f"RESULT bias_delta_by_t={d if d is None else round(d, 4)} celsius (n_distinct_row_samples={n})")


def m4(dbg, perturb=""):
    off = dirty = refused = 0
    if perturb == "declare":  # declare the two writer fields DOMAINS omits
        D = store_mod.DOMAINS
        D["pump_duty"]["written/silent/0"] = D["away"]["active"]
        D["pump_duty"]["written/silent/1"] = D["pump_duty"]["written/mode/1"]
        D["snapshots"]["snapshots/#/learners/peak_tracker"] = "accuracy/peaks"
    for key, doc in dbg["stores"].items():
        name = store_mod._store_name(key)
        if store_mod._sanitize(doc) != doc:
            dirty += 1; print("  dirty:", key)
        bad = [(p, v) for p, k, d, v in store_mod.stored_fields(name, doc)
               if d is None or not store_mod.in_domain(d, v)]
        off += len(bad)
        for p, v in bad[:3]:
            # the path and the value's type only: a store document can hold a
            # credential, and this line goes to stdout and into evidence logs
            print(f"  off-domain {name}: {'/'.join(map(str, p))} ({type(v).__name__})")
    sv = dbg["manifest"].get("store_versions") or {}
    for key, ver in sv.items():
        name = store_mod._store_name(key)
        if not isinstance(ver, int) or ver < 1:
            refused += 1
    print(f"RESULT store_docs={len(dbg['stores'])} count")
    print(f"RESULT store_sanitize_dirty={dirty} count")
    print(f"RESULT store_off_domain_fields={off} count")
    print(f"RESULT store_refused_version={refused} count")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--perturb", choices=["", "dedupe", "declare", "boolkey", "unwrap", "nonempty"], default="")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    download = di.load_bundle(a.bundle)
    dbg = (download.get("data") or {}).get("debug") or download
    print(f"RESULT bundle_unwrapped={int(dbg is not download)} bool")
    global PERTURB
    PERTURB = a.perturb
    m1(dbg); m2(dbg); m3(download, dbg, a.perturb); m4(dbg, a.perturb)
    tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=NA")


if __name__ == "__main__":
    main()
