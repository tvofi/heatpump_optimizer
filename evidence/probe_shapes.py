import ast, sys, re
from collections import Counter
src = open(sys.argv[1]).read()
tree = ast.parse(src)
ns = {"ast": ast, "Counter": Counter, "re": re}
want = {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD", "_r11_alias_verdict", "_R11_LOGGER_HANDOVERS"}
for n in tree.body:
    names = [n.name] if isinstance(n, (ast.FunctionDef,)) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & want:
        exec(compile(ast.Module([n], []), "e", "exec"), ns)
base = "import logging\n_LOGGER = logging.getLogger(__name__)\n"
shapes = {
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "ctl_info": "def f():\n    _LOGGER.info('x')\n",
 "log_kw_level": "def f():\n    _LOGGER.log(level=logging.ERROR, msg='x')\n",
 "log_star": "def f(a):\n    _LOGGER.log(*a)\n",
 "private_log": "def f():\n    _LOGGER._log(logging.ERROR, 'x', ())\n",
 "handle_record": "def f():\n    _LOGGER.handle(logging.makeLogRecord({'levelno': 40}))\n",
 "module_assign_alias": "def f():\n    lg = logging\n    lg.warning('x')\n",
 "getattr_level": "def f():\n    getattr(_LOGGER, 'warning')('x')\n",
 "getattr_root": "def f():\n    getattr(logging, 'warning')('x')\n",
 "importlib": "import importlib\ndef f():\n    importlib.import_module('logging').warning('x')\n",
 "dunder_import": "def f():\n    __import__('logging').warning('x')\n",
 "self_attr_store": "class C:\n    def __init__(self):\n        self.log = _LOGGER\n    def f(self):\n        self.log.warning('x')\n",
 "nested_class_logger": "class C:\n    _LOGGER = logging.getLogger('c')\n",
 "func_local_rebind": "def f():\n    _LOGGER = logging.getLogger('y')\n    _LOGGER.warning('x')\n",
 "walrus_alias": "def f():\n    (lg := logging).warning('x')\n",
 "logging_log_root": "def f():\n    logging.log(40, 'x')\n",
 "lambda_wrap": "W = lambda m: _LOGGER.warning(m)\ndef f():\n    W('x')\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")
print("-- controls: the same call in the spelling the check reads")
for k, s in {"log_pos_level": "def f():\n    _LOGGER.log(logging.ERROR, 'x')\n",
             "import_as_alias": "import logging as lg\ndef f():\n    lg.warning('x')\n",
             "root_direct": "def f():\n    logging.warning('x')\n"}.items():
    srcs = {"m.py": base + s}
    print(f"{k:22s} barrier={sum(ns['_r10_unlatched_logs'](srcs).values())} alias={[b for _m,_l,b in ns['_r11_logger_aliases'](srcs)]}")
