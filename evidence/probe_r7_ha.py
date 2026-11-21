# round-7 probe: Home Assistant helpers whose effect is a log record, through the head's barrier
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
 "ctl_warning": "def f():\n    _LOGGER.warning('x')\n",
 "ha_report_usage": "from homeassistant.helpers.frame import report_usage\ndef f():\n    report_usage('x', level=logging.ERROR)\n",
 "ha_report_usage_per_cycle": "from homeassistant.helpers import frame\nclass C:\n    async def _async_update(self):\n        frame.report_usage('uses x')\n",
}
for k, s in shapes.items():
    srcs = {"m.py": base + s}
    print(f"{k:26s} barrier={sum(ns['_r10_unlatched_logs'](srcs).values())} alias={[b for _m,_l,b in ns['_r11_logger_aliases'](srcs)]}")
