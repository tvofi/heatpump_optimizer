"""R10-LIVESTATE (#2232) sibling census, the design note's instrument 2: a context
held in a local and read for ``_current_state`` after an await in the same async
function. Once the live state is published by rebinding the context, such a read
sees the state as of the binding, not the published one (invariant I1's reader side).

Rule: in every ``async def`` of the package, a local Name assigned from an
expression mentioning ``_ctx`` (``ctx = getattr(self, "_ctx", self)``,
``_ctx_of(self)``), then ``<that name>._current_state`` read on a line after any
``await`` that follows the assignment. Syntactic: a read re-bound through
``_ctx_of(self)`` after the await is not counted, which is the fix's shape.
Metric: held_ctx_reads_after_await. Null: --plant adds one such read to a copy of
coordinator.py's ``_async_drive_pumps`` source in memory and must add 1.
Expected at merge base fd7e289d0: 9 (_async_drive_pumps 1, _update_current_state 8).
Expected at the R10-LIVESTATE head: 0; with --plant 1.

    python3 dev/audit/harnesses/r10_livestate_held_ctx_reads.py [--plant]
"""
import ast
import pathlib
import sys

PKG = pathlib.Path("custom_components/heatpump_optimizer")
PLANT = "--plant" in sys.argv


def count(name, text):
    found = []
    for fn in ast.walk(ast.parse(text)):
        if not isinstance(fn, ast.AsyncFunctionDef):
            continue
        bound = {a.targets[0].id: a.lineno for a in ast.walk(fn) if isinstance(a, ast.Assign)
                 and isinstance(a.targets[0], ast.Name) and "_ctx" in ast.unparse(a.value)}
        awaits = [a.end_lineno for a in ast.walk(fn) if isinstance(a, ast.Await)]
        for r in ast.walk(fn):
            if (isinstance(r, ast.Attribute) and r.attr == "_current_state"
                    and isinstance(r.value, ast.Name) and r.value.id in bound
                    and any(bound[r.value.id] < x < r.lineno for x in awaits)):
                found.append(f"{name}:{r.lineno} {fn.name}")
    return found


total = []
for f in sorted(PKG.glob("*.py")):
    text = f.read_text()
    if PLANT and f.name == "coordinator.py":
        anchor = "    async def _async_drive_pumps(self) -> None:\n"
        assert anchor in text, "plant anchor moved"
        text = text.replace(anchor, anchor + (
            "        _plant = getattr(self, '_ctx', self)\n"
            "        await self._async_planted()\n"
            "        _plant._current_state\n"), 1)
    total += count(f.name, text)
for line in total:
    print(line)
print(f"RESULT held_ctx_reads_after_await={len(total)} count")
