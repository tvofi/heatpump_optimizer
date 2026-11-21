import ast, sys, re, subprocess, tempfile
from collections import Counter
from pathlib import Path
src = open(sys.argv[1]).read()
tree = ast.parse(src)
ns = {"ast": ast, "Counter": Counter, "re": re, "subprocess": subprocess, "tempfile": tempfile, "Path": Path}
want = {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD"}
for n in tree.body:
    names = [n.name] if isinstance(n, (ast.FunctionDef,)) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & want:
        exec(compile(ast.Module([n], []), "e", "exec"), ns)
base = "import logging\n_LOGGER = logging.getLogger(__name__)\n"
shapes = {
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "ctl_re_compile": "import re\nP = re.compile('x')\n",
 "fullwidth_name_call": "def f():\n    _ＬＯＧＧＥＲ.error('x')\n",
 "fullwidth_method": "def f():\n    _LOGGER.ｅrror('x')\n",
 "exc_handler": "import asyncio\ndef f():\n    asyncio.get_running_loop().call_exception_handler({'message': 'x'})\n",
 "utf16_file_arm": None,
}
for k, s in shapes.items():
    if s is None: continue
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")
f = {"s.txt": "_LOGGER.error(1)".encode("utf-16")}
print("utf16_file            alias=", [b for _m,_l,b in ns["_r11_logger_aliases"]({}, f)])
