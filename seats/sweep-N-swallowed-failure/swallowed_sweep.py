#!/usr/bin/env python3
"""Round 11 class sweep, N-swallowed-failure: every except handler of the package whose caught
failure is recorded below WARNING or not at all, and does not leave the handler.

Universe: `tools/audit/enumerate.py d1-excepts` (every except handler in the package).
Seam (static, AST of the handler body, nested defs excluded):
  - no `raise` in the handler, and
  - the highest record it makes is below WARNING: direct `_LOGGER.<level>` calls, `log_held(...)`
    (a latched WARNING), `_LOGGER.exception`, and one level of package helpers the handler calls by
    name whose own body logs at WARNING+ (e.g. `self._weather_fetch_failed`) count as records.
Each seam carries: kind (broad/narrow), whether its try body awaits (an I/O operation), whether the
handler hands the error object on (`err` in a returned/assigned value), and the finder's executed
reading where an arm reached it: lifecycle injection (out/inj_*.jsonl: WARNING+ records added over
the fault-free control across the armed phases) or the local arm (m5_table.tsv).

Command: PYTHONPATH=tests/hastub python3 <this> [--null] [--perturb] [--json OUT]
  --null     a fixture module: a handler logging at WARNING, one re-raising, one returning the
             error, one narrow parse fallback -> seams that are not 'carried'/'parse' = 0
  --perturb  coordinator.py's `_LOGGER.debug("Could not persist ledger: %s", err)` read as
             `_LOGGER.warning(...)` (the D1-s3-05 one-line fix): seams 1 fewer
"""
import ast
import glob
import json
import os
import subprocess
import sys

ROOT = os.getcwd()
RANK = {}
D1 = os.path.join(ROOT, "dev/audit/rounds/round11/D1/s3")
LEVEL = {"debug": 10, "info": 20, "warning": 30, "warn": 30, "error": 40, "exception": 40, "critical": 50}
PERSIST = ("async_save", "async_save_if_changed", "async_delay_save", "persist", "_persist", "async_remove")
NULL_SRC = '''
import logging
_LOGGER = logging.getLogger(__name__)
async def a(store):
    try:
        await store.async_save({})
    except Exception as err:
        _LOGGER.warning("x %s", err)
async def b(store):
    try:
        await store.async_save({})
    except Exception:
        raise
def c(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
async def d(hass):
    try:
        await hass.services.async_call("a", "b", {})
    except Exception as err:
        return f"failed: {err}"
'''


def handlers():
    if "--null" in sys.argv:
        return [("fixture.py", n.lineno, "broad" if n.type is None or getattr(n.type, "id", "") == "Exception" else "narrow", "?")
                for n in ast.walk(ast.parse(NULL_SRC)) if isinstance(n, ast.ExceptHandler)]
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d1-excepts"], capture_output=True,
                         text=True, check=True, cwd=ROOT).stdout.split("\n")
    rows = []
    for line in out:
        if not line.strip():
            continue
        loc, kind, func = line.split()[:3]
        f, ln = loc.rsplit(":", 1)
        rows.append((f, int(ln), kind, func))
    return rows


def source(f):
    if f == "fixture.py":
        return NULL_SRC
    s = open(os.path.join(ROOT, f), encoding="utf-8").read()
    if "--perturb" in sys.argv and f.endswith("/coordinator.py"):
        old = '_LOGGER.debug("Could not persist ledger: %s", err)'
        assert old in s
        s = s.replace(old, '_LOGGER.warning("Could not persist ledger: %s", err)')
    return s


def walk_no_defs(nodes):
    stack = list(nodes)
    while stack:
        n = stack.pop()
        yield n
        for c in ast.iter_child_nodes(n):
            if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                stack.append(c)


def log_level(nodes):
    lv = 0
    for n in walk_no_defs(nodes):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in LEVEL and isinstance(f.value, ast.Name) \
                    and "LOG" in f.value.id.upper():
                lv = max(lv, LEVEL[f.attr])
            elif isinstance(f, ast.Name) and f.id == "log_held":
                lv = max(lv, 30)
    return lv


def called_names(nodes):
    out = set()
    for n in walk_no_defs(nodes):
        if isinstance(n, ast.Call):
            f = n.func
            out.add(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else "")
    return out


def _rank_keys(ids_funcs):
    """(file, func, rank of the handler's line within its function): the finder's arms ran at 92d38ecb,
    whose line numbers differ from this tree; the rank within a function is stable."""
    by = {}
    for hid, func in ids_funcs:
        f, ln = hid.rsplit(":", 1)
        by.setdefault((f, func), []).append(int(ln))
    out = {}
    for (f, func), lns in by.items():
        for k, ln in enumerate(sorted(lns)):
            out[f"{f}:{ln}"] = (f, func, k)
    return out


def finder_ranks():
    p = os.path.join(D1, "out", "m5_table.tsv")
    return _rank_keys([(c[0], c[2]) for c in (l.rstrip("\n").split("\t") for l in open(p))]) if os.path.exists(p) else {}


def lifecycle_readings():
    rec = {}
    for p in sorted(glob.glob(os.path.join(D1, "out", "inj_*.jsonl"))):
        for line in open(p):
            r = json.loads(line)
            armed = [ph for ph in r["phases"] if ph["phase"] != "refreshB2"]
            rec[RANK.get(r["id"], r["id"])] = {"fired": r["fired"], "added_warn": sum(ph["added_warn"] for ph in armed),
                            "added_any": sum(ph["added"] + ph["mark_logged"] for ph in armed),
                            "escaped": any((not ph["ok"] and ph["mark_escaped"]) or ph.get("task_mark") for ph in armed)}
    return rec


def local_readings():
    out = {}
    p = os.path.join(D1, "out", "m5_table.tsv")
    if os.path.exists(p):
        for line in open(p):
            c = line.rstrip("\n").split("\t")
            out[RANK.get(c[0], c[0])] = (c[3], c[4])
    return out


def main():
    trees, funcs = {}, {}
    seams = []
    global RANK
    RANK = finder_ranks()
    life, local = lifecycle_readings(), local_readings()
    rows = handlers()
    here = _rank_keys([(f"{f}:{ln}", func) for f, ln, _k, func in rows])
    for f, ln, kind, func in rows:
        if f not in trees:
            trees[f] = ast.parse(source(f))
            funcs[f] = {}
            for n in ast.walk(trees[f]):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs[f].setdefault(n.name, []).append(n)
        try_node, h = next((t, hh) for t in ast.walk(trees[f]) if isinstance(t, ast.Try)
                           for hh in t.handlers if hh.lineno == ln or (hh.body and hh.body[0].lineno == ln))
        if any(isinstance(n, ast.Raise) for n in walk_no_defs(h.body)):
            continue
        lv = log_level(h.body)
        for name in called_names(h.body):  # one level of package helpers
            for fn in funcs[f].get(name, []):
                lv = max(lv, log_level(fn.body))
        if lv >= 30:
            continue
        errname = h.name
        carried = bool(errname) and any(
            isinstance(n, (ast.Return, ast.Assign)) and errname in {x.id for x in ast.walk(n) if isinstance(x, ast.Name)}
            for n in walk_no_defs(h.body))
        awaits = any(isinstance(n, ast.Await) for n in walk_no_defs(try_node.body))
        tcalls = called_names(try_node.body)
        persist = bool(tcalls & set(PERSIST))
        hid = f"{f}:{ln}"
        seams.append({"id": hid, "kind": kind, "func": func, "record_level": lv, "carried": carried,
                      "awaits": awaits, "persist": persist,
                      "lifecycle": life.get(here.get(hid)), "local": local.get(here.get(hid))})
    for s in seams:
        lc = s["lifecycle"]
        print("SEAM", s["id"], s["kind"], s["func"], f"level={s['record_level']}", f"carried={s['carried']}",
              f"awaits={s['awaits']}", f"persist={s['persist']}",
              f"life={'-' if not lc else ('warn%d/any%d/fired%d' % (lc['added_warn'], lc['added_any'], lc['fired']))}",
              f"local={s['local'][1] if s['local'] else '-'}")
    print(f"RESULT handlers={len(rows)}")
    print(f"RESULT seams={len(seams)}")
    print(f"RESULT seams_broad={sum(s['kind'] == 'broad' for s in seams)}")
    print(f"RESULT seams_persist={sum(s['persist'] for s in seams)}")
    print(f"RESULT seams_not_carried_not_narrow_parse={sum(not s['carried'] and (s['kind'] == 'broad' or s['awaits']) for s in seams)}")
    if "--json" in sys.argv:
        json.dump(seams, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
