#!/usr/bin/env python3
"""Round 11 class sweep, N-structure-blind: every structural ratchet row, probed for a
code shape it cannot see.

Seam universe: every row of tests/structure_budgets.json (18, the PR-gate ratchet) plus the
properties the round's findings showed no row holds (unused package imports, module size
outside the class, dead state inside live code). The 25 archscore.* rows of
tests/ci_budgets.json are measured under every plant as the second reader: a respelling one of
them catches is `guarded` by that CI row.

For each probe: a CANONICAL plant (the gated property in the shape the row keys on; the row
must move -- the row is live and the plant is real) and a RESPELLED plant (the same property,
another spelling). A row is an instance when the canonical plant moves it and the respelled
one moves neither it nor any CI row.

Every plant is applied to a temporary copy of custom_components/heatpump_optimizer; the tree
is never written. Run from the repository root:

    PYTHONPATH=tests/hastub python3 <this> [--only P3,P4] [--null] [--json OUT]

--null: the empty plant (a comment) on both arms: every row reads delta 0.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path.cwd()
PKG_REL = "custom_components/heatpump_optimizer"
sys.path.insert(0, str(REPO / "tools" / "audit"))

COORD = 'coordinator: "HeatPumpOptimizerCoordinator"'
BIG_IF = "".join(f"    if x == {i}:\n        y = {i}\n" for i in range(50))
MOD_IF = "_d7x = 0\n_d7y = 0\n" + "".join(f"if _d7x == {i}:\n    _d7y = {i}\n" for i in range(50)) + "assert _d7y is not None\n"
LONG = "".join(f"    x{i} = {i}\n" for i in range(250))
LONG_NESTED = "".join(f"        x{i} = {i}\n" for i in range(250))

# id: (rows, file, canonical append, respelled append, finding or None)
PROBES = {
    "P1-private-reach": (["coordinator_private_reach"], "ledger.py",
        f"\n\ndef _d7r({COORD}):\n    return coordinator._mode\n\n\nassert _d7r\n",
        f"\n\ndef _d7r({COORD}):\n    return getattr(coordinator, \"_mo\" + \"de\")\n\n\nassert _d7r\n", None),
    "P2-attr-writers": (["coordinator_attrs", "coordinator_multiassigned_attrs"], "ledger.py",
        f"\n\ndef _d7w1({COORD}):\n    coordinator._d7new = 1\n\n\ndef _d7w2({COORD}):\n    coordinator._d7new = 2\n\n\nassert _d7w1 and _d7w2\n",
        f"\n\ndef _d7w1({COORD}):\n    vars(coordinator)[\"_d7new\"] = 1\n\n\ndef _d7w2({COORD}):\n"
        f"    coordinator.__dict__[\"_d7new\"] = 2\n\n\nassert _d7w1 and _d7w2\n", None),
    "P3-cc-module-level": (["max_cc", "functions_cc_over_15", "functions_cc_over_25"], "ledger.py",
        f"\n\ndef _d7cc(x):\n    y = 0\n{BIG_IF}    return y\n\n\nassert _d7cc(0) == 0\n",
        f"\n\n{MOD_IF}", None),
    "P4-dead-mutual-pair": (["dead_top_level_symbols"], "ledger.py",
        "\n\ndef _d7a():\n    return 1\n\n\ndef _d7b():\n    return 2\n",
        "\n\ndef _d7a():\n    return _d7b()\n\n\ndef _d7b():\n    return _d7a()\n", None),
    "P5-import-cycle-absolute": (["import_cycle_modules"], "const.py",
        "\nfrom . import ledger as _d7ledger  # noqa: E402\n",
        "\nfrom custom_components.heatpump_optimizer import ledger as _d7ledger  # noqa: E402\n", None),
    "P6-long-nested": (["max_method_loc", "methods_over_150", "methods_over_200"], "ledger.py",
        f"\n\ndef _d7long():\n{LONG}    return x0\n\n\nassert _d7long\n",
        f"\n\ndef _d7outer():\n    def _d7long():\n{LONG_NESTED}        return x0\n    return _d7long()\n\n\nassert _d7outer\n",
        None),
    "P7-name-kept": (["dead_methods", "name_kept_members"], "ledger.py",
        "\n\nclass _D7A:\n    def d7twin(self):\n        return 1\n\n\nassert _D7A\n",
        "\n\nclass _D7A:\n    def d7twin(self):\n        return 1\n\n\nclass _D7B:\n    def d7twin(self):\n"
        "        return 2\n\n\ndef _d7u(thing):\n    return thing.d7twin()\n\n\nassert _d7u and _D7A and _D7B\n", None),
}
# the judged shapes, recounted through the finder's own census (m1) -- positive control
JUDGED = {
    "D7-s1-01": ("const_modules_over_50", "const-respell"),
    "D7-s1-02": ("duplication_copies", "clone-same-fn"),
    "D7-s1-03": ("(no row) unused package imports", "unused-import"),
    "D7-s1-04": ("class_excess_loc / (no row) module size", "module-growth"),
}


def load_structure(root: Path):
    spec = importlib.util.spec_from_file_location("sw_structure", REPO / "tests" / "structure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO_ROOT = root
    mod.PACKAGE_DIR = root / PKG_REL
    return mod


def rows(root: Path) -> dict:
    S = load_structure(root)
    m = S.measure()["metrics"]
    from archscore import vector
    v = vector.measure(root)
    out = {k: m[k] for k in m}
    out.update({f"archscore.{k}": x for k, x in v.items() if not k.startswith("_") or k == "_inlined_bases"})
    return out


def planted(append: str | None, file: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="sw-blind-"))
    shutil.copytree(REPO / PKG_REL, tmp / PKG_REL, ignore=shutil.ignore_patterns("__pycache__"))
    if append is not None:
        p = tmp / PKG_REL / file
        p.write_text(p.read_text().rstrip("\n") + "\n" + append)
    return tmp


def delta(a: dict, b: dict) -> dict:
    return {k: (b.get(k), a.get(k)) for k in sorted(set(a) | set(b))
            if isinstance(a.get(k), (int, float)) and a.get(k) != b.get(k)}


def main() -> int:
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    null = "--null" in sys.argv
    base_root = planted(None, "")
    base = rows(base_root)
    print("BASE", json.dumps({k: base[k] for k in sorted(base) if isinstance(base[k], (int, float))}))
    report = {}
    for pid, (rws, file, canon, resp, _f) in PROBES.items():
        if only and pid.split("-")[0] not in only:
            continue
        if null:
            canon = resp = "\n# d7 null plant\n"
        dc = delta(base, rows(planted(canon, file)))
        dr = delta(base, rows(planted(resp, file)))
        canon_moves = [r for r in rws if r in dc]
        resp_moves = [r for r in rws if r in dr]
        ci_moves = sorted(k for k in dr if k.startswith("archscore."))
        verdict = ("null" if null else
                   "row-dead" if not canon_moves else
                   "guarded" if resp_moves or ci_moves else "BLIND")
        report[pid] = {"rows": rws, "file": file, "canonical_delta": dc, "respelled_delta": dr,
                       "verdict": verdict}
        print(f"PROBE {pid} rows={','.join(rws)} canonical_moves={canon_moves} respelled_moves={resp_moves} "
              f"ci_rows_moved_by_respell={ci_moves} -> {verdict}")
        print(f"  canonical: {json.dumps(dc)}")
        print(f"  respelled: {json.dumps(dr)}")
    blind = sum(1 for r in report.values() if r["verdict"] == "BLIND")
    print(f"RESULT probes={len(report)}")
    print(f"RESULT blind={blind}")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
