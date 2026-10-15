"""N-future-clamp enumerator (round 10, D14 steps 3-4).

Seam: a stored instant leaf, in a QuarantiningStore of lead L_host, whose
writer is a store of lead L_origin > L_host (the leaf reached through a
DOMAINS alias, i.e. the host embeds another store's payload). Such a leaf
may legitimately lie up to L_origin ahead, and the host's _bound_instants
rewrites it to now on every load (D1-s2-01's mechanism).

Lists EVERY instant leaf of every store (the seam universe) with host/origin
lead, and flags the mismatched ones.
  python3 future_clamp_seams.py            # live tree
  python3 future_clamp_seams.py --perturb  # snapshots store given 24 h (expect flagged 0)
  python3 future_clamp_seams.py --null     # clean fixture (expect 0)
  python3 future_clamp_seams.py --reintro  # clean fixture + one-line embed (expect 1)
Leads are read by AST from every QuarantiningStore(...) construction, so a
store added later is enumerated without editing this file.
"""
import ast, math, pathlib, sys
from datetime import timedelta

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
PKG = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "tests" / "hastub")); sys.path.insert(0, str(ROOT))


def leads():
    """{store key suffix: lead hours (inf for None)} from the AST."""
    from custom_components.heatpump_optimizer import accuracy, boost, manual_plan, const
    env = {"timedelta": timedelta, "max": max, "LEAD_BUCKETS": accuracy.LEAD_BUCKETS,
           "_MAX_LEAD": boost._MAX_LEAD, "None": None,
           "MANUAL_PLAN_WINDOW_HOURS": getattr(const, "MANUAL_PLAN_WINDOW_HOURS",
                                               getattr(manual_plan, "MANUAL_PLAN_WINDOW_HOURS", None))}
    out = {}
    for f in sorted(PKG.glob("*.py")):
        for n in ast.walk(ast.parse(f.read_text())):
            if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "QuarantiningStore":
                key = next((a for a in n.args if isinstance(a, ast.JoinedStr)), None)
                suffix = key.values[-1].value.lstrip("_") if key else "?"
                kw = {k.arg: k.value for k in n.keywords}
                if "lead" not in kw:
                    h = 0.0
                else:
                    v = eval(compile(ast.Expression(kw["lead"]), str(f), "eval"), env)
                    h = math.inf if v is None else v.total_seconds() / 3600
                out[suffix] = (h, f"{f.name}:{n.lineno}")
    return out


def domains():
    from custom_components.heatpump_optimizer import store
    return store.DOMAINS, store.Domain


def instant_leaves(doms, Domain, name, prefix="", origin=None, seen=()):
    """Yield (path, origin store) for every instant leaf of store ``name``, aliases resolved."""
    for path, d in doms[name].items():
        if isinstance(d, Domain):
            if d.kind == "instant":
                yield prefix + path, origin or name
        elif isinstance(d, str):
            tgt, _, sub = d.partition("/")
            if tgt in seen:
                continue
            for p, o in instant_leaves(doms, Domain, tgt, "", None, seen + (name,)):
                if p == sub or p.startswith(sub + "/") or not sub:
                    rest = p[len(sub):].lstrip("/") if sub else p
                    yield prefix + path + ("/" + rest if rest else ""), o if o != tgt else tgt


def run(doms, Domain, L, label):
    keymap = {"dhw_legionella": "dhw_legionella", "snapshots": "snapshots", "debug": "debug"}
    flagged, total = [], 0
    for name in doms:
        host = L.get(keymap.get(name, name), (0.0, "?"))
        for path, origin in instant_leaves(doms, Domain, name):
            total += 1
            o = L.get(origin, (0.0, "?"))
            bad = o[0] > host[0]
            print(f"SEAM {name}:{path} host_lead={host[0]:g}h origin={origin} origin_lead={o[0]:g}h"
                  f" site={host[1]}{'  FLAG' if bad else ''}")
            if bad:
                flagged.append((name, path, origin))
    hosts = sorted({(f[0], f[2]) for f in flagged})
    print(f"RESULT {label} instant_leaves={total} flagged_leaves={len(flagged)} flagged_host_origin_pairs={len(hosts)} {hosts}")
    return hosts


def fixture(reintro):
    from custom_components.heatpump_optimizer.store import Domain
    at = Domain("instant")
    doms = {"ledgerx": {"t": at}, "expiry": {"until": at},
            "ring": {"rows/#/t": at, "rows/#/ledger": "ledgerx"}}
    L = {"ledgerx": (0.0, "fx"), "expiry": (24.0, "fx"), "ring": (0.0, "fx")}
    if reintro:
        doms["ring"]["rows/#/expiry"] = "expiry"  # the one-line re-introduction
    return doms, Domain, L


if __name__ == "__main__":
    if "--null" in sys.argv or "--reintro" in sys.argv:
        d, D, L = fixture("--reintro" in sys.argv)
        run(d, D, L, "reintro" if "--reintro" in sys.argv else "null")
    else:
        d, D = domains(); L = leads()
        for k, v in sorted(L.items()):
            print(f"STORE {k} lead={v[0]:g}h {v[1]}")
        if "--perturb" in sys.argv:
            L["snapshots"] = (24.0, L["snapshots"][1])
        run(d, D, L, "perturb" if "--perturb" in sys.argv else "live")
