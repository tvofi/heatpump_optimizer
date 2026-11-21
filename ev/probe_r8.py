# round-8 probe: shapes at the narrowed claim's edges, through the head's two functions (exec'd alone)
import ast, sys, re, subprocess, tempfile
from collections import Counter
from pathlib import Path
tree = ast.parse(open(sys.argv[1]).read())
ns = {"ast": ast, "Counter": Counter, "re": re, "subprocess": subprocess, "tempfile": tempfile, "Path": Path}
for n in tree.body:
    names = [n.name] if isinstance(n, ast.FunctionDef) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & {"_r10_unlatched_logs", "_r11_logger_aliases", "_R10_LATCH_WORD"}:
        exec(compile(ast.Module([n], []), "e", "exec"), ns)
base = "import logging\n_LOGGER = logging.getLogger(__name__)\n"
shapes = {
 # controls
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "ctl_debug": "def f():\n    _LOGGER.debug('x')\n",
 # claim set: package logger bindings and calls spelled in text
 "ann_top_binding": "_LOG2: logging.Logger = logging.getLogger('x')\n",
 "class_binding": "class C:\n    _LOGGER = logging.getLogger('x')\n",
 "default_arg": "def f(log=_LOGGER):\n    log.error('x')\n",
 "decorator": "@_LOGGER.error\ndef f():\n    pass\n",
 "annotation": "def f(x: logging.Logger):\n    pass\n",
 "match_cls": "def f(x):\n    match x:\n        case logging.Logger():\n            pass\n",
 "attr_store": "_LOGGER.disabled = True\n",
 "global_rebind": "def f():\n    global _LOGGER\n    _LOGGER = logging.getLogger('y')\n",
 "type_of": "def f():\n    type(_LOGGER).error(_LOGGER, 'x')\n",
 "log_float_level": "def f():\n    _LOGGER.log(10.0, 'x')\n",
 "log_bool_level": "def f():\n    _LOGGER.log(True, 'x')\n",
 "log_from_import_level": "from logging import DEBUG\ndef f():\n    _LOGGER.log(DEBUG, 'x')\n",
 # residue category 2: a dependency's own logger or record, named by no logger word
 "dep_logger_log": "from urllib3.connectionpool import log\ndef f():\n    log.error('x')\n",
 "dep_logger_attr": "import urllib3.connectionpool as cp\ndef f():\n    cp.log.error('x')\n",
 "ha_report_usage": "from homeassistant.helpers.frame import report_usage\ndef f():\n    report_usage('x', level=logging.ERROR)\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    print(f"{k:24s} barrier={sum(ns['_r10_unlatched_logs'](srcs).values())} alias={[b for _m,_l,b in ns['_r11_logger_aliases'](srcs)]}")
