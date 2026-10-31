"""Game hub_solve_writes by relocation: the solve's grid-cost push into _opt_config moves, statement
for statement, into a new coordinator method the scheduled cycle calls just before the solve. The
same in-place writes of the same live hub happen on every scheduled cycle; only where they sit moved.
The R9-EG-B1 round-1 review's probe (#1887 at 6b68bca0): a hub write in the pre-solve step
_refresh_model_corrections left hub_solve_writes and tests/arch_score_head.py unmoved."""
import ast, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
lines = src.splitlines(keepends=True)
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
fn = {n.name: n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def first_line(text: str, within) -> int:
    """The 0-based index of the one line of ``within`` (a function node) that reads ``text``."""
    hits = [i for i in range(within.lineno - 1, within.end_lineno) if lines[i].strip() == text]
    assert len(hits) == 1, (text, hits)
    return hits[0]


# The block from the tariff read to the export price, minus the one write that reads a solve local.
solve = fn["async_run_optimization"]
start = first_line("tariff = self._capacity_tariff()", solve)
stop = first_line("ctx._opt_config.pv_export_price = self._pv_export_price()", solve)
block = lines[start:stop + 1]
keep, moved, skip = [], [], False
for ln in block:
    if ln.strip().startswith("ctx._opt_config.baseline_load_kw = "):
        skip = True
    (keep if skip else moved).append(ln)
    if skip and ln.strip() == ")":
        skip = False
indent = len(block[0]) - len(block[0].lstrip())
helper = (["\n", "    def _push_grid_cost(self) -> None:\n",
           '        """The capacity tariff and export price into the live optimizer configuration."""\n',
           '        ctx = getattr(self, "_ctx", self)\n']
          + ["        " + ln[indent:] if ln.strip() else ln for ln in moved])
call = first_line("await self.async_run_optimization()", fn["_async_update_data"])
assert call < start, "the cycle's call precedes the solve's text"
pad = lines[call][:len(lines[call]) - len(lines[call].lstrip())]
# Bottom-up, so each edit leaves the earlier indices valid: the helper at the class end, the block, the call.
lines[cls.end_lineno:cls.end_lineno] = helper
lines[start:stop + 1] = keep
lines[call:call] = [f"{pad}self._push_grid_cost()\n"]
out = lines
p.write_text("".join(out))
ast.parse(p.read_text())
print("moved", sum(1 for ln in moved if ln.strip().startswith("ctx._opt_config.")), "hub writes")
