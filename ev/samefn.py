# samefn.py <rev-a> <rev-b> <function>: whether tests/entities.py's top-level function is identical at both revs
import ast, subprocess, sys


def seg(rev, name):
    s = subprocess.run(["git", "show", f"{rev}:tests/entities.py"], capture_output=True, text=True).stdout
    for n in ast.parse(s).body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.get_source_segment(s, n)


a, b = seg(sys.argv[1], sys.argv[3]), seg(sys.argv[2], sys.argv[3])
print(sys.argv[3], "identical" if a is not None and a == b else "DIFFERS", sys.argv[1], sys.argv[2])
