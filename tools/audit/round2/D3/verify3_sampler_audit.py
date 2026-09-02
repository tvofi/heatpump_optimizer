#!/usr/bin/env python3
"""Verifier seat 3, D3: does the 36-of-2254 sample generalise?

Metric: (a) the reproducibility of candidates.py's sample under its stated
seed; (b) the design's over/under-representation of each mutation kind and
each module-weight class relative to the 2254-site population; (c) the
post-stratified estimate of the population survivor rate and of the
population gap rate, using the sample's per-stratum rates and the
population's stratum sizes; (d) the restricted-killer-set survivor rate of
the finder's weighted sample against a uniform sample of the same
enumeration (tools/audit/round2/D3/../../../../../../tmp — see --uniform).

Run from the repository root:

    PYTHONPATH=tests/hastub .venv/bin/python \
      tools/audit/round2/D3/verify3_sampler_audit.py \
      [--uniform /tmp/verify-D3-3/sampler/uniform_results.json \
       --uniform-sample /tmp/verify-D3-3/sampler/uniform/sample.json]

Baseline c398fc84eec25fc44b60d74aae05b9a2da205884, 8-core Apple M1.
Every number here is a count or a ratio of counts: contention-immune.
Reads only; writes only what --out names.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

D3 = Path(__file__).resolve().parent
RESTRICTED = {"features.py", "entities.py", "open_meteo.py", "frontend.py"}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def post_stratified(pool_sizes: dict, sample_hits: dict, sample_n: dict) -> float:
    """Sum_s (N_s / N) * (hits_s / n_s); strata with n_s == 0 take the pooled rate."""
    total = sum(pool_sizes.values())
    pooled = sum(sample_hits.values()) / max(sum(sample_n.values()), 1)
    out = 0.0
    for s, N_s in pool_sizes.items():
        n_s = sample_n.get(s, 0)
        rate = (sample_hits.get(s, 0) / n_s) if n_s else pooled
        out += (N_s / total) * rate
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uniform", default="")
    ap.add_argument("--uniform-sample", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    pool = json.loads((D3 / "pool.json").read_text())
    samp = json.loads((D3 / "sample.json").read_text())
    pres = json.loads((D3 / "prescreen_results.json").read_text())
    rep = json.loads((D3 / "report.json").read_text())
    cls = {p["id"]: p["classification"] for p in rep["prescreened"]}
    sites = pool["sites"]
    MW = pool["module_weight"]

    surv = {m["id"]: (not pres[m["id"]]["killed_by"]) for m in samp}
    gap = {m["id"]: cls[m["id"]].startswith("gap candidate") for m in samp}
    # The same restricted killer set the uniform arm was run under, applied
    # to the weighted arm, so the two are comparable.
    surv_r = {
        m["id"]: not (
            set(x.replace("tests/", "") for x in pres[m["id"]]["killed_by"])
            & RESTRICTED
        )
        for m in samp
    }

    print("== reproducibility ==")
    print(f"RESULT pool_sites={pool['n_sites']} count")
    print(f"RESULT sampled={len(samp)} count")

    print("\n== representation: kind ==")
    tot_w = sum(s["weight"] for s in sites)
    for k in sorted(pool["by_kind"], key=lambda x: -pool["by_kind"][x]):
        n = pool["by_kind"][k]
        w = sum(s["weight"] for s in sites if s["kind"] == k)
        ms = [m for m in samp if m["kind"] == k]
        share_pop = n / len(sites)
        share_smp = len(ms) / len(samp)
        print(
            f"  {k:16s} pop {100*share_pop:5.1f}%  design-weight {100*w/tot_w:5.1f}%  "
            f"sampled {100*share_smp:5.1f}%  over-rep x{share_smp/share_pop:4.2f}  "
            f"survived {sum(surv[m['id']] for m in ms)}/{len(ms)}  "
            f"gaps {sum(gap[m['id']] for m in ms)}/{len(ms)}"
        )

    print("\n== representation: module weight class ==")
    for mw in sorted({MW.get(s["module"], 1) for s in sites}, reverse=True):
        sel = [s for s in sites if MW.get(s["module"], 1) == mw]
        w = sum(s["weight"] for s in sel)
        ms = [m for m in samp if MW.get(m["module"], 1) == mw]
        share_pop = len(sel) / len(sites)
        share_smp = len(ms) / len(samp)
        print(
            f"  modw={mw}  pop {100*share_pop:5.1f}%  design-weight {100*w/tot_w:5.1f}%  "
            f"sampled {100*share_smp:5.1f}%  over-rep x{share_smp/max(share_pop,1e-9):4.2f}  "
            f"survived {sum(surv[m['id']] for m in ms)}/{len(ms)}  "
            f"gaps {sum(gap[m['id']] for m in ms)}/{len(ms)}"
        )

    print("\n== raw sample rates ==")
    n = len(samp)
    for label, d in (("survivors", surv), ("gaps", gap)):
        k = sum(d.values())
        lo, hi = wilson(k, n)
        print(
            f"RESULT {label}_raw={k}/{n} = {100*k/n:.1f}%  "
            f"Wilson95 [{100*lo:.1f}%, {100*hi:.1f}%]  "
            f"population [{lo*len(sites):.0f}, {hi*len(sites):.0f}] of {len(sites)} sites"
        )

    print("\n== post-stratified population estimates ==")
    est = {}
    for strat_name, keyf in (
        ("kind", lambda s: s["kind"]),
        ("module_weight", lambda s: MW.get(s["module"], 1)),
    ):
        pool_sizes: dict = {}
        for s in sites:
            pool_sizes[keyf(s)] = pool_sizes.get(keyf(s), 0) + 1
        for label, d in (("survivor", surv), ("gap", gap)):
            hits: dict = {}
            ns: dict = {}
            for m in samp:
                key = keyf(m)
                ns[key] = ns.get(key, 0) + 1
                hits[key] = hits.get(key, 0) + (1 if d[m["id"]] else 0)
            p = post_stratified(pool_sizes, hits, ns)
            est[f"{label}_by_{strat_name}"] = p
            print(
                f"RESULT {label}_rate_poststrat_{strat_name}={p:.4f} fraction "
                f"({p*len(sites):.0f} of {len(sites)} sites)"
            )

    if args.uniform and Path(args.uniform).exists():
        uni = json.loads(Path(args.uniform).read_text())
        usamp = json.loads(Path(args.uniform_sample).read_text())
        u_surv = [m["id"] for m in usamp if not uni[m["id"]].get("killed_by")]
        w_surv = [m["id"] for m in samp if surv_r[m["id"]]]
        print("\n== weighted vs uniform, same enumeration, same killer set ==")
        print(f"  killer set K = {sorted(RESTRICTED)}")
        for label, k, nn in (
            ("weighted", len(w_surv), len(samp)),
            ("uniform", len(u_surv), len(usamp)),
        ):
            lo, hi = wilson(k, nn)
            print(
                f"RESULT {label}_restricted_survivors={k}/{nn} = {100*k/nn:.1f}%  "
                f"Wilson95 [{100*lo:.1f}%, {100*hi:.1f}%]"
            )
        d = len(w_surv) / len(samp) - len(u_surv) / len(usamp)
        print(f"RESULT weighting_bias={d:+.4f} fraction (weighted minus uniform)")
        print(f"  weighted survivors under K: {' '.join(w_surv)}")
        print(f"  uniform  survivors under K: {' '.join(u_surv)}")
        est["weighted_restricted"] = len(w_surv) / len(samp)
        est["uniform_restricted"] = len(u_surv) / len(usamp)
        est["weighting_bias"] = d

    print(f"\nRESULT load1={os.getloadavg()[0]:.2f}")
    if args.out:
        Path(args.out).write_text(json.dumps(est, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
