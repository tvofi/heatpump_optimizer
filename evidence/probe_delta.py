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
 "sibling_module_logger": "from . import coordinator\ndef f():\n    coordinator._LOGGER.error('x')\n",
 "sibling_as": "from . import coordinator as c\ndef f():\n    c._LOGGER.warning('x')\n",
 "sys_modules_self": "import sys\ndef f():\n    sys.modules[__name__]._LOGGER.error('x')\n",
 "globals_lookup": "def f():\n    globals()['_LOGGER'].error('x')\n",
 "exec_string": "def f():\n    exec(\"_LOGGER.error('x')\")\n",
 "warnings_warn": "import warnings\ndef f():\n    warnings.warn('x')\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")
