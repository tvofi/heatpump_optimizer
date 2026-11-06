#!/usr/bin/env python3
"""Move each module-scope statement holding a `try` into a function called once.

    python3 tools/audit/seat/wrap_module_tries.py tests/features.py [--dry]

CodeQL's Python extractor is slow on a `try` executed at module scope (#3232:
one 364-line module-level try/finally took tests/features.py's extraction
from 817-1389 s to 2146-2211 s), and tests/entities.py refuses one in any test
script past its _GIANT_SCRIPT_LINES. This rewrites every top-level statement
whose body, outside a def, class or lambda, holds a `try` as

    def _module_block_<line>():
        global <every name the statement binds>
        <the statement, indented, string-literal interiors left as they were>
    _module_block_<line>()

so module state is what it was. It refuses an annotated name or a star import
in such a statement (neither is legal under `global`), and asserts each
wrapped statement's AST, and the order of everything else, unchanged.
"""
import ast, io, symtable, sys, tokenize

TRY = (ast.Try,) + ((ast.TryStar,) if hasattr(ast, "TryStar") else ())
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def holds_try(node):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, SCOPES):
            continue
        if isinstance(ch, TRY) or holds_try(ch):
            return True
    return False


def string_interior_lines(src):
    inner = set()
    kinds = {tokenize.STRING}
    for k in ("FSTRING_MIDDLE", "TSTRING_MIDDLE"):
        if hasattr(tokenize, k):
            kinds.add(getattr(tokenize, k))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in kinds and tok.end[0] > tok.start[0]:
            inner.update(range(tok.start[0] + 1, tok.end[0] + 1))
    return inner


def bound_names(block_src):
    fn = "def _w():\n" + "".join("    " + l if l.strip() else l for l in block_src.splitlines(True))
    top = symtable.symtable(fn, "<w>", "exec")
    (child,) = [c for c in top.get_children() if c.get_name() == "_w"]
    return sorted(s.get_name() for s in child.get_symbols() if s.is_local())


def main(path, dry=False):
    src = open(path).read()
    lines = src.splitlines(True)
    tree = ast.parse(src)
    inner = string_interior_lines(src)
    taken = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    targets = [n for n in tree.body if not isinstance(n, SCOPES) and (isinstance(n, TRY) or holds_try(n))]
    if not targets:
        print(f"{path}: no module-scope try")
        return
    out = []
    pos = 0  # 0-based line index consumed
    wrapped = []
    for n in targets:
        a, b = n.lineno - 1, n.end_lineno  # [a, b)
        # a statement must own its lines: nothing else on its first/last line
        seg = lines[a:b]
        for sub in ast.walk(n):
            if isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Name):
                raise SystemExit(f"{path}:{sub.lineno}: annotated name in a block to wrap")
            if isinstance(sub, ast.ImportFrom) and any(al.name == "*" for al in sub.names):
                raise SystemExit(f"{path}:{sub.lineno}: star import in a block to wrap")
        names = bound_names("".join(seg))
        name = f"_module_block_{n.lineno}"
        assert name not in taken, name
        out.extend(lines[pos:a])
        out.append(f"def {name}():\n")
        if names:
            out.append(f"    global {', '.join(names)}\n")
        for i, l in enumerate(seg, start=a + 1):
            out.append(l if (i in inner or not l.strip()) else "    " + l)
        out.append(f"{name}()\n")
        pos = b
        wrapped.append((n, name))
    out.extend(lines[pos:])
    new = "".join(out)
    # verify: every wrapped statement's AST is identical to the original
    nt = ast.parse(new)
    fns = {f.name: f for f in nt.body if isinstance(f, ast.FunctionDef)}
    for n, name in wrapped:
        body = fns[name].body
        if isinstance(body[0], ast.Global):
            body = body[1:]
        assert len(body) == 1 and ast.dump(body[0]) == ast.dump(n), (path, n.lineno)
    # verify: the rest of the module is unchanged in order
    rest_new = [ast.dump(s) for s in nt.body
                if not (isinstance(s, ast.FunctionDef) and s.name.startswith("_module_block_"))
                and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                         and isinstance(s.value.func, ast.Name) and s.value.func.id.startswith("_module_block_"))]
    rest_old = [ast.dump(s) for s in tree.body if not any(s is n for n, _ in wrapped)]
    assert rest_new == rest_old, path
    print(f"{path}: wrapped {len(wrapped)} statements, {sum(n.end_lineno - n.lineno + 1 for n, _ in wrapped)} lines; "
          f"+{len(new.splitlines()) - len(lines)} lines")
    if not dry:
        open(path, "w").write(new)


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
