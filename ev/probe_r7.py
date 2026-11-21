# round-7 probe: prior round-6 shapes plus attacks on the delta's handler refusal
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
 "ctl_set_handler": "import asyncio\ndef f(loop):\n    loop.set_exception_handler(None)\n",
 "exc_handler": "import asyncio\ndef f():\n    asyncio.get_running_loop().call_exception_handler({'message': 'x'})\n",
 "exc_handler_default": "import asyncio\ndef f():\n    asyncio.get_running_loop().default_exception_handler({'message': 'x'})\n",
 "exc_handler_per_cycle": "class C:\n    async def _async_update(self):\n        self.hass.loop.call_exception_handler({'message': 'x'})\n",
 "handler_getattr_text": "def f(loop):\n    getattr(loop, 'call_exception_handler')({})\n",
 "handler_methodcaller": "import operator\ndef f(loop):\n    operator.methodcaller('default_exception_handler', {})(loop)\n",
 "handler_from_import": "from asyncio import BaseEventLoop as B\ndef f(loop):\n    B.call_exception_handler(loop, {})\n",
 "handler_bytes": "X = b'call_exception_handler'\n",
 "handler_fullwidth": "def f(loop):\n    loop.call_exception_ｈandler({})\n",
 "handler_keyword_dict": "def f(loop):\n    return dict(call_exception_handler=1)\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    c = sum(ns["_r10_unlatched_logs"](srcs).values())
    a = [b for _m, _l, b in ns["_r11_logger_aliases"](srcs)]
    print(f"{k:22s} barrier={c} alias={a}")
