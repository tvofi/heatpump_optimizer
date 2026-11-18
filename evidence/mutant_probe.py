import ast, sys, re
from collections import Counter
tree = ast.parse(open(sys.argv[1]).read()); ns={"ast":ast,"Counter":Counter,"re":re}
for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name in ("_r10_unlatched_logs","_r11_logger_aliases"):
        exec(compile(ast.Module([n],[]),"e","exec"), ns)
lv = {"levels.py": "def exc(self):\n    _LOGGER.exception('x')\ndef crit(self):\n    _LOGGER.critical('x')\ndef warn_alias(self):\n    _LOGGER.warn('x')\n"}
print("barrier sites on planted exc/crit/warn:", dict(ns["_r10_unlatched_logs"](lv)))
pa = {"param.py": "_LOGGER = logging.getLogger(__name__)\ndef f(log):\n    log.warning('x')\ndef g():\n    f(_LOGGER)\n"}
print("alias refusals on planted param:", ns["_r11_logger_aliases"](pa))
