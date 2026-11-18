"""Game dead_members + public_unused: a module-level keep-alive in diagnostics.py that
imports the unused public constant and reads every dead member's name on an untyped receiver.
Nothing calls the lambda; the dead members stay dead and the unused name stays unused."""
import sys
from rt_lib import pkg, metric, structure
root = sys.argv[1]
S = structure(root)
dead_members, _kept = S.dead_members(S.Package(S.module_trees()))
unused = metric("public_surface", root)["details"]["unused_names"]
attrs = sorted({name for _f, _c, name, _l in dead_members} | {u.rsplit(".", 1)[-1] for u in unused if u.count(".") == 2})
tops = sorted(u for u in unused if u.count(".") == 1)
p = pkg(root) / "diagnostics.py"
src = p.read_text()
imports = "".join(f"from .{u.split('.')[0]} import {u.split('.')[1]}  # noqa: F401\n" for u in tops)
keep = ("\n# Members reached only through dynamic dispatch.\n_KEEP_ALIVE = (\n"
        + "".join(f"    {u.split('.')[1]},\n" for u in tops)
        + "    lambda o: (" + ", ".join(f"o.{a}" for a in attrs) + "),\n)\n")
lines = src.splitlines(keepends=True)
last_import = max(i for i, ln in enumerate(lines) if ln.startswith(("from ", "import ")))
# step past a parenthesised import block
while lines[last_import].rstrip().endswith("(") or (last_import + 1 < len(lines) and lines[last_import + 1].startswith("    ")):
    last_import += 1
    if lines[last_import].startswith(")"):
        break
lines.insert(last_import + 1, imports + keep)
p.write_text("".join(lines))
print("attrs", attrs, "tops", tops)
