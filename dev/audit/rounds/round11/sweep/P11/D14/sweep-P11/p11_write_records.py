#!/usr/bin/env python3
"""Round-11 class sweep P11 (D14 steps 3-4): every write the package records as made.

Class P11: the only oracle for an external counterpart is a test double written
from what the code needed. D16-s1-05 is the instance this round: Home Assistant's
entity service call SKIPS an entity whose state is unavailable (no error raised;
homeassistant/helpers/service.py entity_service_call drops entities that are not
`available`), while tests/harness.py:FakeServices.async_call records and dispatches
every call. So a production write path that books "written" after the call agrees
with the double and disagrees with Home Assistant.

SEAM: a function that performs a write -- `<x>.services.async_call(...)`,
`<x>.async_call(...)`, or a package function that (transitively) does, e.g.
`write_setpoint`, `switch_supply`, `_send`, `_write` -- and AFTER it, in the same
function, records the write: an assignment/augassign to an attribute or subscript,
or a call named note_command / append / _record_write / _report_write.
Writers are `services.async_call` and the package functions that call it directly or
through up to two wrappers (write_setpoint -> write_setpoint_c -> _valve_write_problem).
FLAG: the function's code (comments and docstring excluded) never tests the target's
availability: no "unavailable" / STATE_UNAVAILABLE / `.available`, and no
`inputs.number_reading(...)` (None for a non-numeric state) with an `is None` test
before the write.

  python3 p11_write_records.py [--pkg DIR] [--null] [--perturb]
--null: a clean fixture (the recorder checks availability first) -> flagged 0.
--perturb: the same fixture with the one availability line removed -> flagged 1.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
import tempfile
from pathlib import Path

RECORD_CALLS = {"note_command", "append", "_record_write", "_report_write"}
AVAIL = re.compile(r"unavailable|STATE_UNAVAILABLE|\.available\b")
READER = re.compile(r"number_reading\(")  # inputs.number_reading: None for a non-numeric (unavailable) state


def name_of(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def functions(tree):
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((prefix + ch.name, ch))
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, prefix + ch.name + ".")
            else:
                walk(ch, prefix)
    walk(tree, "")
    return out


def own(fn):
    stack, out = list(ast.iter_child_nodes(fn)), []
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        out.append(n)
        stack.extend(ast.iter_child_nodes(n))
    return out


def scan(pkg: Path):
    mods = {p: p.read_text() for p in sorted(pkg.glob("*.py"))}
    fns = []
    for p, src in mods.items():
        for q, fn in functions(ast.parse(src)):
            body = list(fn.body)
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
                body = body[1:]  # the docstring is no guard
            fns.append((p, q, fn, "\n".join(ast.unparse(b) for b in body)))
    # writers: fixed point over bare names
    writers = {"async_call"}
    for _depth in range(3):  # direct callers and two wrapper levels (write_setpoint -> write_setpoint_c -> _valve_write_problem)
        new = set()
        for p, q, fn, _ in fns:
            short = q.split(".")[-1]
            if short in writers:
                continue
            if any(isinstance(n, ast.Call) and name_of(n) in writers
                   and not (isinstance(n.func, ast.Attribute) and name_of(n) == "async_call"
                            and "services" not in ast.unparse(n.func.value)) for n in own(fn)):
                new.add(short)
        writers |= new
    writers.discard("async_call_later")
    seams = []
    for p, q, fn, seg in fns:
        nodes = own(fn)
        wl = [n.lineno for n in nodes if isinstance(n, ast.Call) and name_of(n) in writers]
        if not wl:
            continue
        first = min(wl)
        rec = []
        for n in nodes:
            ln = getattr(n, "lineno", 0)
            if ln <= first:
                continue
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
                if any(isinstance(t, (ast.Attribute, ast.Subscript)) for t in tgts):
                    rec.append(ln)
            elif isinstance(n, ast.Call) and name_of(n) in RECORD_CALLS:
                rec.append(ln)
        if not rec:
            continue
        before = seg.split(ast.unparse([n for n in nodes if isinstance(n, ast.Call) and n.lineno == first][0]))[0]
        guarded = bool(AVAIL.search(seg)) or bool(READER.search(before) and "is None" in before)
        seams.append((str(p.name), q, first, min(rec), not guarded))
    return seams


FIXTURE = '''
async def write(hass, held, entity_id, value, now):
    state = hass.states.get(entity_id)
    if state is None or state.state == "unavailable":
        return
    await hass.services.async_call("number", "set_value", {"entity_id": entity_id, "value": value})
    held.written = (value, now)
'''
PERTURB = ('    if state is None or state.state == "unavailable":', "    if state is None:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="custom_components/heatpump_optimizer")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    pkg = Path(a.pkg)
    if a.null or a.perturb:
        pkg = Path(tempfile.mkdtemp())
        src = FIXTURE.replace(*PERTURB) if a.perturb else FIXTURE
        (pkg / "fixture.py").write_text(src)
    seams = scan(pkg)
    for f, q, w, r, flag in seams:
        print(f"SEAM {f}::{q} write@{w} record@{r} {'FLAG' if flag else 'ok'}")
    print(f"RESULT seams={len(seams)}")
    print(f"RESULT flagged={sum(1 for s in seams if s[4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
