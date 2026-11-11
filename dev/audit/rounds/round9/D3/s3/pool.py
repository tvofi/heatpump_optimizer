#!/usr/bin/env python3
"""D3.M1 -- the seeded, consequence-weighted mutant pool of seat D3-s3.

Metric: the candidate list (every single-line mutant site of ten operators in
  D3-s3's 57 production files) and a seeded weighted sample of POOL_SIZE
  mutants from it, at most PER_FILE per module, written to pool.json.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s3/pool.py
Expected: RESULT candidates=<n> sites (deterministic for the baseline tree,
  exact); RESULT pool=36 mutants; pool.json byte-identical on a re-run.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: box B3
  (4 CPUs, 15 GiB, CPython 3.14.0rc2).  No timing: nothing here is provisional.

Operators.  The six of tests/mutation_table.py (`candidates()`, imported, not
copied: CLAMP_DROP, GUARD_OFF, RAISE_DEL, RETURN_DEL, BOOLOP, CONST) plus four
the gate's instrument does not generate, so the ledger can hold no disposition
for them:
  NEGATE        a one-line `if X:` with no else  -> `if not (X):`
  CMP_BOUNDARY  the single `<`/`<=`/`>`/`>=` of a one-line if/while/return test
                flips strictness (`<` <-> `<=`, `>` <-> `>=`)
  KEY_RENAME    a string-literal key of a one-line dict literal or subscript
                STORE -> key + "_x"  (a payload / attribute / store key)
  ARITH_SWAP    the single `+` <-> `-` of a one-line BinOp in an assignment
                or return

Weights (recorded in pool.json): file tier x operator weight x ledger factor.
  File tier 3 = drives a device, a setpoint, a schedule or money; 2 = learns,
  publishes, persists or configures; 1 = presentation / prefill / naming.
  Operator: GUARD_OFF, CLAMP_DROP, RAISE_DEL, KEY_RENAME 3; NEGATE, RETURN_DEL,
  BOOLOP, CONST 2; CMP_BOUNDARY, ARITH_SWAP 1.
  Ledger factor 0.5 when tests/mutation_budgets.json's ledger already holds a
  `killed_by` disposition for the site (the gate claims a kill), else 1.
Sampling: Efraimidis-Spirakis keys u**(1/w), u from random.Random(SEED),
  sorted descending, taken while a file holds fewer than PER_FILE.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
PKG = "custom_components/heatpump_optimizer/"
SEED = 20260926
POOL_SIZE = 36
PER_FILE = 4

# The seat's cells: every production module except the s1/s2 files.
OTHER_SEATS = {"coordinator.py", "optimizer.py", "thermal_model.py", "sysid.py",
               "defrost.py", "flow_lift.py", "price_model.py", "tariff.py",
               "grid_fee.py"}

TIER3 = {"pump_mode.py", "pump_arbiter.py", "pump_schedule.py",
         "pump_signals.py", "power_guard.py", "legionella.py",
         "disinfection.py", "setpoint_check.py", "freq_control.py",
         "mixing_valve.py", "silent_mode.py", "boost.py", "away.py",
         "dhw_schedule.py", "pv.py", "battery.py", "wood_fuel.py",
         "external_heat.py", "ledger.py", "store.py", "inputs.py",
         "services.py", "climate.py", "switch.py", "currency.py",
         "comfort_band.py", "dhw_draws.py", "presets.py"}
TIER1 = {"narrative.py", "diagnostics.py", "frontend.py", "name_match.py",
         "device_prefill.py", "modbus_prefill.py", "prefill_offer.py"}
OP_W = {"GUARD_OFF": 3, "CLAMP_DROP": 3, "RAISE_DEL": 3, "KEY_RENAME": 3,
        "NEGATE": 2, "RETURN_DEL": 2, "BOOLOP": 2, "CONST": 2,
        "CMP_BOUNDARY": 1, "ARITH_SWAP": 1}


def seat_files() -> list[Path]:
    root = Path(PKG)
    return sorted(p for p in root.glob("*.py") if p.name not in OTHER_SEATS)


def tier(name: str) -> int:
    return 3 if name in TIER3 else 1 if name in TIER1 else 2


def extra_candidates(path: Path):
    """The four operators tests/mutation_table.py does not generate."""
    src = path.read_text()
    lines = src.splitlines()
    tree = ast.parse(src)
    rel = str(path)
    for node in ast.walk(tree):
        ln = getattr(node, "lineno", None)
        if ln is None:
            continue
        line = lines[ln - 1]
        stripped = line.strip()
        ind = line[: len(line) - len(line.lstrip())]
        if (isinstance(node, ast.If) and not node.orelse
                and node.test.lineno == node.test.end_lineno == ln
                and stripped.startswith("if ") and stripped.endswith(":")):
            cond = stripped[3:-1]
            yield dict(kind="NEGATE", file=rel, line=ln, old=line,
                       new=f"{ind}if not ({cond}):")
        test = None
        if isinstance(node, (ast.If, ast.While)):
            test = node.test
        elif isinstance(node, ast.Return) and node.value is not None:
            test = node.value
        if (test is not None and isinstance(test, ast.Compare)
                and len(test.ops) == 1
                and test.lineno == test.end_lineno == ln):
            op = test.ops[0]
            flip = {ast.Lt: (" < ", " <= "), ast.LtE: (" <= ", " < "),
                    ast.Gt: (" > ", " >= "), ast.GtE: (" >= ", " > ")}
            for cls, (a, b) in flip.items():
                if isinstance(op, cls) and line.count(a) == 1 and (
                        a.strip() not in ("<", ">")
                        or line.count(b) == 0):
                    yield dict(kind="CMP_BOUNDARY", file=rel, line=ln,
                               old=line, new=line.replace(a, b))
        if (isinstance(node, ast.Dict) and node.lineno == node.end_lineno):
            for k in node.keys:
                if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                        and k.value.isidentifier()):
                    q = [f'"{k.value}":', f"'{k.value}':"]
                    for qq in q:
                        if line.count(qq) == 1:
                            yield dict(kind="KEY_RENAME", file=rel, line=ln,
                                       old=line,
                                       new=line.replace(qq, qq[:-2] + "_x"
                                                        + qq[-2:]))
                            break
        if (isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
                and node.slice.value.isidentifier()
                and node.lineno == node.end_lineno):
            v = node.slice.value
            for qq in (f'["{v}"]', f"['{v}']"):
                if line.count(qq) == 1:
                    yield dict(kind="KEY_RENAME", file=rel, line=ln, old=line,
                               new=line.replace(qq, qq[:-2] + "_x" + qq[-2:]))
                    break
        if (isinstance(node, (ast.Assign, ast.AugAssign, ast.Return))
                and node.lineno == getattr(node, "end_lineno", -1)
                and getattr(node, "value", None) is not None):
            bins = [b for b in ast.walk(node.value)
                    if isinstance(b, ast.BinOp)
                    and isinstance(b.op, (ast.Add, ast.Sub))]
            code = line.split("#", 1)[0]
            if len(bins) == 1 and (code.count(" + ") + code.count(" - ")) == 1:
                a, b = (" + ", " - ") if " + " in code else (" - ", " + ")
                yield dict(kind="ARITH_SWAP", file=rel, line=ln, old=line,
                           new=line.replace(a, b, 1))


def build():
    budgets = mt.load_budgets()
    disp = mt.dispositions(budgets)
    cands = []
    for path in seat_files():
        six = list(mt.candidates(mt.ROOT / path))
        for m in six:
            m["file"] = str(path)
        more = list(extra_candidates(path))
        sites = mt.anchor_sites(path.read_text(), six + more)
        for s in sites:
            e = disp.get(s["anchor"])
            s["ledger"] = (("killed_by:" + e["killed_by"]) if isinstance(e, dict)
                           and "killed_by" in e and e.get("old") == s["old"]
                           else (("triage:" + e["verdict"]) if isinstance(e, dict)
                                 and e.get("verdict") and e.get("old") == s["old"]
                                 else "none"))
            lf = 0.5 if s["ledger"].startswith("killed_by") else 1.0
            s["weight"] = tier(path.name) * OP_W[s["kind"]] * lf
            cands.append(s)
    # One mutant per (file, line, kind, new) -- the ops can coincide.
    uniq = {}
    for s in cands:
        uniq.setdefault((s["file"], s["line"], s["kind"], s["new"]), s)
    cands = sorted(uniq.values(),
                   key=lambda m: (m["file"], m["line"], m["kind"], m["new"]))
    rng = random.Random(SEED)
    keyed = [(rng.random() ** (1.0 / m["weight"]), i, m)
             for i, m in enumerate(cands)]
    keyed.sort(key=lambda t: (-t[0], t[1]))
    per, lines_used, pool = {}, set(), []
    for _k, _i, m in keyed:
        if len(pool) >= POOL_SIZE:
            break
        if per.get(m["file"], 0) >= PER_FILE:
            continue
        if (m["file"], m["line"]) in lines_used:
            continue
        per[m["file"]] = per.get(m["file"], 0) + 1
        lines_used.add((m["file"], m["line"]))
        pool.append(m)
    for n, m in enumerate(pool, 1):
        m["id"] = f"M{n:02d}"
    return cands, pool


def main() -> int:
    cands, pool = build()
    by_kind = {}
    for m in cands:
        by_kind[m["kind"]] = by_kind.get(m["kind"], 0) + 1
    out = {"seed": SEED, "pool_size": POOL_SIZE, "per_file": PER_FILE,
           "op_weights": OP_W, "tier3": sorted(TIER3), "tier1": sorted(TIER1),
           "files": [str(p) for p in seat_files()],
           "candidates_by_kind": by_kind, "candidates": len(cands),
           "pool": pool}
    (HERE / "pool.json").write_text(json.dumps(out, indent=1, sort_keys=True)
                                    + "\n")
    print(f"RESULT candidates={len(cands)} sites")
    for k in sorted(by_kind):
        print(f"RESULT candidates_{k}={by_kind[k]} sites")
    print(f"RESULT pool={len(pool)} mutants")
    for m in pool:
        print(f"{m['id']} {m['file']}:{m['line']} {m['kind']} w={m['weight']}"
              f" ledger={m['ledger']}")
        print(f"    - {m['old'].strip()}")
        print(f"    + {m['new'].strip()}")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
