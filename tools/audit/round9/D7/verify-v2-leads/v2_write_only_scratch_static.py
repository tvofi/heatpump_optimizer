"""verify-v2 (independent lens, D7-s3-72): purely static, whole-class AST census of the 5
ThermalModel._step_* scratch members -- an independent method from the finder's runtime property-
descriptor spy (which instruments __get__/__set__ and drives 4 real golden solves). This harness
never imports numpy or runs a solve; it only parses thermal_model.py.

Metric definition (mine): for each of the 5 members, over every method of class ThermalModel,
classify each method as a WRITER (contains `self.<name> = ...` or `self.<name> += ...`) and/or a
READER (contains `self.<name>` as a Load anywhere in its body). A member is "write_only" if it has
>=1 writer method and its only reader methods are themselves writers (i.e. no method that reads it
without also writing it -- a pure consumer). This mirrors the finder's runtime distinction
(self_reads inside a writer vs. consumer_reads from a non-writer) but is derived from source
structure alone, so it cannot be fooled by a solve path this harness's own driver happens not to
exercise, and it cannot be fooled by an attribute that a consumer reads only conditionally.

Run from cwd=/home/claude/ev2:
    python3 tools/audit/round9/D7/verify-v2-leads/v2_write_only_scratch_static.py
Expected (mine): write_only_members=4 of 5 (same 4 as the finder: _step_dhw_refused,
_step_dhw_floor_injected, _step_dhw_draw_kw, _step_wood_refused); _step_buffer_refused has a
non-writer reader (simulate_trajectory, which does `buffer_refused[i] = self._step_buffer_refused`).
Baseline / tree: evidence branch 96b89163.
"""
import ast
import os
import sys

ROOT = os.getcwd()
TM = os.path.join(ROOT, "custom_components/heatpump_optimizer/thermal_model.py")
if not os.path.isfile(TM):
    print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
    sys.exit(2)

src = open(TM).read()
tree = ast.parse(src)

ATTRS = ["_step_buffer_refused", "_step_dhw_refused", "_step_dhw_floor_injected",
         "_step_dhw_draw_kw", "_step_wood_refused"]

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ThermalModel":
        cls = node
        break
assert cls is not None, "ThermalModel class not found"

writers = {a: set() for a in ATTRS}
readers = {a: set() for a in ATTRS}

for meth in cls.body:
    if not isinstance(meth, ast.FunctionDef):
        continue
    for sub in ast.walk(meth):
        # writer: Assign/AugAssign whose target is self.<attr>
        targets = []
        if isinstance(sub, ast.Assign):
            targets = sub.targets
        elif isinstance(sub, ast.AugAssign):
            targets = [sub.target]
        for t in targets:
            if (isinstance(t, ast.Attribute) and t.attr in ATTRS
                    and isinstance(t.value, ast.Name) and t.value.id == "self"):
                writers[t.attr].add(meth.name)
        # reader: any Load-context self.<attr>
        if (isinstance(sub, ast.Attribute) and sub.attr in ATTRS
                and isinstance(sub.value, ast.Name) and sub.value.id == "self"
                and isinstance(sub.ctx, ast.Load)):
            readers[sub.attr].add(meth.name)

dead = 0
for a in ATTRS:
    consumer_methods = readers[a] - writers[a]
    is_write_only = bool(writers[a]) and not consumer_methods
    dead += is_write_only
    print(f"member {a:26s} writers={sorted(writers[a])} all_readers={sorted(readers[a])} "
          f"non_writer_readers={sorted(consumer_methods)} write_only={is_write_only}")

print(f"RESULT write_only_members={dead} of {len(ATTRS)} count")
print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
