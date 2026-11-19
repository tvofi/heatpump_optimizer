import ast, sys, re
from collections import Counter
src = open(sys.argv[1]).read()
tree = ast.parse(src)
ns = {"ast": ast, "Counter": Counter, "re": re}
want = {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD"}
for n in tree.body:
    names = [n.name] if isinstance(n, (ast.FunctionDef,)) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & want:
        exec(compile(ast.Module([n], []), "e", "exec"), ns)
base = "import logging\n_LOGGER = logging.getLogger(__name__)\n"
shapes = {
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "builtins_exec": "import builtins\ndef f():\n    builtins.exec(\"_LOGGER.error('x')\")\n",
 "builtins_getattr_exec": "import builtins\ndef f():\n    getattr(builtins, 'exec')(\"_LOGGER.error('x')\")\n",
 "from_builtins_exec": "from builtins import exec as run\ndef f():\n    run(\"_LOGGER.error('x')\")\n",
 "dunder_builtins": "def f():\n    __builtins__['exec'](\"_LOGGER.error('x')\")\n",
 "vars_sibling": "from . import coordinator\ndef f():\n    vars(coordinator)['_LOGGER'].error('x')\n",
 "sibling_from_import_mod": "from .coordinator import logging as lg2\n",
 "ctl_re_compile": "import re\nP = re.compile('x')\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")

