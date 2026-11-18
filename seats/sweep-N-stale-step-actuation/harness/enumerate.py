"""N-stale-step-actuation sweep enumerator (round 11, SW2).

Seam: a function that reads the action cut once per solve -- the
attribute ``_current_action``, ``self._action()`` (legionella's view of
it) or ``get_current_action(...)``, directly or through getters that
read it and reach no write -- and reaches an actuator write
(a Home Assistant service call, an MQTT publish, or a package write
primitive) through the package's call graph.  Such a write carries the
value of the step the last solve cut, not of the step covering the write
instant, unless the path re-derives the step (``_step_index(plan, now)``).
Functions that also call ``_step_index`` are printed with step_keyed=1.

Usage:  python3 enumerate.py [ROOT]      (default custom_components/heatpump_optimizer)
        python3 enumerate.py --controls
"""
import ast
import pathlib
import sys
import tempfile

CUT_ATTRS = {"_current_action"}
CUT_CALLS = {"get_current_action"}
CUT_SELF_CALLS = {"_action"}
# Calls that leave the process toward a device or a Home Assistant entity.
WRITE_PRIMS = {"async_call", "async_publish", "publish", "select_option",
               "set_value", "write_setpoint", "_async_set_pump", "switch_supply",
               "_drive_switch", "turn_on", "turn_off"}


def _name(f):
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def scan(root):
    funcs = {}  # simple name -> list of records
    for path in sorted(pathlib.Path(root).rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            rec = {"file": str(path), "name": node.name, "line": node.lineno,
                   "cut": [], "calls": set(), "writes": False, "step": False}
            for sub in ast.walk(node):
                if sub is not node and isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    pass
                if isinstance(sub, ast.Attribute) and sub.attr in CUT_ATTRS and isinstance(sub.ctx, ast.Load):
                    rec["cut"].append(sub.lineno)
                if isinstance(sub, ast.Call):
                    n = _name(sub.func)
                    if n in CUT_CALLS or (n in CUT_SELF_CALLS and isinstance(sub.func, ast.Attribute)
                                          and isinstance(sub.func.value, ast.Name) and sub.func.value.id == "self"):
                        rec["cut"].append(sub.lineno)
                    if n in WRITE_PRIMS:
                        rec["writes"] = True
                    if n == "_step_index":
                        rec["step"] = True
                    if n:
                        rec["calls"].add(n)
            funcs.setdefault(node.name, []).append(rec)
    # fixed point: a name reaches a write if any definition of it writes or calls one that does
    reach = {n for n, rs in funcs.items() if any(r["writes"] for r in rs)}
    changed = True
    while changed:
        changed = False
        for n, rs in funcs.items():
            if n not in reach and any(r["calls"] & reach for r in rs):
                reach.add(n)
                changed = True
    # getters: a function that reads the cut and reaches no
    # write hands it to its caller (_commanded_power -> _command_frequency)
    getters = {n for n, rs in funcs.items()
               if n not in reach and any(r["cut"] for r in rs)}
    changed = True
    while changed:  # getters of getters (_commanded_split -> _commanded_power)
        changed = False
        for n, rs in funcs.items():
            if n not in reach and n not in getters and any(r["calls"] & getters for r in rs):
                getters.add(n)
                changed = True
    out = []
    for n, rs in funcs.items():
        for r in rs:
            via = r["calls"] & getters
            if via and not r["cut"]:
                r["cut"] = [r["line"]]
            if r["cut"] and (r["writes"] or r["calls"] & reach):
                out.append((r["file"], min(r["cut"]), n, int(r["step"])))
    return sorted(out)


def controls():
    repo = pathlib.Path(__file__).resolve().parents[6]
    real = scan(repo / "custom_components" / "heatpump_optimizer")
    names = {s[2] for s in real}
    want = {"_command_frequency", "async_publish_current_action", "async_track_cycle"}
    print(f"positive: finding sites {sorted(want)} found={sorted(want & names)}")
    clean = (
        "class A:\n"
        "    async def tick(self, now):\n"
        "        i = _step_index(self.plan, now)\n"
        "        await self.hass.services.async_call('number', 'set_value', {'value': self.plan.freq[i]})\n"
        "    def payload(self):\n"
        "        return dict(self._current_action)\n"
    )
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "m.py"
        p.write_text(clean)
        null = len(scan(d))
        p.write_text(clean.replace("        i = _step_index(self.plan, now)\n",
                                   "        i = self._current_action['i']\n"))
        pert = len(scan(d))
    print(f"null: clean fixture seams={null}")
    print(f"perturbation: one-line re-introduction seams={pert}")
    ok = want <= names and null == 0 and pert == 1
    print("controls", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--controls"]:
        sys.exit(controls())
    rows = scan(sys.argv[1] if len(sys.argv) > 1 else "custom_components/heatpump_optimizer")
    for f, ln, n, st in rows:
        print(f"{f}:{ln}\t{n}\tstep_keyed={st}")
    print(f"seams={len(rows)}")
