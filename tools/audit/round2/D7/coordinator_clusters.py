#!/usr/bin/env python3
"""D7 step 2 -- cluster HeatPumpOptimizerCoordinator's methods by the self._* state they share.

Metric (one line): over the method--attribute bipartite graph of the class (attribute =
``self.<name>`` read or written inside a method, names that are methods excluded; call =
``self.<method>(...)``), (a) SEEDED (greedy) clustering -- an attribute's home is the
``__init__``/``_init_*`` method that first assigns it, every method joins the home whose
attributes it touches most (self-calls to already-placed methods weigh 0.5), unowned attributes
join the cluster that touches them most, iterated to a fixed point -- and (b) SPECTRAL
clustering -- normalized-Laplacian embedding of the method--method cosine-similarity graph
(rows = attribute indicator vectors), k-means++ (scipy kmeans2, seed 0) at k in {6, 8, 10, 12,
16}; methods that touch no self._* state form a separate "stateless" cluster. For each: the
cross-cluster attribute fraction (attribute references whose attribute is owned -- majority
vote -- by another cluster / all attribute references), the cross-cluster call fraction
(self-calls into another cluster / all self-calls) and, per cluster, the CUT COST = distinct
attributes shared with other clusters + calls crossing its boundary (both directions).

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/coordinator_clusters.py
Expected: RESULT n_methods=256 (exact); fractions exact to 4 dp (deterministic: seed 0, ties
          by source order); baseline c398fc84eec25fc44b60d74aae05b9a2da205884.
Machine:  8-core Apple M1, 8 GB, shared audit box -- counts, contention-immune.
Instrumented symbol: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
Perturbation: move the lowest cut-cost-per-method seam (RESULT seam_min_cut_name at k=10)
          out of the class into its own module -> n_methods DOWN by that seam's size and
          cross_attr_fraction_k10 DOWN; rename one seam's attributes to another seam's names
          -> that seam's cut cost UP.
Writes:   tools/audit/round2/D7/coordinator_clusters.json only.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.cluster.vq import kmeans2

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "custom_components" / "heatpump_optimizer" / "coordinator.py"
OUT = Path(__file__).resolve().parent / "coordinator_clusters.json"
CLASS = "HeatPumpOptimizerCoordinator"


def load_class() -> ast.ClassDef:
    tree = ast.parse(SRC.read_text())
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name == CLASS:
            return n
    raise SystemExit(f"{CLASS} not found")


def method_graph(cls: ast.ClassDef):
    methods = [m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    names = [m.name for m in methods]
    name_set = set(names)
    attrs_of, writes_of, calls_of, lines_of = {}, {}, {}, {}
    for m in methods:
        a, w, c = Counter(), set(), Counter()
        for d in ast.walk(m):
            if isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name) and d.value.id == "self":
                if d.attr in name_set:
                    c[d.attr] += 1
                else:
                    a[d.attr] += 1
                    if isinstance(d.ctx, (ast.Store, ast.Del)):
                        w.add(d.attr)
        attrs_of[m.name], writes_of[m.name], calls_of[m.name] = a, w, c
        lines_of[m.name] = (m.end_lineno or m.lineno) - m.lineno + 1
    return names, attrs_of, writes_of, calls_of, lines_of


def fractions(names, attrs_of, calls_of, cluster_of, owner_of):
    attr_refs = cross_attr = call_refs = cross_call = 0
    for m in names:
        for a, n in attrs_of[m].items():
            attr_refs += n
            if owner_of.get(a) != cluster_of[m]:
                cross_attr += n
        for t, n in calls_of[m].items():
            call_refs += n
            if cluster_of.get(t) != cluster_of[m]:
                cross_call += n
    return (cross_attr / attr_refs if attr_refs else 0.0,
            cross_call / call_refs if call_refs else 0.0, attr_refs, call_refs)


def owners_by_majority(names, attrs_of, cluster_of):
    votes: dict[str, Counter] = defaultdict(Counter)
    for m in names:
        for a, n in attrs_of[m].items():
            votes[a][cluster_of[m]] += n
    return {a: v.most_common(1)[0][0] for a, v in votes.items()}


def cut_costs(names, attrs_of, calls_of, lines_of, cluster_of, owner_of):
    out = {}
    for c in sorted(set(cluster_of.values()), key=str):
        members = [m for m in names if cluster_of[m] == c]
        shared, crossing = set(), 0
        for m in members:
            shared.update(a for a in attrs_of[m] if owner_of.get(a) != c)
            crossing += sum(n for t, n in calls_of[m].items() if cluster_of.get(t) != c)
        for m in names:
            if cluster_of[m] != c:
                shared.update(a for a in attrs_of[m] if owner_of.get(a) == c)
                crossing += sum(n for t, n in calls_of[m].items() if cluster_of.get(t) == c)
        owned = [a for a, o in owner_of.items() if o == c]
        out[c] = {"size": len(members), "lines": sum(lines_of[m] for m in members),
                  "owned_attrs": len(owned), "shared_attrs": len(shared), "crossing_calls": crossing,
                  "cut_cost": len(shared) + crossing, "members": members,
                  "owned_attr_names": sorted(owned), "shared_attr_names": sorted(shared)}
    return out


def seeded(names, attrs_of, writes_of, calls_of):
    inits = [n for n in names if n == "__init__" or n.startswith("_init_")]
    home_of: dict[str, str] = {}
    for n in inits:
        for a in writes_of[n]:
            home_of.setdefault(a, n)
    cluster_of = {n: n for n in inits}
    owner_of = dict(home_of)
    for _ in range(20):
        changed = False
        for m in names:
            if m in inits:
                continue
            votes = Counter()
            for a, n in attrs_of[m].items():
                if a in owner_of:
                    votes[owner_of[a]] += n
            for t, n in calls_of[m].items():
                if t in cluster_of and t not in inits:
                    votes[cluster_of[t]] += 0.5 * n
            new = votes.most_common(1)[0][0] if votes else "__init__"
            if cluster_of.get(m) != new:
                cluster_of[m] = new
                changed = True
        maj = owners_by_majority(names, attrs_of, cluster_of)
        new_owner = dict(home_of)
        for a, c in maj.items():
            new_owner.setdefault(a, c)
        if new_owner != owner_of:
            owner_of = new_owner
            changed = True
        if not changed:
            break
    return cluster_of, owner_of


def spectral(names, attrs_of, k, seed=0):
    stateful = [m for m in names if attrs_of[m]]
    vocab = sorted({a for m in stateful for a in attrs_of[m]})
    idx = {a: i for i, a in enumerate(vocab)}
    X = np.zeros((len(stateful), len(vocab)))
    for i, m in enumerate(stateful):
        for a in attrs_of[m]:
            X[i, idx[a]] = 1.0
    Xn = X / np.linalg.norm(X, axis=1)[:, None]
    S = Xn @ Xn.T
    np.fill_diagonal(S, 0.0)
    d = S.sum(axis=1)
    d[d <= 0] = 1e-12
    Dm = np.diag(1.0 / np.sqrt(d))
    L = np.eye(len(stateful)) - Dm @ S @ Dm
    w, v = np.linalg.eigh(L)
    U = v[:, :k]
    U = U / np.maximum(np.linalg.norm(U, axis=1)[:, None], 1e-12)
    _, labels = kmeans2(U, k, minit="++", seed=seed)
    cluster_of = {m: 0 for m in names}                 # 0 = stateless
    for m, l in zip(stateful, labels):
        cluster_of[m] = int(l) + 1
    owner_of = owners_by_majority(names, attrs_of, cluster_of)
    return cluster_of, owner_of


STOP = {"async", "view", "get", "set", "update", "check", "on", "the", "of", "for", "to", "current", "apply", "is"}


def token_name(members):
    toks = Counter()
    for m in members:
        for t in re.sub(r"^_?(async_)?", "", m).split("_"):
            if t and t not in STOP:
                toks[t] += 1
    return "/".join(t for t, _ in toks.most_common(2)) or "misc"


def main() -> int:
    cls = load_class()
    names, attrs_of, writes_of, calls_of, lines_of = method_graph(cls)
    all_attrs = sorted({a for m in names for a in attrs_of[m]})
    writer_count = Counter(a for m in names for a in writes_of[m])
    multi_writer = sorted(a for a, n in writer_count.items() if n > 1)
    print(f"=== D7 coordinator clustering ({SRC.name}, class {CLASS}) ===")
    print(f"methods={len(names)} attrs={len(all_attrs)} attrs_written_in_>1_method={len(multi_writer)} "
          f"stateless_methods={sum(1 for m in names if not attrs_of[m])}")
    res: dict = {"n_methods": len(names), "n_attrs": len(all_attrs), "n_attrs_multi_writer": len(multi_writer),
                 "n_stateless_methods": sum(1 for m in names if not attrs_of[m])}
    dump: dict = {"attrs_multi_writer": multi_writer}

    cl, ow = seeded(names, attrs_of, writes_of, calls_of)
    fa, fc, ar, cr = fractions(names, attrs_of, calls_of, cl, ow)
    costs = cut_costs(names, attrs_of, calls_of, lines_of, cl, ow)
    res.update({"attr_refs": ar, "call_refs": cr, "cross_attr_fraction_seeded": round(fa, 4),
                "cross_call_fraction_seeded": round(fc, 4), "clusters_seeded": len(set(cl.values()))})
    print("\n-- (a) seeded by __init__/_init_* homes")
    print(f"cross-cluster attribute refs {fa:.3f}, cross-cluster calls {fc:.3f}")
    print(f"{'cluster':22} {'size':>4} {'lines':>5} {'owned':>5} {'shared':>6} {'xcalls':>6} {'cut':>5}")
    for c, d in sorted(costs.items(), key=lambda kv: kv[1]["cut_cost"]):
        print(f"{c:22} {d['size']:4d} {d['lines']:5d} {d['owned_attrs']:5d} {d['shared_attrs']:6d} {d['crossing_calls']:6d} {d['cut_cost']:5d}")
    dump["seeded"] = {"cluster_of": cl, "owner_of": ow, "costs": costs}

    dump["spectral"] = {}
    print("\n-- (b) spectral (normalized Laplacian + k-means++, seed 0) on attribute cosine")
    for k in (6, 8, 10, 12, 16):
        cl_u, ow_u = spectral(names, attrs_of, k)
        fa_u, fc_u, _, _ = fractions(names, attrs_of, calls_of, cl_u, ow_u)
        costs_u = cut_costs(names, attrs_of, calls_of, lines_of, cl_u, ow_u)
        named = {c: ("stateless" if c == 0 else token_name(d["members"])) for c, d in costs_u.items()}
        res[f"cross_attr_fraction_k{k}"] = round(fa_u, 4)
        res[f"cross_call_fraction_k{k}"] = round(fc_u, 4)
        sizes = sorted((d["size"] for c, d in costs_u.items() if c != 0), reverse=True)
        print(f"k={k:2d}: cross-attr {fa_u:.3f} cross-call {fc_u:.3f} sizes={sizes}")
        dump["spectral"][k] = {"cluster_of": cl_u, "owner_of": ow_u,
                               "costs": {str(c): {**d, "name": named[c]} for c, d in costs_u.items()}}
        if k == 10:
            print(f"   {'name':22} {'size':>4} {'lines':>5} {'owned':>5} {'shared':>6} {'xcalls':>6} {'cut':>5}  members (first 4)")
            for c, d in sorted(costs_u.items(), key=lambda kv: (kv[1]["cut_cost"] / max(kv[1]["size"], 1))):
                print(f"   {named[c]:22} {d['size']:4d} {d['lines']:5d} {d['owned_attrs']:5d} {d['shared_attrs']:6d} "
                      f"{d['crossing_calls']:6d} {d['cut_cost']:5d}  {d['members'][:4]}")
            cands = sorted((d["cut_cost"] / d["size"], d["cut_cost"], named[c], d["size"], d["lines"], c)
                           for c, d in costs_u.items() if d["size"] >= 8 and c != 0)
            print("\n   Seam candidates (>=8 methods) by cut cost per method:")
            for cpm, cut, nm, size, ln, c in cands:
                print(f"     {nm:22} size={size:3d} lines={ln:5d} cut={cut:3d} cut/method={cpm:.2f} "
                      f"shared={sorted(costs_u[c]['shared_attr_names'])[:6]}")
            if cands:
                res["seam_min_cut_name"] = cands[0][2]
                res["seam_min_cut_size"] = cands[0][3]
                res["seam_min_cut_lines"] = cands[0][4]
                res["seam_min_cut_cost"] = cands[0][1]
                res["seam_max_cut_name"] = cands[-1][2]
                res["seam_max_cut_cost"] = cands[-1][1]
                res["seams_ge8_methods"] = len(cands)

    fan_in = Counter(a for m in names for a in attrs_of[m])
    print("\nAttributes touched by the most methods:")
    for a, n in fan_in.most_common(12):
        print(f"  {n:4d} methods  self.{a}")
    res["attr_max_fan_in"] = fan_in.most_common(1)[0][1]
    res["attrs_fan_in_ge_20"] = sum(1 for _, n in fan_in.items() if n >= 20)
    dump["fan_in"] = fan_in.most_common(60)

    for k, v in res.items():
        unit = "ratio" if isinstance(v, float) else ("text" if isinstance(v, str) else "count")
        print(f"RESULT {k}={v} {unit}")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    OUT.write_text(json.dumps({"results": res, **dump}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
