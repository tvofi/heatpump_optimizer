# REVIEWER'S OWN probe: the review's moved-spelling rule over carry-201's
# from/control/brief fields. "_SP_STALE_RUN" in the arm is the same rule.
import json, re, sys
from pathlib import Path
sys.path.insert(0, "tests")
from layout import locate
_EXE = r"((?:[\w.-]+/)+[\w.-]+\.(?:py|mjs|js|sh))(?![\w.])"
CITE = re.compile(r"(?<![\w./-])" + _EXE)
d = json.loads(Path("dev/programme/carries/carry-201.json").read_text())
tot = 0
def walk(node, path=""):
    global tot
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("from", "control", "brief") and isinstance(v, str):
                for m in CITE.finditer(v):
                    w = m.group(1); p = locate(w)
                    if p != w and not Path(w).is_file() and Path(p).is_file():
                        tot += 1
                        print("  MOVED %-58s -> %s" % (w, p))
            else:
                walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for v in node: walk(v, path)
walk(d)
print("MOVED_SPELLINGS", tot)
