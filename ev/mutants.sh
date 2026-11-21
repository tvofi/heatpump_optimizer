#!/bin/bash
# mutants.sh: each mutant edits the fix's _r11_logger_aliases predicate in a copy of
# tests/entities.py at a7fcb6bd and runs the reach block (reach.py); a kill is a FAIL line.
cd $HOME/hpo-orch/r10s6/r11/fix3729-r6 || exit 1
E=$HOME/hpo-seats/r11/fix3729-r6/ev
PY=$HOME/hpo-orch/r10s6/venv-ci/bin/python
git show a7fcb6bdfc:tests/entities.py > "$E/ent-a7fcb6bd.py"; F=$E/ent-a7fcb6bd.py
mut() {  # name, python expression rewriting s
  "$PY" - "$F" "$E/mut-$1.py" "$2" <<'EOF'
import sys
s = open(sys.argv[1]).read(); old = s
exec(sys.argv[3])
assert s != old, "mutation matched nothing"
open(sys.argv[2], "w").write(s)
EOF
  r=$("$PY" "$E/reach.py" "$E/mut-$1.py" 2>&1 | grep -E "^(FAIL|Traceback)" | cut -c1-90)
  echo "$1: ${r:-SURVIVED}"
}
mut M1-constant-arm 's = s.replace("            if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):\n                if text_names_one(node.value):", "            if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):\n                if False:")'
mut M2-ast-front-end 's = s.replace("for n in ast.walk(ast.parse(value)):", "for n in ():")'
mut M3-pickle-front-end 's = s.replace("for _op, arg, _pos in pickletools.genops(", "for _op, arg, _pos in iter(()) if 1 else pickletools.genops(")'
mut M4-files-arm 's = s.replace("        if text_names_one(data):", "        if False:")'
mut M5-ident-arm 's = s.replace("                for s in idents(node):\n                    if names_one.search(s):", "                for s in idents(node):\n                    if False:")'
mut M6-raw-text 's = s.replace("        if names_one.search(value if isinstance(value, str) else value.decode(\"latin-1\")):\n            return True", "        if False:\n            return True")'
mut M7-inner-idents 's = s.replace("inner += [s for s in idents(n) if names_one.search(s)]", "pass")'
mut M8-inner-constants 's = s.replace("                    inner.append(n.value)", "                    pass")'
mut M9-regex-narrowed 's = s.replace("names_one = re.compile(r\"LOGGER|[Ll]ogger|logging|warnings\")", "names_one = re.compile(r\"LOGGER\")")'
mut M10-allowance-dropped 's = s.replace("    (\"log_latch.py\", \"text sha256:82178ac44c5d08e8\"): 1,", "")'
mut M11-round5-function "import ast
def seg(t):
    for n in ast.parse(t).body:
        if isinstance(n, ast.FunctionDef) and n.name == '_r11_logger_aliases':
            return ast.get_source_segment(t, n)
r5 = seg(open('$E/ent-148254e8.py').read()).replace('def _r11_logger_aliases(sources):', 'def _r11_logger_aliases(sources, files=None):')
s = s.replace(seg(s), r5)"
mut M12-pyc-skipped 's = s.replace("if p and not p.endswith(\".py\") and", "if p and not p.endswith((\".py\", \".pyc\")) and")'
mut M13-pycache-skipped 's = s.replace("if p and not p.endswith(\".py\") and", "if p and \"__pycache__\" not in p and not p.endswith(\".py\") and")'
mut M14-untracked-read 's = s.replace("    return {p: (pkg / p).read_bytes() for p in sorted(tracked)\n", "    tracked = [q.relative_to(pkg).as_posix() for q in pkg.rglob(\"*\")]\n    return {p: (pkg / p).read_bytes() for p in sorted(tracked)\n")'
