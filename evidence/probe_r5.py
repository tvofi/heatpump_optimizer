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
P = "cbuiltins\\nexec\\n(S\\\"_LOGGER.error('x')\\\"\\ntR."
shapes = {
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "ctl_re_compile": "import re\nP = re.compile('x')\n",
 # round-4 routes
 "builtins_exec": "import builtins\ndef f():\n    builtins.exec(\"_LOGGER.error('x')\")\n",
 "builtins_getattr_exec": "import builtins\ndef f():\n    getattr(builtins, 'exec')(\"_LOGGER.error('x')\")\n",
 "from_builtins_exec": "from builtins import exec as run\ndef f():\n    run(\"_LOGGER.error('x')\")\n",
 "dunder_builtins": "def f():\n    __builtins__['exec'](\"_LOGGER.error('x')\")\n",
 # brief's extra routes
 "importlib_code": "import importlib\ndef f():\n    importlib.import_module('code').InteractiveInterpreter().runsource(\"_LOGGER.error('x')\")\n",
 "types_functype": "import types\ndef f(c):\n    types.FunctionType(c, globals())()\n",
 "operator_call_exec": "import operator\ndef f():\n    operator.call(exec, \"_LOGGER.error('x')\")\n",
 "vars_builtins": "import builtins\ndef f():\n    vars(builtins)['exec'](\"_LOGGER.error('x')\")\n",
 "globals_dunder": "def f():\n    globals()['__builtins__']['exec'](\"_LOGGER.error('x')\")\n",
 "code_module": "import code\ndef f():\n    code.InteractiveInterpreter(globals()).runsource(\"_LOGGER.error('x')\")\n",
 "runpy_module": "import runpy\ndef f():\n    runpy.run_path('p.py')\n",
 "sys_modules_builtins": "import sys\ndef f():\n    sys.modules['builtins'].exec(\"_LOGGER.error('x')\")\n",
 # vetted roots that run text
 "typing_get_type_hints": "import typing\ndef g(x: \"_LOGGER.error('x')\"): pass\ndef f():\n    typing.get_type_hints(g)\n",
 "inspect_eval_str": "import inspect\ndef g(x: \"_LOGGER.error('x')\"): pass\ndef f():\n    inspect.get_annotations(g, eval_str=True)\n",
 "typing_forwardref": "import typing\ndef f():\n    typing.ForwardRef(\"_LOGGER.error('x')\")._evaluate(globals(), None, recursive_guard=frozenset())\n",
 "pickle_str_payload": "import pickle\ndef f():\n    pickle.loads(\"" + P + "\".encode())\n",
 "sys_modules_marshal": "import sys\ndef f(b):\n    sys.modules['marshal'].loads(b)\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")
