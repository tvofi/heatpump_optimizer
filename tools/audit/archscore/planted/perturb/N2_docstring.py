"""N2 (NULL): documentation only. Extend the docstring of the tree's longest
function (optimizer._optimize_with_dhw) by four lines, and give one
undocumented coordinator method (_async_save_accuracy) a four-line docstring.
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, PKG, read, write, find_method

def add_doc(rel, cls, name, text):
    s = read(rel)
    fn = find_method(s, cls, name)
    lines = s.splitlines(keepends=True)
    first = fn.body[0]
    indent = " " * first.col_offset
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        # insert before the closing quotes line of the existing docstring
        end = first.end_lineno
        lines.insert(end - 1, "".join(f"{indent}{t}\n" if t else "\n" for t in [""] + text))
    else:
        doc = f'{indent}"""{text[0]}\n' + "".join(f"{indent}{t}\n" if t else "\n" for t in text[1:]) + f'{indent}"""\n'
        lines.insert(first.lineno - 1, doc)
    write(rel, "".join(lines))

add_doc(f"{PKG}/optimizer.py", "HeatPumpOptimizer", "_optimize_with_dhw",
        ["Reading order: requirements, bounds, the solve, then the report;", "each",
         "stage is documented where it starts."])
add_doc(COORD, COORD_CLASS, "_async_save_accuracy",
        ["Persist the accuracy history.", "", "Called on the store cadence;",
         "the load side is ``_async_load_accuracy``."])
