"""Run only R10-BUFFER-STORE's checks out of tests/features.py (mutation probe).

All four zoning x valve `_grad_parity` cells (features.py's grad grid) and then
the store section, so a batch-only defect has a cell to fail in. The cell
labels are features.py's own; this probe adds no check of its own. Anchors are
found by their own text, not by line number, so a merge into features.py moves
them with the file.
"""
import sys
src = open("tests/features.py").read().splitlines(keepends=True)


def first(pred, start=0):
    for i in range(start, len(src)):
        if pred(src[i]):
            return i + 1
    raise SystemExit("probe: anchor not found")


def lines(a, b):
    return "".join(src[a - 1:b])


pre = lines(12, 105) + lines(142, 149)
grad_import = first(lambda l: l.startswith("from profiles import house as _grad_house"))
g_start = first(lambda l: l.startswith("from datetime import datetime as _dt_grad"), grad_import)
g_end = first(lambda l: l.startswith("import heatpump_optimizer.optimizer as _grad_optmod"), g_start) - 1
store_import = first(lambda l: l.startswith("from heatpump_optimizer.optimizer import (  # noqa: E402"),
                     first(lambda l: "# right to decline (measured: exactly that, at a 40 C start)." in l))
sec = first(lambda l: l.startswith('R.section("The valve hold schedule (item 29)")'), store_import)
g = {"__name__": "probe"}
exec(compile(pre, "features-pre", "exec"), g)
exec(compile(lines(grad_import, grad_import), "features-grad-import", "exec"), g)
exec(compile(lines(g_start, g_end) + "import heatpump_optimizer.optimizer as _grad_optmod\n",
             "features-grad", "exec"), g)
for cell in (
    '_grad_parity(False, label="single-zone")\n',
    '_grad_parity(True, label="two-zone")\n',
    '_grad_parity(True, valve="manual", label="two-zone with valve")\n',
    '_grad_parity(False, valve="manual", label="single-zone with valve")\n',
):
    exec(compile(cell, "cell", "exec"), g)
exec(compile("from heatpump_optimizer import mixing_valve as _mv\n" + lines(store_import, sec - 1),
             "features-store", "exec"), g)
sys.exit(1 if g["R"].failures else 0)
