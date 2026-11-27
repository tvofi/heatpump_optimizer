"""Spike: per-span production lines executed, then rule-1 rows and their drive cost.

    PYTHONPATH=tests/hastub:tests python3 linereach.py record OUT.json     # one run of tests/features.py
    python3 linereach.py cost OUT.json                                     # rows by reaching parts; rule-1 drive cost
"""
import ast
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import case_select as cs  # noqa: E402

PROD = os.path.realpath("custom_components/heatpump_optimizer")
TOOL = sys.monitoring.COVERAGE_ID


class LineRec:
    def __init__(self):
        self.cur, self.lines = None, defaultdict(set)
        mon = sys.monitoring
        mon.use_tool_id(TOOL, "linereach")
        mon.register_callback(TOOL, mon.events.LINE, self._line)
        mon.set_events(TOOL, mon.events.LINE)

    def _line(self, code, line):
        f = code.co_filename
        if f.startswith(PROD) and self.cur is not None:
            self.lines[self.cur].add((os.path.basename(f), line))
        return sys.monitoring.DISABLE

    def begin(self, sid, stmts, ns):
        self.cur = sid
        print(f"@@SPAN {sid}", flush=True)
        sys.monitoring.restart_events()

    def end(self, ns):
        pass


def record(out):
    r = LineRec()
    rc = cs.run("tests/features.py", recorder=r)
    json.dump({"rc": rc, "lines": {k: sorted(v) for k, v in r.lines.items()}}, open(out, "w"))
    print(f"@@END rc={rc}")
    return rc


def _func_lines(path):
    """Lines inside a function body (else module-level: runs at import)."""
    inside = set()
    for n in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for b in n.body:
                inside.update(range(b.lineno, (b.end_lineno or b.lineno) + 1))
    return inside


def cost(rec_path):
    import swap_run
    parts = swap_run.partition()
    rec = json.load(open(rec_path))
    lines = {sid: {tuple(x) for x in v} for sid, v in rec["lines"].items()}
    by_line = defaultdict(set)
    for sid, v in lines.items():
        for x in v:
            by_line[x].add(sid)
    e = cs.entry(cs.load(), "tests/features.py")
    spans = e["spans"]
    sec = {sid: spans.get(sid, {}).get("seconds", 0.0) for sid in parts}
    head = float(os.environ["HEAD_S"])  # measured: case_select run with an empty plan
    needs = {sid: set(spans.get(sid, {}).get("needs", [])) for sid in parts}
    files_of = {sid: {os.path.basename(f) for f in spans.get(sid, {}).get("files", [])} for sid in parts}
    rows = []
    for p in Path("tests/mutation_ledger/killed_by").rglob("*.json"):
        try:
            row = json.load(open(p))
        except Exception:  # noqa: BLE001
            continue
        if row.get("killed_by") == "tests/features.py":
            rows.append(row)
    src_cache, fl_cache = {}, {}
    out = Counter()
    rule1, rule2, rule3 = [], [], []
    for row in rows:
        f = row["anchor"].split(":")[0]
        base = os.path.basename(f)
        if f not in src_cache:
            src_cache[f] = open(f, encoding="utf-8").read().split("\n")
            fl_cache[f] = _func_lines(f)
        cand = [i + 1 for i, t in enumerate(src_cache[f]) if t.rstrip("\n") == row["old"]]
        reach = set()
        for ln in cand:
            if ln in fl_cache[f]:
                reach |= by_line.get((base, ln), set())
            else:
                reach |= {sid for sid in parts if base in files_of[sid]}
        rparts = {parts[s] for s in reach if s in parts}
        out[min(len(rparts), 2) if cand else -1] += 1
        def drive(x):
            plan, todo = set(), [s for s in reach if parts.get(s) == x]
            while todo:
                s = todo.pop()
                if s in plan or parts.get(s) != x:
                    continue
                plan.add(s)
                todo += list(needs.get(s, ()))
            return plan, head + sum(sec[s] for s in plan)
        if len(rparts) == 1:
            x = next(iter(rparts))
            plan, c = drive(x)
            rule1.append((row["anchor"], x, len(plan), c))
        elif len(rparts) > 1:
            cs_ = sorted(drive(x)[1] for x in rparts)
            rule2.append((cs_[0], sum(cs_)))
        elif cand:
            rule3.append(sum(head + sum(sec[s] for s in parts if parts[s] == x) for x in set(parts.values())))
    print("rows", len(rows), "by reaching parts (0 none, 1 one, 2 several, -1 old text gone):", dict(out))
    tot = sum(c for *_, c in rule1)
    print(f"rule-1 rows {len(rule1)}; drive CPU-s (recorded span seconds, header included) {tot:.0f}; "
          f"mean {tot / max(1, len(rule1)):.1f}; max {max((c for *_, c in rule1), default=0):.1f}")
    print(f"rule-2 rows {len(rule2)}: first candidate {sum(a for a, _ in rule2):.0f} CPU-s, every candidate {sum(b for _, b in rule2):.0f}; "
          f"rule-3 rows {len(rule3)}: {sum(rule3):.0f} CPU-s; header {head:.1f} s; span seconds sum {sum(sec.values()):.1f}")
    print("rule-1 rows by part:", dict(Counter(x for _, x, _, _ in rule1)))
    json.dump(rule1, open(rec_path + ".rule1.json", "w"), indent=0)


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(record(a[1]) if a[0] == "record" else cost(a[1]))
