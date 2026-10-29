import ast, re, sys, yaml as _yaml
from pathlib import Path
src = Path("tests/entities.py").read_text()
tree = ast.parse(src)
want = {"_EX_SHELLS","_EX_SAFE","_EX_TEST_HEAD","_EX_READER","_ex_run_blocks","_ex_hazards","_ex_scan"}
body = [n for n in tree.body if (isinstance(n,(ast.FunctionDef,)) and n.name in want) or
        (isinstance(n,ast.Assign) and any(getattr(t,"id",None) in want for t in n.targets))]
g = {"re":re,"Path":Path,"_yaml":_yaml}
exec(compile(ast.Module(body=body,type_ignores=[]),"x","exec"), g)
if sys.argv[1] == "scan":
    for r in sys.argv[2:]:
        b,n,h = g["_ex_scan"](Path(r)); print(r.split("/")[-1], (b,n,len(h)), h)
else:
    cases = {
     "and-list last fails": "prep && cmd --gate\nrc=$?\n",
     "or-list rhs fails": "cmd1 || cmd2\nrc=$?\n",
     "brace form": "cmd --gate\nrc=${?}\n",
     "local masks": "f() { local x=$(cmd); rc=$?; }\n",
     "pipeline": "cmd | tee log\nrc=$?\n",
     "arith": "cmd\nrc=$(( $? + 0 ))\n",
     "export": "cmd\nexport RC=$?\n",
     "cmdsub assign": "out=$(cmd)\nrc=$?\n",
     "semicolon in string": "echo 'a;b'\ncmd\nrc=$?\n",
     "set -e later": "set +e\ncmd\nset -e\nother\nrc=$?\n",
     "bash -e inline": "set -euo pipefail\ncmd\nrc=$?\n",
     "if not test": "cmd\nif (( $? != 0 )); then :; fi\n",
     "[[ test ]] var": "cmd\n[[ $? -eq 0 ]] || exit 1\n",
    }
    for k,t in cases.items(): print(f"{k:24} hits={len(g['_ex_hazards'](t)[1])}")
